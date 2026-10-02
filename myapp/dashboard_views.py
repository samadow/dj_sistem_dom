from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .models import Apartment, Booking, Building, Inquiry, Sale, User
from .permissions import permission_required
from .views import Booking_creat, Inquiry_creat, booking_cancel as existing_booking_cancel


@permission_required('admin', 'manager', 'user')
def dashboard(request):
    user = request.app_user
    context = {'current_user': user}

    if user.role == 'admin':
        context.update(
            user_count=User.objects.count(),
            building_count=Building.objects.filter(is_active=True).count(),
            apartment_count=Apartment.objects.filter(is_active=True).count(),
            sale_count=Sale.objects.count(),
            recent_users=User.objects.order_by('-pk')[:5],
            recent_sales=Sale.objects.select_related('apartment', 'apartment__building').order_by('-sold_at')[:4],
        )
        template = 'admin_dashboard.html'
    elif user.role == 'manager':
        context.update(
            unanswered_count=Inquiry.objects.filter(answer='').count(),
            pending_count=Booking.objects.filter(status='pending').count(),
            available_count=Apartment.objects.filter(is_active=True, status='available').count(),
            unanswered_inquiries=Inquiry.objects.filter(answer='').select_related('apartment', 'apartment__building').order_by('-created_at')[:4],
            pending_bookings=Booking.objects.filter(status='pending').select_related('apartment', 'apartment__building', 'user').order_by('-created_at')[:4],
        )
        template = 'manager_dashboard.html'
    else:
        context.update(
            inquiries=Inquiry.objects.filter(user=user).select_related('apartment', 'apartment__building').order_by('-created_at')[:5],
            bookings=Booking.objects.filter(user=user).select_related('apartment', 'apartment__building').order_by('-created_at')[:5],
        )
        template = 'user_dashboard.html'

    return render(request, template, context)


@permission_required('admin')
def user_list(request):
    return render(request, 'user_list.html', {
        'users': User.objects.order_by('username'),
        'current_user': request.app_user,
    })


@require_POST
@permission_required('admin')
def make_manager(request, pk):
    user = get_object_or_404(User, pk=pk, role='user')
    user.role = 'manager'
    user.save(update_fields=['role'])
    return redirect('user_list')


@require_POST
@permission_required('admin')
def remove_manager(request, pk):
    user = get_object_or_404(User, pk=pk, role='manager')
    user.role = 'user'
    user.save(update_fields=['role'])
    return redirect('user_list')


class RoleInquiryCreate(Inquiry_creat):
    success_url = reverse_lazy('my_inquiries')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('user', None)
        form.fields.pop('answer', None)
        return form

    def form_valid(self, form):
        form.instance.user = self.request.app_user
        return super().form_valid(form)


class RoleBookingCreate(Booking_creat):
    success_url = reverse_lazy('my_bookings')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('user', None)
        form.fields.pop('status', None)
        return form

    def form_valid(self, form):
        form.instance.user = self.request.app_user
        return super().form_valid(form)


def cancel_booking(request, pk):
    response = existing_booking_cancel(request, pk)
    if request.app_user.role == 'user' and 300 <= response.status_code < 400:
        return redirect('my_bookings')
    return response
