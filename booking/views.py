import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Table, Booking, Meal
from datetime import datetime
from django.utils import timezone
import io
import base64
from staff.forms import ReportForm, TableForm
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

@login_required
def index(request):
    upcoming_bookings = Booking.objects.upcoming_for_user(request.user)
    if request.method == 'POST':
        bookingform = BookingForm(request.POST)
        if bookingform.is_valid():
            booking = bookingform.save(commit=False)
            booking.user = request.user
            booking.save()
    else:
        bookingform = BookingForm()

    context = {
        'upcoming_bookings': upcoming_bookings,
        'bookingform': bookingform
    }
    return render(request, "index.html", context)


@login_required
def BookingListView(request):
    upcoming_bookings = Booking.objects.upcoming_for_user(request.user)
    past_bookings = Booking.objects.past_for_user(request.user)

    context = {
        "title": "Booking List",
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        "current_date": timezone.now().date(),
    }
    return render(request, "book/booking_list.html", context)

@login_required
def BookingDetailView(request, pk):
    booking = get_object_or_404(Booking.objects.with_relations(), pk=pk)
    context = {
        "title": "Booking Details",
        "booking": booking
    }
    return render(request, "book/booking_detail.html", context)

@login_required
def BookingUpdateView(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect("booking_list")
    else:
        form = BookingForm(instance=booking)
    context = {
        "title": "Update Booking",
        "form": form
    }
    return render(request, "book/booking_update.html", context)

@login_required
def BookingDeleteView(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == "POST":
        try:
            booking.delete()
            return redirect("booking_list")
        except Exception as e:
            context = {
                "title": "Delete Booking",
                "booking": booking,
                "error": str(e)
            }
            return render(request, "book/booking_delete.html", context)
    context = {
        "title": "Delete Booking",
        "booking": booking
    }
    return render(request, "book/booking_delete.html", context)


def Tablesview(request):
    tables = Table.objects.all()
    context ={
        'tables': tables,
    }
    return render(request, 'tables/table_list.html', context)

def Dishesview(request):
    dishes = Meal.objects.all()
    context = {
        'dishes' : dishes,
    }
    return render (request, 'dishes/dishes.html', context)

@login_required
def reports_view(request):
    report_html = None
    report_type = None

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            bookings = Booking.objects.get_by_report_type(report_type)
            report_html = render_to_string(f'reports/{report_type}_report.html', {'bookings': bookings})
    else:
        form = ReportForm()

    return render(request, 'reports/reports.html', {
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

@login_required
def download_report(request, report_type):
    bookings = Booking.objects.get_by_report_type(report_type)
    html_string = render_to_string(f'reports/{report_type}_report.html', {'bookings': bookings})
    return generate_pdf_response(html_string, f'{report_type}_report.pdf')
