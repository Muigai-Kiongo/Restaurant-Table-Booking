from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Meal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} (@ {self.price})"
    

class Table(models.Model):
    number = models.IntegerField()
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
   
    def __str__(self):
        return f"Table {self.number} (Capacity: {self.capacity})"


class BookingManager(models.Manager):
    def with_relations(self):
        return self.select_related('user', 'table', 'meal_option')

    def upcoming_for_user(self, user):
        now = timezone.now()
        return self.with_relations().filter(
            user=user, 
            date__gte=now.date()
        ).exclude(
            date=now.date(), 
            time__lt=now.time()
        ).order_by('date', 'time')

    def past_for_user(self, user):
        now = timezone.now()
        return self.with_relations().filter(
            user=user
        ).filter(
            models.Q(date__lt=now.date()) | 
            models.Q(date=now.date(), time__lt=now.time())
        ).order_by('-date', '-time')

    def get_by_report_type(self, report_type):
        now = timezone.now()
        qs = self.with_relations()
        if report_type == 'weekly':
            week_start = now.date() - timedelta(days=7)
            return qs.filter(date__gte=week_start)
        elif report_type == 'monthly':
            month_start = now.date().replace(day=1)
            return qs.filter(date__gte=month_start)
        elif report_type == 'yearly':
            year_start = now.date().replace(month=1, day=1)
            return qs.filter(date__gte=year_start)
        return qs.none()


class Booking(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash on Arrival'),
        ('M-Pesa', 'M-Pesa STK Push'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    time = models.TimeField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    meal_option = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    mpesa_receipt_number = models.CharField(max_length=50, null=True, blank=True)

    objects = BookingManager()

    def __str__(self):
        return f"Booking by {self.user} for {self.table} on {self.date} at {self.time} to have {self.meal_option}"
