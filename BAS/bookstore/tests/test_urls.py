import random
from django.test import TestCase
from django.urls import reverse, resolve
from bookstore import views
from bookstore.models import Book, Cart
from unittest.mock import patch
from django.contrib.auth.models import User  # Import User model

class TestUrls(TestCase):

    def setUp(self):
        # Create a sample book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            publisher='Test Publisher',
            price=random.uniform(10.0, 50.0),  # Random price between 10.0 and 50.0
            isbn='1234567890123'
        )

        # Create a sample user
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password='password'
        )

        # Create a sample cart with the sample book and user
        self.cart = Cart.objects.create(
            user=self.user,
            book=self.book,
            quantity=random.randint(1, 10),  # Random quantity between 1 and 10
            revenue=random.uniform(10.0, 500.0)  # Random revenue between 10.0 and 500.0
        )

    # Patch the Book.objects.values_list method to return a book ID for testing add_to_cart URL resolution
    @patch('bookstore.models.Book.objects.values_list')
    def test_add_to_cart_url_is_resolved(self, mock_book_values_list):
        book_id = self.book.id
        mock_book_values_list.return_value = [book_id]
        url = reverse('add_to_cart', args=[book_id])
        self.assertEquals(resolve(url).func, views.add_to_cart)

    # Patch the Cart.objects.values_list method to return a cart ID for testing remove_from_cart URL resolution
    @patch('bookstore.models.Cart.objects.values_list')
    def test_remove_from_cart_url_is_resolved(self, mock_cart_values_list):
        cart_id = self.cart.id
        mock_cart_values_list.return_value = [cart_id]
        url = reverse('remove_from_cart', args=[cart_id])
        self.assertEquals(resolve(url).func, views.remove_from_cart)

    # Test URL resolution for login
    def test_login_url_is_resolved(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, views.login_view)

    # Test URL resolution for register
    def test_register_url_is_resolved(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, views.register_view)

    # Test URL resolution for home
    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, views.index)

    # Test URL resolution for logout
    def test_logout_url_is_resolved(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, views.logout_view)

    # Test URL resolution for search
    def test_search_url_is_resolved(self):
        url = reverse('search')
        self.assertEquals(resolve(url).func, views.search)

    # Test URL resolution for cart
    def test_cart_url_is_resolved(self):
        url = reverse('cart')
        self.assertEquals(resolve(url).func, views.cart)

    # Test URL resolution for book_details
    def test_book_details_url_is_resolved(self):
        book_id = self.book.id
        if book_id:
            url = reverse('book_details', args=[book_id])
            self.assertEquals(resolve(url).func, views.book_details)

    # Test URL resolution for request_book
    def test_request_book_url_is_resolved(self):
        book_id = self.book.id
        if book_id:
            url = reverse('request_book', args=[book_id])
            self.assertEquals(resolve(url).func, views.request_book)

    # Test URL resolution for send_procure_request
    def test_send_procure_request_url_is_resolved(self):
        url = reverse('send_procure_request')
        self.assertEquals(resolve(url).func, views.send_procure_request)

    # Test URL resolution for proceed_to_buy
    def test_proceed_to_buy_url_is_resolved(self):
        url = reverse('proceed_to_buy')
        self.assertEquals(resolve(url).func, views.proceed_to_buy)

    # Test URL resolution for start_shopping
    def test_start_shopping_url_is_resolved(self):
        url = reverse('start_shopping')
        self.assertEquals(resolve(url).func, views.start_shopping)

    # Test URL resolution for send_email
    def test_send_email_url_is_resolved(self):
        url = reverse('send_email')
        self.assertEquals(resolve(url).func, views.send_email)

    # Test URL resolution for logout_index
    def test_logout_index_url_is_resolved(self):
        url = reverse('logout_index')
        self.assertEquals(resolve(url).func, views.logout_index)

        print("URLs working fine...")

