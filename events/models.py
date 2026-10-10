from django.db import models
from django.conf import settings
from django.utils import timezone
from clubs.models import Club

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('general', 'Hosted by University'),
        ('club', 'Hosted by a Club'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='general')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True, related_name="events")
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,verbose_name="Event Date")
    created_at = models.DateTimeField(default=timezone.now,verbose_name="Event Date")
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    max_capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited capacity")
    is_online = models.BooleanField(default=False)
    notice = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        if self.club:
            return f"{self.title} ({self.club.name})"
        return self.title
    
class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('going','Going'),('interested','Interested')])
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name