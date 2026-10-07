from django.contrib import admin
from django.urls import path
from users.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('activate/<int:user_id>/<str:token>/', activate_user, name='activate_user'),
    path('sign-out/', sign_out, name='sign-out'),
]
