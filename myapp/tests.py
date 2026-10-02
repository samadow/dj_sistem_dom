from django.test import TestCase
from django.urls import reverse

from .models import Apartment, Building


class PropertyDetailTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(
            name="Бинои якум", address="Кӯчаи якум", total_floors=5
        )
        self.other_building = Building.objects.create(
            name="Бинои дуюм", address="Кӯчаи дуюм", total_floors=7
        )
        self.apartment = Apartment.objects.create(
            building=self.building, number=11, floor=2, rooms=3, area=70, price=500000
        )
        Apartment.objects.create(
            building=self.other_building, number=22, floor=3, rooms=2, area=50, price=300000
        )
        session = self.client.session
        session["user_id"] = 1
        session.save()

    def test_building_detail_only_lists_its_apartments(self):
        response = self.client.get(reverse("bulding_detail", args=[self.building.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бинои якум")
        self.assertContains(response, "Квартира №11")
        self.assertNotContains(response, "Квартира №22")

    def test_apartment_detail_links_back_to_its_building(self):
        response = self.client.get(reverse("apartment_detail", args=[self.apartment.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Квартира №11")
        self.assertContains(response, reverse("bulding_detail", args=[self.building.pk]))

    def test_details_require_login(self):
        self.client.session.flush()
        response = self.client.get(reverse("bulding_detail", args=[self.building.pk]))
        self.assertRedirects(response, reverse("login"))

    def test_my_pages_render(self):
        for name in ("my_inquiries", "my_bookings"):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
