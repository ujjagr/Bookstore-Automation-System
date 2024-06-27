from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# MODELS

#---------BOOK-----------#
class Book(models.Model):
    title= models.CharField(max_length=100)
    author= models.CharField(max_length=100)
    publisher= models.CharField(max_length=100)
    price= models.DecimalField(max_digits=8, decimal_places=2)
    isbn= models.CharField(max_length=13,unique=True)
    image= models.ImageField(upload_to='static/images',default='static/images/book.jpg')
    genre= models.CharField(max_length=50,default="others")
    desc= models.CharField(max_length=1000,default="")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new book instance
            super().save(*args, **kwargs)  # Save the book instance
            # Create corresponding Inventory instance with zero stock
            Inventory.objects.create(book=self)
            Vendor_list.objects.create(book=self)
        else:
            super().save(*args, **kwargs)  # For existing books, just save normally

#---------INVENTORY-----------#
class Inventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    rack_number = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.book.title} - {self.stock}"

    # whenever inventory changes reflect it in the vendor's list model
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update corresponding Vendor_list stock
        try:
            vendor_list = Vendor_list.objects.get(book=self.book)
            vendor_list.stock = self.stock
            vendor_list.save()
        except Vendor_list.DoesNotExist:
            pass

#---------REQUEST-BOOK-(requests for books with less stock)-----------#
class RequestBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    requested_by = models.CharField(max_length=50)
    email= models.EmailField(default="")
    quantity= models.IntegerField(default=0)
    date_of_request= models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.book.title}-{self.requested_by}"

#---------PROCURE-BOOK-(requests for procurement of a new book)-----------#
class ProcureBook(models.Model):
    user_name= models.CharField(max_length=50)
    email= models.EmailField()
    phone_no= models.IntegerField()
    book_title= models.CharField(max_length=50)
    author_name= models.CharField(max_length=50)
    book_publisher= models.CharField(max_length=50)
    book_isbn= models.CharField(max_length=13,default="")
    genre= models.CharField(max_length=50,default="")

    def __str__(self):
        return f"{self.book_title}-{self.user_name}"

#---------CART-(to store the books customer wants to buy)-----------#
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    revenue= models.DecimalField(max_digits=8, decimal_places=2,default=0)

    def __str__(self):
        return f"{self.book.title}-{self.quantity}"

    def update_revenue(self):
        self.revenue = self.quantity * self.book.price
        self.save()

#---------SALES-(contains all the sales done in the shop)-----------#
class Sales(models.Model):
    date= models.DateTimeField(default=timezone.now())
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    revenue= models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.IntegerField(default=0)
    buyer_name= models.CharField(max_length=100,default="")

    def __str__(self):
        return f"{self.date} - {self.book.title}"

    def delete(self, *args, **kwargs):
        # Update inventory before deleting the sale
        inventory = Inventory.objects.get(book=self.book)
        inventory.stock += self.quantity  # Increase stock by the quantity of the sale being deleted
        inventory.save()

        super().delete(*args, **kwargs)

#---------VENDOR-(contains the details of all vendors)-----------#
class Vendor(models.Model):
    name= models.CharField(max_length=100)
    email= models.EmailField()
    phone= models.IntegerField()
    address= models.CharField(max_length=200)

    def __str__(self):
        return self.name

#---------VENDOR-LIST(contains the list of all books and there corresponding vendors)-----------#
class Vendor_list(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    vendor= models.ForeignKey(Vendor,on_delete=models.CASCADE,null=True)
    threshold= models.IntegerField(default=20)
    stock= models.IntegerField(default=0)

    def __str__(self):
        return self.book.title
    




