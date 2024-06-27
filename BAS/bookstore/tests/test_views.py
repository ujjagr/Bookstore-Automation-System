from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from bookstore.models import Book,Cart, Inventory
from django.db import transaction

class ModelTestCase(TestCase):
    def setUp(self):
        self.client= Client()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.search_url = reverse('search')

    def test_login_success(self):
        user= User.objects.create_user(username='testuser', email='test@example.com')
        response= self.client.post(self.login_url, {'email': 'test@example.com'})
        self.assertRedirects(response, self.search_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        response = self.client.post(self.login_url, {'email': 'nonexistent@example.com'})
        self.assertRedirects(response, self.register_url) 

    def test_register_success(self):
        response = self.client.post(self.register_url, {'username': 'newuser', 'email': 'newuser@example.com'})
        self.assertRedirects(response, self.search_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_failure(self):
        User.objects.create_user(username='existinguser', email='existinguser@example.com', password='password')
        response = self.client.post(self.register_url, {'username': 'existinguser', 'email': 'existinguser@example.com'})
        self.assertEqual(response.status_code, 200)  # Status code 200 indicates staying on the page
        self.assertContains(response, 'Username or email already exists')

        print("User authentication working fine...")

