from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club
from events.models import Event, EventAttendance


User = get_user_model()


class EventViewTests(TestCase):
    def setUp(self):
        # Each test gets its own users, club, and event in Django's test database.
        self.creator = User.objects.create_user(username="creator", password="pass-12345")
        self.other_user = User.objects.create_user(username="visitor", password="pass-12345")
        self.staff_user = User.objects.create_user(
            username="staff", password="pass-12345", is_staff=True
        )
        self.club = Club.objects.create(name="Science Club")
        self.event = Event.objects.create(
            title="Science Expo",
            description="Annual science exhibition",
            event_type="club",
            club=self.club,
            date=date.today() + timedelta(days=14),
            created_by=self.creator,
        )

    def test_event_list_page_loads(self):
        # The public event list should render and include the created event.
        response = self.client.get(reverse("event-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "event_list.html")
        self.assertContains(response, "Science Expo")

    def test_event_detail_page_loads(self):
        # The detail page should display the selected event.
        response = self.client.get(reverse("event-detail", args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "event_detail.html")
        self.assertEqual(response.context["event"], self.event)

    def test_event_detail_returns_404_for_unknown_event(self):
        # A non-existent event ID should not produce a successful response.
        response = self.client.get(reverse("event-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_create_event_requires_login(self):
        # Anonymous users should be redirected to the login page.
        response = self.client.get(reverse("create-event"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_creator_can_create_event(self):
        # A logged-in user can submit a valid event; the view assigns created_by.
        self.client.login(username="creator", password="pass-12345")
        response = self.client.post(reverse("create-event"), {
            "title": "New Workshop",
            "description": "Workshop description",
            "event_type": "general",
            "date": (date.today() + timedelta(days=20)).isoformat(),
            "time": "",
            "location": "Room 101",
            "max_capacity": "",
            "is_online": "",
            "notice": "",
            "website": "",
            "facebook": "",
        })
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
        created_event = Event.objects.get(title="New Workshop")
        self.assertEqual(created_event.created_by, self.creator)

    def test_creator_can_update_event(self):
        # The event creator is allowed to update their own event.
        self.client.login(username="creator", password="pass-12345")
        response = self.client.post(
            reverse("update-event", args=[self.event.pk]),
            {
                "title": "Updated Science Expo",
                "description": self.event.description,
                "event_type": "club",
                "club": self.club.pk,
                "date": self.event.date.isoformat(),
                "time": "",
                "location": "",
                "max_capacity": "",
                "is_online": "",
                "notice": "",
                "website": "",
                "facebook": "",
            },
        )
        self.assertRedirects(response, reverse("event-detail", args=[self.event.pk]))
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Science Expo")

    def test_non_creator_cannot_update_event(self):
        # A regular user who did not create the event is redirected without changes.
        self.client.login(username="visitor", password="pass-12345")
        response = self.client.get(reverse("update-event", args=[self.event.pk]))
        self.assertRedirects(response, reverse("event-detail", args=[self.event.pk]))
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Science Expo")

    def test_staff_user_can_update_event(self):
        # Staff users are explicitly allowed by the update view's permission check.
        self.client.login(username="staff", password="pass-12345")
        response = self.client.get(reverse("update-event", args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_event.html")

    def test_creator_can_delete_event(self):
        # Deletion is performed with POST and removes the event record.
        self.client.login(username="creator", password="pass-12345")
        response = self.client.post(reverse("delete-event", args=[self.event.pk]))
        self.assertRedirects(response, reverse("event-list"))
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_non_creator_cannot_delete_event(self):
        # A non-creator cannot delete the event.
        self.client.login(username="visitor", password="pass-12345")
        response = self.client.post(reverse("delete-event", args=[self.event.pk]))
        self.assertRedirects(response, reverse("event-detail", args=[self.event.pk]))
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())

    def test_join_event_requires_login(self):
        # Joining is protected by login_required.
        response = self.client.get(reverse("join-event", args=[self.event.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_user_can_join_event(self):
        # A logged-in user should get one attendance record when joining.
        self.client.login(username="visitor", password="pass-12345")
        response = self.client.get(reverse("join-event", args=[self.event.pk]))
        self.assertRedirects(response, reverse("event-detail", args=[self.event.pk]))
        self.assertTrue(EventAttendance.objects.filter(
            event=self.event, user=self.other_user
        ).exists())

    def test_joining_twice_does_not_create_duplicate_attendance(self):
        # Repeating the join request should leave exactly one attendance record.
        self.client.login(username="visitor", password="pass-12345")
        url = reverse("join-event", args=[self.event.pk])
        self.client.get(url)
        self.client.get(url)
        self.assertEqual(
            EventAttendance.objects.filter(event=self.event, user=self.other_user).count(),
            1,
        )

    def test_user_can_leave_event(self):
        # A user with an attendance record can leave and remove that record.
        EventAttendance.objects.create(
            event=self.event, user=self.other_user, status="going"
        )
        self.client.login(username="visitor", password="pass-12345")
        response = self.client.get(reverse("leave-event", args=[self.event.pk]))
        self.assertRedirects(response, reverse("event-detail", args=[self.event.pk]))
        self.assertFalse(EventAttendance.objects.filter(
            event=self.event, user=self.other_user
        ).exists())
