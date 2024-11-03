from django import forms
from django.utils import timezone
from .models import Booking, Meal, Table

class BookingForm(forms.ModelForm):


    class Meta:
        model = Booking
        fields = ('user', 'date', 'time', 'table', 'meal_option')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'table': forms.Select(attrs={'class': 'form-control'}),
            'meal_option': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].required = False  
        self.fields['meal_option'].required = False

        # Optional: Filter available tables based on date and time
        # TODO: Implement filtering logic here

    def clean_date(self):
        date = self.cleaned_data.get('date')
        # TODO: Implement date validation logic here
        return date

    def clean_time(self):
        time = self.cleaned_data.get('time')
        # TODO: Implement time validation logic here
        return time

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        table = cleaned_data.get('table')

        # TODO: Implement logic to check if the table is already booked
        return cleaned_data