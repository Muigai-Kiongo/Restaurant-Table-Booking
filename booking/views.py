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





current_date = datetime.now().date()
tables = Table.objects.all()
dishes = Meal.objects.all()

@login_required
def index(request):
    upcoming_bookings = Booking.objects.filter(user=request.user ,date=current_date)
    if request.method == 'POST':
        bookingform = BookingForm(request.POST)
        if bookingform.is_valid():
            booking = bookingform.save(commit=False)
            booking.user = request.user
            booking.save()  # Save the booking to get the ID


    else:
        bookingform = BookingForm()

    context = {
        'upcoming_bookings': upcoming_bookings,
        'bookingform': bookingform
    }
    return render(request, "index.html", context)


def BookingListView(request):
    current_datetime = timezone.now()  # Get the current date and time
    bookings = Booking.objects.filter(user=request.user).order_by('date', 'time')  # Order by date and time

    past_bookings = []
    upcoming_bookings = []

    for booking in bookings:
        if booking.date < current_datetime.date() or (booking.date == current_datetime.date() and booking.time < current_datetime.time()):
            past_bookings.append(booking)
        else:
            upcoming_bookings.append(booking)

    context = {
        "title": "Booking List",
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        "current_date": current_datetime.date(),
    }
    return render(request, "book/booking_list.html", context)

def BookingDetailView(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    context = {
        "title": "Booking Details",
        "booking": booking
    }
    return render(request, "book/booking_detail.html", context)

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
    return render(request, "book/booking_delete.htm", context)


def Tablesview(request):
    context ={
        'tables': tables,
    }

    return render(request, 'tables/table_list.html', context)

def Dishesview(request):
    context = {
        'dishes' : dishes,
    }

    return render (request, 'dishes/dishes.html', context)



