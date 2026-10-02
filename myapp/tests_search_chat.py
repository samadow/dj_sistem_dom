from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Apartment, Building, User


class SearchAndChatTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(username="admin", phone_number="100", password="x", role="admin")
        self.user = User.objects.create(username="client", phone_number="101", password="x", role="user")
        self.building = Building.objects.create(name="Сомони", address="Марказ", total_floors=5)
        self.available = Apartment.objects.create(
            building=self.building, number=12, floor=2, rooms=3, area=75, price=300000,
        )
        self.sold = Apartment.objects.create(
            building=self.building, number=18, floor=3, rooms=2, area=50, price=220000,
            status="sold",
        )

    def sign_in(self, user):
        session = self.client.session
        session["user_id"] = user.pk
        session.save()

    def test_search_is_available_to_all_roles_and_filters_client_results(self):
        self.sign_in(self.user)
        response = self.client.get(reverse("apartment_search"), {"q": "Сомони"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Квартира №12")
        self.assertNotContains(response, "Квартира №18")

        response = self.client.get(reverse("apartment_search"), {"q": "12", "floor": "2"})
        self.assertEqual(list(response.context["apartments"]), [self.available])

        self.sign_in(self.admin)
        response = self.client.get(reverse("apartment_search"), {"q": "Сомони"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Квартира №18")

    def test_chat_requires_login(self):
        response = self.client.get(reverse("ai"))
        self.assertRedirects(response, reverse("login"))

    def test_chat_accepts_both_url_forms(self):
        self.sign_in(self.user)
        self.assertEqual(self.client.get("/ai").status_code, 200)
        self.assertEqual(self.client.get("/ai/").status_code, 200)

    def test_chat_page_has_its_own_form_and_menu_link(self):
        self.sign_in(self.user)
        response = self.client.get(reverse("ai"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ai_chat.html")
        self.assertContains(response, 'name="question"')
        self.assertContains(response, 'AI ёрдамчӣ')

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("myapp.views.Groq")
    def test_chat_returns_json_and_keeps_conversation(self, groq):
        self.sign_in(self.user)
        groq.return_value.chat.completions.create.return_value.choices = [
            type("Choice", (), {"message": type("Message", (), {"content": "Салом!"})()})()
        ]
        response = self.client.post(
            reverse("ai"), {"question": "Салом"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Салом!")
        self.assertEqual(
            groq.return_value.chat.completions.create.call_args.kwargs["model"],
            "openai/gpt-oss-120b",
        )
        history = self.client.get(reverse("ai"), HTTP_X_REQUESTED_WITH="XMLHttpRequest").json()["history"]
        self.assertEqual([item["role"] for item in history], ["user", "assistant"])
