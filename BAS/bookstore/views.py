from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import Book,Cart,Inventory, Sales, ProcureBook, RequestBook, Vendor_list
from datetime import timedelta
import re
import random
import datetime


#---USER-LOGIN---#
def login_view(request):
    if request.method == 'POST':
        previous_url = request.session.get('previous_url') # get the previous url from cache
        email = request.POST['email'] # take the email from form
        user = authenticate(request, email=email) # authenticate whether that user is present or not
        if user is not None:
            login(request, user) # login if user present
            # redirect to previous url if it exists else go to the search page
            return redirect(previous_url) if previous_url else redirect('search')
        else:
            # show the error message if user email does not exists
            messages.error(request, 'Email not present ! Please Register')

    return render(request, 'registration/login.html') # render the login html page

#---REGISTER-A-NEW-USER---#
def register_view(request):
    if request.method == 'POST':
        previous_url = request.session.get('previous_url') # get the previous url from cache
        username = request.POST['username'] # get username and email
        email = request.POST['email']
        # if that user already exists
        if User.objects.filter(Q(email=email) | Q(username=username)).exists(): 
            messages.error(request, 'Username or email already exists')
        else:
            # else create a new user and login
            user = User.objects.create_user(username=username, email=email)  
            login(request, user)
            # redirect to previous url if it exists else go to the search page
            return redirect(previous_url) if previous_url else redirect('search')
    return render(request, 'registration/register.html') # render the registration html page

#---HOME-PAGE---#
def index(request):
    return render(request,'index.html') # return the home page

#---LOG-OUT-OF-ADMIN-PAGE---#
def logout_view(request):
  logout(request) # remove any authenticated user
  response = redirect('home') # redirect to the index.html page
  return response


#---SEARCH-BOOKS---#
def cleaner(query):
    metacharacters = [
        "^",  # Matches the beginning of the string
        "$",  # Matches the end of the string
        "*",  # Matches zero or more repetitions of the preceding character
        "+",  # Matches one or more repetitions of the preceding character
        "?",  # Matches zero or one occurrence of the preceding character
        "|",  # Alternation (either or)
        "[",  # Character class (start of a set of characters)
        "]",  # Character class (end of a set of characters)
        "\\",  # Escape character (to use a metacharacter literally)
        "{",  # Quantifier (start of a repetition specification)
        "}",  # Quantifier (end of a repetition specification)
        "(",  # Capturing group (start)
        ")",  # Capturing group (end)
        "^",  # Inside character class for negation (e.g., [^a-z])
        "-",  # Inside character class for range (e.g., [a-z])
    ]
    query1 = ""
    for i in query:
        if i in metacharacters:
            if i == "\\":
                query1+="\\\\"
            elif i == '^':
                query1+= '\^'
            else:
                query1 += '['+i+']'
        else:
            query1 += i
    return query1

#---SEARCH-BOOKS---#
def search(request):
    request.session['previous_url'] = request.build_absolute_uri()
    query = request.GET.get('query') # get query from the form
    search_type = request.GET.get('search_type') # get the query type i.e. by author or title

    all_books = Book.objects.all()
    shuffled_books = random.sample(list(all_books), len(all_books))
    
    genres=['fiction','spiritual','self-help','JEE','children']
    modal_value=0

    if query and search_type: # search for the book either by author name or title in the books table of db
        if search_type == 'author':
            books = search_authors(request)
        elif search_type == 'title':
            books = search_books(request)
        else:
            books = []
        normal = 0
    else: # if no query show the page with all the books
        books = []
        normal=1 # normal is the parameter which decides whether normal page is to be shown or searched results
    # render the page search.html  with the list of searched book
    return render(request, 'search.html', {'books': books, 'request': request, 'genres':genres, 'all_books':shuffled_books,'normal':normal, 'modal_value':modal_value})

def customer_to_search(request):
    all_books = Book.objects.all()
    shuffled_books = random.sample(list(all_books), len(all_books))
    
    genres=['fiction','spiritual','self-help','JEE','children']

    normal=1
    modal_value=1
    books = []

    return render(request, 'search.html', {'books': books, 'request': request, 'genres':genres, 'all_books':shuffled_books,'normal':normal, 'modal_value':modal_value})

#---SEARCH-TITLE---#
def search_books(request):
    
    query = cleaner(str(request.GET.get('query'))) # get query from the form)
    query2 = query.split(' ')
    query3 = str()
    count = 0
    for i in query2:
        if len(i) != 1:
            query3 += (str(i) + ".*")
            count = 1
        else:
            query3 += (str(i) + ".*")
    if count == 1:
        query = query3
    query = query.replace(' ','')
    query = query.lower()
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('title')}
    else: 
        books = {}
    y = "[.*,-:()' ]*"
    result = list()
    i = 0
    while(i< len(query)):
        if(query[i]=='['):
            y += query[i] + query[i+1] + query[i+2]
            i = i + 3
        elif (query[i] == "."):
            y += (query[i] + query[i+1])
            i = i + 2
        else:
            y += (query[i]+  "[.*,-:()' ]*")
            i= i + 1
    for i in books:
        if(re.search(y,i.lower())):
            result.append(i)
    books = Book.objects.none()
    for i in result:
        r = Book.objects.filter(
            Q(title=i)
        )
        books = books.union(r)
    # render the page search.html  with the list of searched book
    return books

