from django import forms
from django.utils import timezone
from .models import Booking, Meal, Table
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from datetime import time  # Import the time class from datetime module

class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ('user', 'date', 'time', 'table', 'meal_option', 'payment_method', 'phone_number')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'table': forms.Select(attrs={'class': 'form-control'}),
            'meal_option': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select', 'id': 'paymentMethodSelect'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 254712345678', 'id': 'phoneNumberInput'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].required = False  
        self.fields['meal_option'].required = False
        self.fields['phone_number'].required = False

        # Add min attribute for HTML5 date validation
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()
        
        # Add IDs for JavaScript targeting
        self.fields['date'].widget.attrs['id'] = 'dateInput'
        self.fields['time'].widget.attrs['id'] = 'timeInput'
        self.fields['table'].widget.attrs['id'] = 'tableSelect'

        # Filter available tables based on date and time (if date and time are provided)
        if 'date' in self.data and 'time' in self.data:
            try:
                date = self.data.get('date')
                time = self.data.get('time')
                self.fields['table'].queryset = self.get_available_tables(date, time)
            except (ValueError, TypeError):
                pass  # Handle the case where date/time is not valid

    def get_available_tables(self, date, time):
        # Filter tables that are not booked for the given date and time
        bookings = Booking.objects.filter(date=date, time=time).values_list('table_id', flat=True)
        return Table.objects.exclude(id__in=bookings)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise ValidationError(_('Booking date cannot be in the past.'))
        return date

    def clean_time(self):
        time_value = self.cleaned_data.get('time')
        if time_value < time(8, 0) or time_value > time(23, 0):
            raise ValidationError(_('Booking time must be between 08:00 and 23:00.'))
        if time_value < timezone.now().time() and self.cleaned_data.get('date') == timezone.now().date():
            raise ValidationError(_('Booking time cannot be in the past.'))
        return time_value

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_value = cleaned_data.get('time')
        table = cleaned_data.get('table')
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number')

        if payment_method == 'M-Pesa':
            if not phone_number:
                self.add_error('phone_number', _('Phone number is required for M-Pesa payment.'))
            else:
                # Basic validation for Safaricom format (2547XXXXXXXX or 07XXXXXXXX)
                clean_phone = phone_number.replace('+', '').replace(' ', '')
                if not (clean_phone.startswith('254') or clean_phone.startswith('07') or clean_phone.startswith('01')):
                    self.add_error('phone_number', _('Please enter a valid Kenyan mobile number for M-Pesa.'))

        # Check if the table is already booked
        if date and time_value and table:
            # Check for double booking within one hour
            end_time = (timezone.datetime.combine(date, time_value) + timezone.timedelta(hours=1)).time()
            if Booking.objects.filter(date=date, time__gte=time_value, time__lt=end_time, table=table).exists():
                raise ValidationError(_('The selected table is already booked for this date and time.'))

        return cleaned_data

    def save(self, commit=True):
        # Clear the form after submission
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.cleaned_data.clear()  # Clear the form data after saving
        return instance