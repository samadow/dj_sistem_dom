"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp.views import *
from myapp.dashboard_views import dashboard, user_list, make_manager, remove_manager, RoleInquiryCreate, RoleBookingCreate, cancel_booking
from myapp.permissions import permission_required
from myapp.models import Booking


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', register, name='register'),
    path('login',login,name='login'),
    path('logaut',logauttt,name='logaut'),
    path('creat_b',permission_required('admin')(Bulindingcreat.as_view()),name='creat_b'),
    path('all_bul',permission_required('admin', 'manager', 'user')(BUlding_all.as_view()),name='all_bul'),
    path('buildings',permission_required('admin', 'manager', 'user')(BUlding_all.as_view()),name='bulding_all'),
    path('buildings/<int:pk>',permission_required('admin', 'manager', 'user')(boldingDetail.as_view()),name='bulding_detail'),
    path('buildings/<int:pk>/update',permission_required('admin')(bolding_up.as_view()),name='bulding_up'),
    path('buildings/<int:pk>/delete',permission_required('admin')(bulding_delete.as_view()),name='bulding_delete'),
    path('apartments',permission_required('admin', 'manager', 'user')(apartment_all.as_view()),name='apartment_all'),
    path('apartments/search',permission_required('admin', 'manager', 'user')(apartment_search),name='apartment_search'),
    path('apartments/<int:pk>',permission_required('admin', 'manager', 'user')(ApartmentDetail.as_view()),name='apartment_detail'),
    path('apartments/create',permission_required('admin', 'manager')(Apartment_cr.as_view()),name='apartment_cr'),
    path('apartments/<int:pk>/update',permission_required('admin', 'manager')(Apartment_up.as_view()),name='apartment_up'),
    path('apartments/<int:pk>/delete',permission_required('admin', 'manager')(apartment_delete.as_view()),name='apartment_delete'),
    path('inquiries',permission_required('admin', 'manager')(Inquiry_all.as_view()),name='inquiry_all'),
    path('inquiries/mine',permission_required('admin', 'manager', 'user')(MyInquiries.as_view()),name='my_inquiries'),
    path('inquiries/create',permission_required('admin', 'manager', 'user')(RoleInquiryCreate.as_view()),name='inquiry_cr'),
    path('inquiries/<int:pk>/update',permission_required('admin', 'manager')(Inquiry_up.as_view()),name='inquiry_up'),
    path('inquiries/<int:pk>/delete',permission_required('admin', 'manager')(Inquiry_delete.as_view()),name='inquiry_delete'),
    path('dashboard',dashboard,name='dahsboard'),
    path('users',user_list,name='user_list'),
    path('users/<int:pk>/make-manager',make_manager,name='make_manager'),
    path('users/<int:pk>/remove-manager',remove_manager,name='remove_manager'),
    path('delete',permission_required('admin', 'manager', 'user')(BUlding_all.as_view()),name='delete'),
    path('bookings', permission_required('admin', 'manager')(Booking_all.as_view()), name='booking_all'),
    path('bookings/mine', permission_required('admin', 'manager', 'user')(MyBookings.as_view()), name='my_bookings'),
    path('bookings/create', permission_required('admin', 'manager', 'user')(RoleBookingCreate.as_view()), name='booking_cr'),
    path('bookings/<int:pk>/update', permission_required('admin', 'manager')(Booking_up.as_view()), name='booking_up'),
    path('bookings/<int:pk>/delete', permission_required('admin', 'manager')(Booking_delete.as_view()), name='booking_delete'),
    path('bookings/<int:pk>/confirm', permission_required('admin', 'manager')(booking_confirm), name='booking_confirm'),
    path('bookings/<int:pk>/reject', permission_required('admin', 'manager')(booking_reject), name='booking_reject'),
    path('bookings/<int:pk>/cancel', permission_required('admin', 'manager', 'user', owner_model=Booking)(cancel_booking), name='booking_cancel'),
    path('sales', permission_required('admin', 'manager')(Sale_all.as_view()), name='sale_all'),
    path('sales/create', permission_required('admin', 'manager')(Sale_creat.as_view()), name='sale_cr'),
    path('sales/<int:pk>', permission_required('admin', 'manager')(Sale_detail.as_view()), name='sale_detail'),
    path("ai", permission_required('admin', 'manager', 'user')(ai_chat), name="ai"),
    path("ai/", permission_required('admin', 'manager', 'user')(ai_chat), name="ai_slash"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
