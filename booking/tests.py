from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Meal, Table, Booking
from datetime import datetime, time

class BookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.meal = Meal.objects.create(name='Test Meal', description='Test Description', price=10.00)
        self.table = Table.objects.create(number=1, capacity=4, is_available=True)
        self.booking = Booking.objects.create(
            user=self.user,
            date=datetime.now().date(),
            time=time(12, 0),
            table=self.table,
            meal_option=self.meal,
            phone_number='1234567890'
        )

    def test_meal_creation(self):
        self.assertEqual(self.meal.name, 'Test Meal')

    def test_table_creation(self):
        self.assertEqual(self.table.number, 1)

    def test_booking_creation(self):
        self.assertEqual(self.booking.user.username, 'testuser')
        self.assertEqual(self.booking.table.number, 1)

class BookingViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_index_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_booking_list_view(self):
        response = self.client.get(reverse('booking_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/booking_list.html')
