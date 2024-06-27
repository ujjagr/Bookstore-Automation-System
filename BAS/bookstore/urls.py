from django.urls import path
from . import views

urlpatterns = [
    # user-login
    path('login/', views.login_view, name='login'),
    # user-register
    path('register/', views.register_view, name='register'),
    # home page
    path('',views.index,name='home'),
    # user-logout
    path('logout/', views.logout_view, name='logout'),
    # search page
    path('search/',views.search, name='search'),
    # search page on clicking the customer button from index page.
    path('customer_to_search/',views.customer_to_search,name='customer_to_search'),
    # add a book to cart
    path("add_to_cart/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    # cart page
    path("cart/", views.cart, name="cart"), 
    # remove a book from cart
    path("remove_from_cart/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    # book details page
    path('book_details/<int:book_id>/', views.book_details, name='book_details'),
    # request a book having less stock
    path('request_book/<int:book_id>/',views.request_book,name='request_book'),
    # procure a new book page
    path('send-procure-request/', views.send_procure_request, name='send_procure_request'), 
    # proceed to buy and generate bill
    path('proceed_to_buy/', views.proceed_to_buy, name='proceed_to_buy'),
    # when start shopping is clicked
    path('start_shopping/',views.start_shopping,name='start_shopping'),  
    # send the wishlist
    path('send_email',views.send_email,name='send_email'),
    # logout and move to the index page
    path('logout_index',views.logout_index,name='logout_index'),
]