#---SEARCH-AUTHORS---#
def search_authors(request):
    query = cleaner(str(request.GET.get('query'))) # get query from the form
    query = query.replace('.',' ')
    query2 = query.split(' ')
    count = 0
    j = 0
    for i in query2:
        if len(i) == 1:
            j = 2
            break
    if j == 2:
        query3 = "^"
    else:
        query3 = str()
    for i in query2:
        if len(i) != 1:
            query3 += str(i)
            count = 1
        else:
            query3 += (str(i) + ".*")
    if count == 1:
        query =  query3
    else:
        query = query
    query = query.replace(' ','')
    query = query.lower()
    print(query)
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('author')}
    else:
        books = {}
    y = "[.*,-:()' ]*"
    result = list()
    i = 0
    while(i< len(query)):
        if(query[i]=='['):
            y += query[i] + query[i+1] + query[i+2]
            i = i + 3
        elif (query[i] == "."):
            y += (query[i] + query[i+1])
            i = i + 2
        else:
            y += (query[i]+  "[\.\*,-:()' ]*")
            i= i + 1
    for i in books:
        if(re.search(y,i.lower())):
            result.append(i)
    books = Book.objects.none()
    for i in result:
        r = Book.objects.filter(
            Q(author=i)
        )
        books = books.union(r)
    # render the page search.html  with the list of searched book
    return books


#---ADD-A-BOOK-TO-CART---#
@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id) # get the book from the Book db using id
    #-----check quantity-------#
    quantity = request.POST.get('quantity') # get the quantity asked for
    if not quantity:
        messages.error(request, "Please enter a quantity.") # if no quantity is entered return to the previous searched page
        return redirect('/book_details/'+str(book_id))
    try:
        quantity = int(quantity)
    except ValueError: # if entered quantity is not a valid integer give error and return to previous page
        messages.error(request, "Invalid quantity.")
        return redirect('/book_details/'+str(book_id))

    if(quantity>book.inventory.stock):
        messages.error(request, f"Less stock for '{book.title}'")
        return redirect('/book_details/'+str(book_id))

    #------get the cart instance-------#
    # if book already present in cart get its instance else create a new instance
    cart, created = Cart.objects.get_or_create(user=request.user,book=book,defaults={'quantity': quantity})
    
    if created: # if new cart instance created
        cart.quantity = quantity
        cart.revenue = quantity*book.price
    else:
        if(cart.quantity+quantity>book.inventory.stock):
            messages.error(request, f"Less stock for '{book.title}'")
            return redirect('/book_details/'+str(book_id))
        cart.quantity += quantity
        cart.revenue += quantity*book.price

    cart.save() # save the book with quantity in the Cart

    # give a success message that the book is added to the cart and redirect to the book's detail page
    messages.success(request, f'"{book.title}" added to cart.')
    return redirect('/book_details/'+str(book_id))


#---CART-PAGE---#
def cart(request):
    if not request.user.is_authenticated: # if user not authenticated redirect to login page
        request.session['previous_url'] = request.build_absolute_uri() # save this url in cache
        return redirect('login')

    carts = Cart.objects.filter(user=request.user)
    # calculate the total price of cart
    total_price = sum(cart.book.price * cart.quantity for cart in carts)
    context = {
        'cart': carts,
        'total_price': total_price
    }
    return render(request, 'cart.html', context)

#---REMOVE-BOOK-FROM-CART---#
@login_required
def remove_from_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    book = cart.book
    cart.delete()
    messages.success(request, f'"{book.title}" removed from your cart.')
    return redirect('cart')

#---OPEN-BOOK_DETAILS-PAGE---#
def book_details(request,book_id):
    request.session['previous_url'] = request.build_absolute_uri()
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_details.html',{'book':book})

#---REQUEST-BOOK-IF-STOCK-OUT---#
@login_required
def request_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # get the user details and required quantity
        requested_by = request.user.username
        email = request.user.email
        quantity = request.POST.get('quantity')

        try:
            quantity = int(quantity)
        except ValueError: # if entered quantity is not a valid integer give error and return to previous page
            messages.error(request, "Quantity not entered.")
            return redirect('/book_details/'+str(book_id))

        if quantity <= 0:
            messages.error(request, 'Invalid quantity. Please enter a positive number.')
            return redirect('/book_details/'+str(book_id))

        if quantity <= book.inventory.stock:
            messages.error(request, f"The quantity of {quantity} can be bought with the existing stock !")
        else:
            # If the requested quantity exceeds the stock, create a request
            messages.success(request, f'Request sent for "{book.title}"')
            RequestBook.objects.create(date_of_request=timezone.localtime(timezone.now()),book=book, requested_by=requested_by, email=email, quantity=quantity).save()

    # Redirect back to the book detail page
    return redirect('/book_details/'+str(book_id))

