from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AccountsViewTests(TestCase):
    def test_signup_view_status_code(self):
        response = self.client.get(reverse('register'))
        # Using status_code 200 to check if page renders correctly
        self.assertEqual(response.status_code, 200)

    def test_signup_view_template(self):
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'registration/register.html')
