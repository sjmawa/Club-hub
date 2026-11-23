from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from clubs.models import Club
from events.models import Category, Event, EventAttendance


User = get_user_model()


class EventModelTests(TestCase):
    def setUp(self):
        # Create fresh test records; Django rolls them back after each test.
        self.user = User.objects.create_user(username="event_creator", password="test-pass-123")
        self.club = Club.objects.create(name="Programming Club")

    def test_event_can_be_created_with_valid_fields(self):
        # Verify the Event model stores its main fields and relationships.
        event = Event.objects.create(
            title="Python Workshop",
            description="A beginner workshop",
            event_type="club",
            club=self.club,
            date=date(2027, 1, 15),
            time=time(14, 30),
            created_by=self.user,
        )

        self.assertEqual(event.title, "Python Workshop")
        self.assertEqual(event.event_type, "club")
        self.assertEqual(event.club, self.club)
        self.assertEqual(event.created_by, self.user)
        self.assertEqual(event.date, date(2027, 1, 15))

    def test_general_event_string_representation_is_its_title(self):
        # General events have no club, so __str__ should return only the title.
        event = Event.objects.create(title="University Fair", date=date(2027, 2, 1))
        self.assertEqual(str(event), "University Fair")

    def test_club_event_string_representation_includes_club_name(self):
        # Club-hosted events include the related club name in __str__.
        event = Event.objects.create(
            title="Coding Contest",
            event_type="club",
            club=self.club,
            date=date(2027, 2, 1),
        )
        self.assertEqual(str(event), "Coding Contest (Programming Club)")

    def test_event_attendance_string_representation(self):
        # Verify attendance is connected to the expected user and event.
        event = Event.objects.create(title="Tech Talk", date=date(2027, 3, 1))
        attendance = EventAttendance.objects.create(
            event=event, user=self.user, status="going"
        )
        self.assertEqual(str(attendance), "event_creator - Tech Talk (going)")

    def test_event_attendance_has_valid_status_choices(self):
        # The model currently defines 'going' and 'interested' as valid statuses.
        valid_statuses = {choice[0] for choice in EventAttendance._meta.get_field("status").choices}
        self.assertEqual(valid_statuses, {"going", "interested"})

    def test_category_string_representation(self):
        # Category.__str__ should return its name.
        category = Category.objects.create(name="Technology")
        self.assertEqual(str(category), "Technology")