#---REQUEST-FOR-A-NEW-BOOK---#
def send_procure_request(request):

    if not request.user.is_authenticated: # if user not authenticated redirect to login page
        request.session['previous_url'] = request.build_absolute_uri() # save this url in cache
        return redirect('login')

    if request.method == 'POST':
        # Get data from the request
        user_name = request.user.username
        email = request.user.email
        phone_no = request.POST.get('phone_no')
        book_title = request.POST.get('book_title')
        author_name = request.POST.get('author_name')
        book_publisher = request.POST.get('book_publisher')
        book_isbn = request.POST.get('book_isbn')
        genre = request.POST.get('genre')

        # Create and save the ProcureBook object
        procure_book = ProcureBook.objects.create(
            user_name=user_name,
            email=email,
            phone_no=phone_no,
            book_title=book_title,
            author_name=author_name,
            book_publisher=book_publisher,
            book_isbn=book_isbn,
            genre=genre
        )
        procure_book.save()
        messages.success(request, f"Request sent for {book_title} ")
        return redirect('send_procure_request')  # Redirect to a success page after form submission

    # If the request method is not POST, render the procurement.html template
    return render(request, 'procurement.html')


#---MAKE-BILL-AND-REDUCE-INVENTORY---#
@login_required
def proceed_to_buy(request):
    cart = Cart.objects.filter(user=request.user)
    if request.method =='POST': # get the name of buyer, email and phone number from the form

        if not cart.exists():
            messages.error(request, "Your cart is empty or Transaction is over")
            return redirect('cart')

        name = request.user.username
        email = request.user.email

        for cart_item in cart:
            book = cart_item.book
            inventory = Inventory.objects.get(book=book)
            # Handle insufficient stock situation
            if inventory.stock < cart_item.quantity:
                messages.error(request,f"Insufficient stock for {book.title} . Reduce your quantity.")
                return redirect('cart')

        for cart_item in cart:
            book = cart_item.book
            inventory = Inventory.objects.get(book=book)
            # if inventory stock is greater than or equal to asked quantity reduce the inventory
            if inventory.stock >= cart_item.quantity:
                inventory.stock -= cart_item.quantity
                inventory.save()
        
        # find the total price
        total_price = sum(cart_item.book.price * cart_item.quantity for cart_item in cart)

        # fill the bill content
        bill_email="\n"
        bill_date= datetime.date.today()
        bill_time= datetime.datetime.now().time()
        print(bill_time)

        for cart_item in cart:
            bill_email+=f"{cart_item.book.title} X {cart_item.quantity} - MRP:₹{cart_item.book.price} TOTAL:₹{cart_item.book.price * cart_item.quantity}\n"  #inside loop
            sales= Sales.objects.create(book=cart_item.book,quantity=cart_item.quantity,revenue=cart_item.book.price * cart_item.quantity,buyer_name=name)
            sales.save()
        bill_email+=f"\nTotal: ₹{total_price}"# just outside loop

        #email sending procedure
        subject = 'Bill for your purchase'
        message = f'Hi {name}, Thank you for buying.\n\nYour purchase is:\n{bill_email}\n\nVisit us Again'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )

        context = {
            'bill_content': bill_email,
            'bill_date': bill_date,
            'bill_time': bill_time,
            'buyer_name': name,
            'cart_items': cart,
            'total_price': total_price
        }
         # delete the cart and user
        Cart.objects.filter(user=request.user).delete()
        user = request.user
        if not user.is_superuser:
            Cart.objects.filter(user=user).delete()
            user.delete()
        logout(request)
        return render(request, 'bill.html', context)

    else:
        return redirect('cart')

# On logging out redirect to the index.html/home page
def logout_index(request):
    logout(request)
    return redirect('home')

#---When-START-SHOPPING-button-is-clicked---#
def start_shopping(request):
    logout(request)
    return redirect('search')

#---Send-EMAIL---#
def send_email(request):
    # get the cart objects of the user
    cart = Cart.objects.filter(user=request.user)
    if cart.exists():
        name=request.user.username
        email=request.user.email

        # writing the email message
        email_str="\n"
        for cart_item in cart:
            email_str+= f"{cart_item.book.title}  - Rack no: {cart_item.book.inventory.rack_number}\n"

        # Email sending procedure
        subject = 'Your Wishlist'
        message = f"Hi {name}, These are the book details.\n{email_str}\nHope you will like the books.\n\n\nDon't forget to complete your purchase."
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)

        messages.success(request, f"Book details sent successfully to {email}!")
    
    return redirect('cart')

