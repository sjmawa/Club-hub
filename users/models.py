from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username 