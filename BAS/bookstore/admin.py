from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, F 
from django.core.mail import send_mail
from django.conf import settings

from bookstore.models import Book,RequestBook,ProcureBook,Cart,Inventory,Sales, Vendor, Vendor_list
from datetime import datetime,timedelta
from rangefilter.filters import DateRangeFilter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

# admin.site.register(Cart)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'publisher','price')
    ordering= ('title',)  # Hierarchical date-based navigation
    search_fields= ('title','author','isbn','publisher','genre')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'stock', 'rack_number')
    ordering= ('rack_number',)  # Hierarchical date-based navigation

@admin.register(RequestBook)
class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('date_of_request', 'book', 'requested_by', 'quantity')
    ordering= ('date_of_request',)  # Hierarchical date-based navigation
    search_fields= ('requested_by',)

@admin.register(ProcureBook)
class ProcureBookAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'book_title', )

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('date', 'book','buyer_name', 'revenue', 'quantity')
    ordering= ('-date',)  # Hierarchical date-based navigation

    list_filter=(
        ("date",DateRangeFilter), 
        "book" 
    )

    change_list_template = 'admin/sales_change_list.html'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        queryset = response.context_data['cl'].queryset
        total_revenue = queryset.aggregate(total_revenue=Sum('revenue'))['total_revenue']
        graph_data= self.revenue_graph(queryset)
        response.context_data['total_revenue'] = total_revenue if total_revenue is not None else 0
        response.context_data['graph_data']=graph_data
        return response

    def revenue_graph(self, queryset):
        date_revenues = {}  # Dictionary to store total revenues for each date

        # Aggregate revenues for each date
        for sale in queryset:
            date = sale.date  # Extract date portion
            date_local= date+timedelta(hours=5,minutes=30)
            date_local= date_local.date()
            if date_local in date_revenues:
                date_revenues[date_local] += sale.revenue
            else:
                date_revenues[date_local] = sale.revenue

        
        dates = sorted(date_revenues.keys())
        revenues = [date_revenues[date] for date in dates]

        bar_width = 0.1 

        plt.figure(figsize=(6, 4))  # Adjust the figure size as needed
        plt.bar(dates, revenues, color='blue',width=bar_width)  # Create a bar plot
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Set tick interval to 1 day

        plt.title('TOTAL REVENUE v/s DATE')
        plt.xlabel('DATE')
        plt.ylabel('TOTAL REVENUE (in ₹)')
        plt.grid(True)
        plt.xticks(rotation=90)
        plt.tight_layout()

        # Convert plot to PNG image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Return a template response with the plot image
        return encoded_image

    

class ThresholdFIlter(admin.SimpleListFilter):
    title= _("Threshold")
    parameter_name= "threshold"

    def lookups(self,request,model_admin):
        return[
            ("threshold",("Update threshold and Show books below threshold"))
        ]

    def queryset(self,request,queryset):
        if self.value()=="threshold":
            # Calculate the date range for the last two weeks
            two_weeks_ago = timezone.localtime(timezone.now()) - timedelta(days=14)

            # Query to get the count of books sold in the last two weeks
            books_sold = Sales.objects.filter(
                date__gte=two_weeks_ago,
            ).values('book').annotate(total_sold=Sum('quantity'))

            # Dictionary to store the updated thresholds for each book
            updated_thresholds = {}

            for book_sold in books_sold:
                book_id = book_sold['book']
                total_sold = book_sold['total_sold']
                new_threshold = 20 + total_sold
                updated_thresholds[book_id] = new_threshold

            # Update the threshold for each book
            for book_id, new_threshold in updated_thresholds.items():
                Vendor_list.objects.filter(book_id=book_id).update(threshold=new_threshold)

            # Filter books below threshold
            books_below_threshold = Vendor_list.objects.filter(book__inventory__stock__lt=F('threshold'))
            

            return books_below_threshold

@admin.register(Vendor_list)
class VendorListAdmin(admin.ModelAdmin):
    list_display = ('book', 'vendor','threshold','stock')
    list_filter= [ThresholdFIlter]
    ordering=('vendor',)
    # change_list_template='admin/added_button.html'
    actions=['send_orders_to_vendors']

    def send_orders_to_vendors(self, request, queryset):
        # Collect all vendors and their respective books below threshold
        vendor_books = {}
        for vendor_list in queryset:
            if vendor_list.stock < vendor_list.threshold:
                if vendor_list.vendor.id not in vendor_books:
                    vendor_books[vendor_list.vendor.id] = []
                vendor_books[vendor_list.vendor.id].append(vendor_list)

        # Send orders to vendors
        for vendor_id, books in vendor_books.items():
            vendor = Vendor.objects.get(id=vendor_id)
            order_message = "Please supply the following books:\n\n"
            for book in books:
                order_message += f"- {book.book.title} ({book.threshold - book.stock} copies)\n"

            # Send the order message to the vendor via email
            send_mail(
                subject="Order Request",
                message=order_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[vendor.email],
            )

        self.message_user(request, _("Orders sent to vendors successfully."))

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    
