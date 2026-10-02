from django.test import TestCase
from django.urls import reverse

from .models import Apartment, Booking, Building, Inquiry, User


class RoleDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin1', password='x', phone_number='1', role='admin')
        self.manager = User.objects.create(username='manager1', password='x', phone_number='2', role='manager')
        self.user = User.objects.create(username='user1', password='x', phone_number='3', role='user')
        self.other = User.objects.create(username='user2', password='x', phone_number='4', role='user')
        building = Building.objects.create(name='Бино', address='Суроға', total_floors=5)
        self.apartment = Apartment.objects.create(
            building=building, number=1, floor=1, rooms=2, area=60, price=100000,
        )
        Inquiry.objects.create(apartment=self.apartment, user=self.user, question='Саволи ман')
        Inquiry.objects.create(apartment=self.apartment, user=self.other, question='Саволи дигар')

    def sign_in(self, user):
        session = self.client.session
        session['user_id'] = user.pk
        session.save()

    def test_each_role_gets_its_dashboard(self):
        for user, template in (
            (self.admin, 'admin_dashboard.html'),
            (self.manager, 'manager_dashboard.html'),
            (self.user, 'user_dashboard.html'),
        ):
            self.sign_in(user)
            response = self.client.get(reverse('dahsboard'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)

        self.assertContains(response, 'Саволи ман')
        self.assertNotContains(response, 'Саволи дигар')
        self.assertNotContains(response, 'Корбарон ва нақшҳо')

    def test_only_admin_can_change_roles(self):
        self.sign_in(self.manager)
        self.assertEqual(self.client.get(reverse('user_list')).status_code, 403)
        self.assertEqual(
            self.client.post(reverse('make_manager', args=[self.user.pk])).status_code, 403
        )

        self.sign_in(self.admin)
        self.assertEqual(self.client.get(reverse('user_list')).status_code, 200)
        self.assertRedirects(
            self.client.post(reverse('make_manager', args=[self.user.pk])),
            reverse('user_list'),
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'manager')

    def test_role_routes_match_dashboard_actions(self):
        self.sign_in(self.user)
        self.assertEqual(self.client.get(reverse('bulding_all')).status_code, 200)
        self.assertEqual(self.client.get(reverse('apartment_all')).status_code, 200)
        for name in ('creat_b', 'apartment_cr', 'inquiry_all', 'booking_all', 'sale_all'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 403)

        self.sign_in(self.manager)
        self.assertEqual(self.client.get(reverse('creat_b')).status_code, 403)
        self.assertEqual(self.client.get(reverse('apartment_cr')).status_code, 200)
        self.assertEqual(self.client.get(reverse('inquiry_all')).status_code, 200)
        self.assertEqual(self.client.get(reverse('booking_all')).status_code, 200)

    def test_user_creates_records_for_self(self):
        self.sign_in(self.user)
        inquiry_response = self.client.post(reverse('inquiry_cr'), {
            'apartment': self.apartment.pk,
            'question': 'Саволи нав',
            'user': self.other.pk,
            'answer': 'Ҷавоби сохта',
        })
        self.assertRedirects(inquiry_response, reverse('my_inquiries'))
        inquiry = Inquiry.objects.get(question='Саволи нав')
        self.assertEqual(inquiry.user_id, self.user.pk)
        self.assertEqual(inquiry.answer, '')

        booking_response = self.client.post(reverse('booking_cr'), {
            'apartment': self.apartment.pk,
            'user': self.other.pk,
            'status': 'confirmed',
        })
        self.assertRedirects(booking_response, reverse('my_bookings'))
        booking = Booking.objects.get(apartment=self.apartment)
        self.assertEqual(booking.user_id, self.user.pk)
        self.assertEqual(booking.status, 'pending')
