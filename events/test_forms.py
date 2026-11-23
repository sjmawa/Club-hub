from datetime import date, timedelta

from django.test import TestCase

from clubs.models import Club
from events.forms import EventForm


class EventFormTests(TestCase):
    def setUp(self):
        # EventForm requires a valid event type, title, and date.
        self.club = Club.objects.create(name="Robotics Club")
        self.valid_data = {
            "title": "Robotics Exhibition",
            "description": "Student robotics projects",
            "event_type": "club",
            "club": self.club.pk,
            "date": (date.today() + timedelta(days=7)).isoformat(),
            "time": "10:30",
            "location": "Engineering Building",
            "max_capacity": "50",
            "is_online": "",
            "notice": "",
            "website": "",
            "facebook": "",
        }

    def test_form_accepts_valid_event_data(self):
        # A complete, valid set of form data should pass validation.
        form = EventForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_missing_required_title(self):
        # The title field is required by the Event model/form.
        data = self.valid_data.copy()
        data["title"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_rejects_missing_required_date(self):
        # The date field is required and cannot be left blank.
        data = self.valid_data.copy()
        data["date"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_form_rejects_invalid_date_input(self):
        # DateField should reject text that cannot be interpreted as a date.
        data = self.valid_data.copy()
        data["date"] = "not-a-date"
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_form_rejects_invalid_event_type(self):
        # event_type must match one of the model's declared choices.
        data = self.valid_data.copy()
        data["event_type"] = "university-wide"
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("event_type", form.errors)

    def test_optional_fields_can_be_left_blank(self):
        # Description, time, location, capacity, and links are optional.
        data = self.valid_data.copy()
        data.update({
            "description": "",
            "time": "",
            "location": "",
            "max_capacity": "",
            "website": "",
            "facebook": "",
        })
        form = EventForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
