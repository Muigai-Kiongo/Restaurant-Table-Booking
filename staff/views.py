from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from booking.forms import BookingForm
from booking.models import Table, Booking, Meal
from django.utils import timezone
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import numpy as np
from django.http import HttpResponse
from collections import defaultdict
from datetime import datetime, timedelta
import io
import base64
from .forms import ReportForm, TableForm
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib import messages

@staff_member_required 
def staff_view(request):
    current_date = timezone.now().date()
    current_time = timezone.now().time()

    bookings = Booking.objects.with_relations()

    past_date = current_date - timedelta(days=1 )
    today_bookings = bookings.filter(date=current_date).order_by('time')
    tomorrow_date = current_date + timedelta(days=1)
    tomorrow_bookings = bookings.filter(date=tomorrow_date).order_by('time')
    other_bookings = bookings.exclude(date__in=[past_date, current_date, tomorrow_date]).order_by('date', 'time')

    context = {
        'today_bookings': today_bookings,
        'tomorrow_bookings': tomorrow_bookings,
        'other_bookings': other_bookings,
        'user': request.user,
    }

    return render(request, 'staff.html', context)

@staff_member_required
def StaffTablesview(request):
    tables = Table.objects.all()
    context ={
        'tables': tables,
    }
    return render(request, 'staff/tables/tables.html', context)

@staff_member_required
def create_table(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tables')
    else:
        form = TableForm()
    
    context = {
        'form': form,
        'title': 'Create Table',
    }
    return render(request, 'staff/tables/create_table.html', context)

@staff_member_required
def update_table(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('tables')
    else:
        form = TableForm(instance=table)

    context = {
        'form': form,
        'title': 'Update Table',
    }
    return render(request, 'staff/tables/update_table.html', context)

@staff_member_required
def StaffDishesview(request):
    dishes = Meal.objects.all()
    context ={
        'dishes' : dishes,
    }
    return render(request, 'staff/dishes.html', context)


@staff_member_required
def StaffBookview(request, pk):
    booking = get_object_or_404(Booking.objects.with_relations(), pk=pk)
    dishes = Meal.objects.all()

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect("booking_list")
    elif 'delete' in request.POST:
        booking.delete()
        messages.success(request, 'Booking deleted successfully.')
        return redirect('staff_home') 
    else:
        form = BookingForm(instance=booking)
    
    context = {
        'booking': booking,
        'dishes': dishes,
        'user': request.user,
        "form": form
    }
    return render(request, 'staff/book_detail.html', context)

@staff_member_required
def Staffupdate_book(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect("booking_list")
    else:
        form = BookingForm(instance=booking)
    
    return render(request, 'booking_detail.html', {'booking': booking, 'user': request.user})

@staff_member_required
def Staffcancel_book(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking canceled successfully!')
        return redirect('staff_home') 
    
    return render(request, 'booking_detail.html', {'booking': booking, 'user': request.user})

@staff_member_required
def booking_statistics(request):
    now = timezone.now()
    week_start = now.date() - timezone.timedelta(days=7)
    week_bookings = Booking.objects.filter(date__gte=week_start)

    month_start = now.date().replace(day=1)
    month_bookings = Booking.objects.filter(date__gte=month_start)

    daily_count = defaultdict(int)
    hourly_count = defaultdict(int)

    for booking in week_bookings:
        daily_count[booking.date] += 1
        hourly_count[booking.time.hour] += 1

    busy_days = sorted(daily_count.items())
    peak_hours = sorted(hourly_count.items())

    days, counts = zip(*busy_days) if busy_days else ([], [])
    hours, hour_counts = zip(*peak_hours) if peak_hours else ([], [])

    busy_days_image = create_busy_days_graph(days, counts)
    peak_hours_image = create_peak_hours_graph(hours, hour_counts)

    monthly_count = defaultdict(int)
    for booking in month_bookings:
        monthly_count[booking.date.strftime('%Y-%m')] += 1

    monthly_data = sorted(monthly_count.items())
    months, monthly_counts = zip(*monthly_data) if monthly_data else ([], [])

    monthly_insights_image = create_monthly_insights_graph(months, monthly_counts)

    context = {
        'busy_days_image': busy_days_image,
        'peak_hours_image': peak_hours_image,
        'monthly_insights_image': monthly_insights_image,
    }

    return render(request, 'staff/booking_statistics.html', context)

def create_busy_days_graph(days, counts):
    plt.figure(figsize=(10, 5))
    plt.bar(days, counts, color='teal')
    plt.title('Busy Days (Last Week)')
    plt.xlabel('Days')
    plt.ylabel('Number of Bookings')
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def create_peak_hours_graph(hours, hour_counts):
    plt.figure(figsize=(10, 5))
    plt.plot(hours, hour_counts, marker='o', color='orange')
    plt.title('Peak Hours (Last Week)')
    plt.xlabel('Hours')
    plt.ylabel('Number of Bookings')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def create_monthly_insights_graph(months, monthly_counts):
    plt.figure(figsize=(10, 5))
    plt.bar(months, monthly_counts, color='blue')
    plt.title('Monthly Insights')
    plt.xlabel('Months')
    plt.ylabel('Number of Bookings')
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@staff_member_required
def reports_view(request):
    report_html = None
    report_type = None

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            bookings = Booking.objects.get_by_report_type(report_type)
            report_html = render_to_string(f'staff/reports/{report_type}_report.html', {'bookings': bookings})
    else:
        form = ReportForm()

    return render(request, 'staff/reports.html', {
        'form': form,
        'report_html': report_html,
        'report_type': report_type,
    })

def generate_pdf_response(html_string, filename):
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@staff_member_required
def download_report(request, report_type):
    bookings = Booking.objects.get_by_report_type(report_type)
    html_string = render_to_string(f'staff/reports/{report_type}_report.html', {'bookings': bookings})
    return generate_pdf_response(html_string, f'{report_type}_report.pdf')
