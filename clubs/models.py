from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone

class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='club_images/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    def __str__(self):
        return self.name
    
class ClubRole(models.Model):
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name="roles")
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.role_name} ({self.club.name})"


class ClubMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(ClubRole, on_delete=models.SET_NULL, null=True, blank=True) 
    joined_at = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'club')

