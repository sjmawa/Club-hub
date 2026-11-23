from datetime import date, timedelta

from django.test import TestCase

from events.forms import EventForm


class EventDateValidationTests(TestCase):
    def _form_with_date(self, event_date):
        # Supply the minimum required EventForm data and vary only the date.
        return EventForm(data={
            "title": "Date Validation Test",
            "event_type": "general",
            "date": event_date,
        })

    def test_today_is_accepted_as_an_event_date(self):
        # The current implementation has no rule rejecting today's date.
        form = self._form_with_date(date.today().isoformat())
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_date_is_accepted(self):
        # A correctly formatted future date should pass DateField validation.
        future_date = (date.today() + timedelta(days=10)).isoformat()
        form = self._form_with_date(future_date)
        self.assertTrue(form.is_valid(), form.errors)

    def test_past_date_is_rejected(self):
        past_date = (date.today() - timedelta(days=1)).isoformat()
        form = self._form_with_date(past_date)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
        self.assertEqual(
            form.errors["date"],
            ["Event date cannot be in the past."],
        )

    def test_missing_date_is_rejected(self):
        # Event.date is required, so an empty date must fail form validation.
        form = self._form_with_date("")
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_malformed_date_is_rejected(self):
        # A value that is not a valid date must produce a date field error.
        form = self._form_with_date("32/99/not-a-date")
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
