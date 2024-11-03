from django.db import models
from django.contrib.auth.models import User

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

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    time = models.TimeField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    meal_option = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15, null=True)

    def __str__(self):
        return f"Booking by {self.user} for {self.table} on {self.date} at {self.time} to have {self.meal_option}"