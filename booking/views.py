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
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .mpesa import initiate_stk_push

@login_required
def index(request):
    upcoming_bookings = Booking.objects.upcoming_for_user(request.user)
    mpesa_message = None

    if request.method == 'POST':
        bookingform = BookingForm(request.POST)
        if bookingform.is_valid():
            booking = bookingform.save(commit=False)
            booking.user = request.user
            booking.save()
            
            if booking.payment_method == 'M-Pesa':
                amount = booking.meal_option.price if booking.meal_option else 1.00 # Flat 1 KES for testing if no meal
                response = initiate_stk_push(
                    phone_number=booking.phone_number,
                    amount=amount,
                    account_reference=f"BK-{booking.id}"
                )
                if "error" in response:
                    mpesa_message = f"Failed to initiate M-Pesa payment: {response['error']}"
                else:
                    mpesa_message = "M-Pesa payment initiated. Please check your phone to enter your PIN."
            else:
                # Redirect to avoid form resubmission
                return redirect('home')
    else:
        bookingform = BookingForm()

    context = {
        'upcoming_bookings': upcoming_bookings,
        'bookingform': bookingform,
        'mpesa_message': mpesa_message
    }
    return render(request, "index.html", context)

@csrf_exempt
def mpesa_callback(request):
    """
    Handle the M-Pesa STK Push callback.
    Expected JSON payload from Daraja.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            body = data.get('Body', {}).get('stkCallback', {})
            result_code = body.get('ResultCode')
            
            # Extract metadata (Receipt, Amount, Phone, etc)
            callback_metadata = body.get('CallbackMetadata', {}).get('Item', [])
            receipt_number = None
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    receipt_number = item.get('Value')

            # We need to find the booking. Daraja doesn't echo AccountReference back in the callback directly,
            # so usually developers pass the Booking ID in the CallBackURL (e.g. /mpesa/callback/<booking_id>/)
            # Alternatively, if we just want to mock it for now since it's a test environment:
            
            # For a proper production system, the CheckoutRequestID is saved in DB and mapped to the booking.
            # But for simplicity, we'll just log it.
            print(f"M-Pesa Callback Received: ResultCode {result_code}, Receipt {receipt_number}")
            
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        except json.JSONDecodeError:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON"})
            
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Method Not Allowed"})


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

@login_required
def get_available_tables_api(request):
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    
    if not date_str or not time_str:
        return JsonResponse({'tables': []})
        
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Calculate 1-hour window to prevent double booking overlaps
        from datetime import timedelta
        end_time = (datetime.combine(date_obj, time_obj) + timedelta(hours=1)).time()
        
        # Find tables already booked in this window
        booked_table_ids = Booking.objects.filter(
            date=date_obj, 
            time__gte=time_obj, 
            time__lt=end_time
        ).values_list('table_id', flat=True)
        
        available_tables = Table.objects.exclude(id__in=booked_table_ids).filter(is_available=True)
        
        tables_data = [{'id': t.id, 'text': str(t)} for t in available_tables]
        return JsonResponse({'tables': tables_data})
    except ValueError:
        return JsonResponse({'tables': []})
