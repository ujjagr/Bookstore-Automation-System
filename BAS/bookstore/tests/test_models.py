from django.test import TestCase
from bookstore.models import Book, Inventory, Vendor_list, RequestBook, ProcureBook, Cart, Sales, Vendor
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            publisher='Test Publisher',
            price=19.99,
            isbn='9780123456789',
            # image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            genre='Test Genre',
            desc='Test Description'
        )
        # Check if an Inventory instance already exists for the Book
        if not hasattr(self.book, 'inventory'):
            self.inventory = Inventory.objects.create(book=self.book, stock=10, rack_number='A')
        else:
            self.book.inventory.stock=10
            self.book.inventory.rack_number='A'
            self.inventory = self.book.inventory  # Use the existing Inventory instance
        
        self.vendor = Vendor.objects.create(name='Test Vendor', email='test@example.com', phone=1234567890, address='Test Address')

        if not hasattr(self.book, 'vendor_list'):
            self.vendor_list = Vendor_list.objects.create(book=self.book, vendor=self.vendor, threshold=20, stock=10)
        else:
            self.book.vendor_list.vendor=self.vendor
            self.vendor_list = self.book.vendor_list  # Use the existing Inventory instance
        
        self.request_book = RequestBook.objects.create(book=self.book, requested_by='Test User', email='test@example.com', quantity=1, date_of_request=timezone.now())
        self.procure_book = ProcureBook.objects.create(user_name='Test User', email='test@example.com', phone_no=1234567890, book_title='Test Book', author_name='Test Author', book_publisher='Test Publisher', genre='Test Genre')
        self.cart = Cart.objects.create(user=self.user, book=self.book, quantity=2, revenue=39.98)
        self.sales = Sales.objects.create(date=timezone.now(), book=self.book, revenue=19.99, quantity=1, buyer_name='Test User')

    def test_book_model(self):
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')
        self.assertEqual(self.book.publisher, 'Test Publisher')
        self.assertEqual(float(self.book.price), 19.99)
        self.assertEqual(self.book.isbn, '9780123456789')
        self.assertEqual(self.book.genre, 'Test Genre')
        self.assertEqual(self.book.desc, 'Test Description')

    def test_inventory_model(self):
        self.assertEqual(str(self.inventory), 'Test Book - 10')

    def test_vendor_model(self):
        self.assertEqual(self.vendor.name, 'Test Vendor')
        self.assertEqual(self.vendor.email, 'test@example.com')
        self.assertEqual(self.vendor.phone, 1234567890)
        self.assertEqual(self.vendor.address, 'Test Address')

    def test_vendor_list_model(self):
        self.assertEqual(str(self.vendor_list), 'Test Book')

    def test_request_book_model(self):
        self.assertEqual(str(self.request_book), 'Test Book-Test User')

    def test_procure_book_model(self):
        self.assertEqual(str(self.procure_book), 'Test Book-Test User')

    def test_cart_model(self):
        self.assertEqual(str(self.cart), 'Test Book-2')
        self.assertEqual(float(self.cart.revenue), 39.98)

    def test_sales_model(self):
        self.assertEqual(str(self.sales), f"{self.sales.date} - Test Book")
        self.assertEqual(float(self.sales.revenue), 19.99)

    def test_update_revenue_method(self):
        # Update revenue for the cart
        self.cart.update_revenue()
        self.assertEqual(float(self.cart.revenue), 39.98)  # Revenue should remain the same as quantity * price

        # Update revenue after changing quantity
        self.cart.quantity = 3
        self.cart.update_revenue()
        self.assertEqual(float(self.cart.revenue), 59.97)  # New revenue should reflect the new quantity * price

    def test_book_save_method(self):
        # Create a new book instance
        new_book = Book.objects.create(
            title='New Test Book',
            author='New Test Author',
            publisher='New Test Publisher',
            price=29.99,
            isbn='9780123456780',  # Different ISBN to ensure uniqueness
            image=SimpleUploadedFile(name='new_test_image.jpg', content=b'', content_type='image/jpeg'),
            genre='New Test Genre',
            desc='New Test Description'
        )
        
        # Check if an inventory instance is created for the new book
        self.assertIsNotNone(new_book.inventory)
        
        # Check if a vendor list instance is created for the new book
        self.assertIsNotNone(new_book.vendor_list)

    def test_inventory_save_method(self):
        # Create a new book instance
        new_book = Book.objects.create(
            title='Another Test Book',
            author='Another Test Author',
            publisher='Another Test Publisher',
            price=39.99,
            isbn='9780123456781',
            image=SimpleUploadedFile(name='another_test_image.jpg', content=b'', content_type='image/jpeg'),
            genre='Another Test Genre',
            desc='Another Test Description'
        )
        
        # Create a new inventory instance manually
        new_inventory = Inventory.objects.get(book=new_book)
        new_inventory.stock=22
        # Save the inventory
        new_inventory.save()
        
        # Check if the vendor list stock is updated accordingly
        vendor_list = Vendor_list.objects.get(book=new_book)
        self.assertEqual(vendor_list.stock, 22)

        print("Models working fine...")
    
