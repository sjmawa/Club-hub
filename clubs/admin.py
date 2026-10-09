from django.contrib import admin
from clubs.models import Club, ClubMembership, ClubRole
# Register your models here.
admin.site.register(Club)
admin.site.register(ClubMembership)
admin.site.register(ClubRole)