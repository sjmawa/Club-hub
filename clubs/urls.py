from django.contrib import admin
from django.urls import path
from clubs.views import club_list, club_detail,delete_club,member_list,assign_role, create_club,join_club, add_role,cancel_request, update_club,pending_requests, approve_member,reject_member
urlpatterns = [
    path('', club_list, name='club-list'),
    path('<int:club_id>/', club_detail, name='club-detail'),
    path('create/', create_club, name='create-club'),
    #path('club/<int:club_id>/join/', join_club, name='join-club'),
    path('<int:club_id>/update/', update_club, name='update-club'),
    path('<int:club_id>/delete/', delete_club, name='delete-club'),
    #path('membership/confirm/<int:membership_id>/<str:token>/',confirm_membership, name='confirm-membership'),
    path('<int:club_id>/add-role/', add_role, name='add-role'),
    path('<int:club_id>/join/', join_club, name='join-club'),
    path('<int:club_id>/members/', member_list, name='club-members'),
    path('<int:club_id>/pending/', pending_requests, name='pending-requests'),
    path('approve/<int:membership_id>/',approve_member, name='approve-member'),
    path('reject/<int:membership_id>/',reject_member, name='reject-member'),
    path('membership/<int:membership_id>/cancel/', cancel_request, name='cancel-request'),
    path('<int:club_id>/assign-role/', assign_role, name='assign-role'),
]
