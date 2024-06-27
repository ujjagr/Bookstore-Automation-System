"""
URL configuration for BAS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

admin.site.site_header= "AUTHORISED LOGIN"
admin.site.site_title= "AUTHORISED LOGIN"
admin.site.index_title= "Welcome to Bookstore Management Portal"

from bookstore.views import logout_view

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    # note the override comes before the admin URLs below
    path('admin/logout/', lambda request: redirect('/logout/', permanent=False)),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('',include('bookstore.urls')),
]
