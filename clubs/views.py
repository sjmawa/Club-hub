from django.shortcuts import HttpResponse, render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from clubs.models import Club, ClubRole, ClubMembership
from events.models import Event
from clubs.forms import ClubForm, ClubRoleForm
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator

def club_list(request):
    clubs = Club.objects.all()
    return render(request, 'club_list.html', {'clubs': clubs})

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    is_member = False
    is_pending = False
    membership_id = None 
    if request.user.is_authenticated:
        membership = ClubMembership.objects.filter(user=request.user,club=club).first()
        if membership:
            membership_id = membership.id 
            if membership.confirmed:
                is_member = True
            else:
                is_pending = True
    members = ClubMembership.objects.filter(club=club,confirmed=True)
    roles = ClubRole.objects.filter(club=club)
    events = Event.objects.filter(club=club).order_by('-date')
    committee = members.filter(role__isnull=False).select_related('user', 'role')

    return render(request, 'club_detail.html', {
        'club': club,
        'members': members,
        'roles': roles,
        'is_member': is_member,
        'is_pending': is_pending,
        'events': events,
        'committee': committee,
        'membership_id': membership_id
    })
@login_required(login_url='sign-in')
def create_club(request):
    if request.method == 'POST':
        club_form = ClubForm(request.POST, request.FILES)
        if club_form.is_valid():
            club = club_form.save()
            # Automatically add the creator as a member
            ClubMembership.objects.create(user=request.user, club=club)
            messages.success(request, 'Club created successfully!')
            return redirect('club-list')
    else:
        club_form = ClubForm()
    return render(request, 'create_club.html', {'club_form': club_form})

def join_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    membership, created = ClubMembership.objects.get_or_create(
        user=request.user,
        club=club,
        defaults={'confirmed': False}
    )

    if not created:
        if membership.confirmed:
            messages.info(request, "You are already a confirmed member of this club.")
        else:
            messages.info(request, "You already requested to join. Awaiting approval.")
        return redirect('club-detail', club_id)

    messages.success(request, "Your request to join the club has been submitted.")
    return redirect('club-detail', club_id)

def pending_requests(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    # Replace with your actual executive role logic
    # Example: only Executive Committee members may approve
    if not request.user.is_staff:
        return redirect('club-detail', club_id)

    pending = ClubMembership.objects.filter(club=club, confirmed=False)
    return render(request, 'pending_request.html', {
        'club': club,
        'pending': pending
    })

def approve_member(request, membership_id):
    membership = get_object_or_404(ClubMembership, id=membership_id)
    membership.confirmed = True
    membership.save()
    messages.success(request, f"{membership.user.username} has been approved!")
    return redirect('pending-requests', membership.club.id)

def reject_member(request, membership_id):
    membership = get_object_or_404(ClubMembership, id=membership_id)
    club_id = membership.club.id
    membership.delete()
    messages.warning(request, "Membership request rejected.")
    return redirect('pending-requests', club_id)

def cancel_request(request, membership_id):
    membership = get_object_or_404(ClubMembership, id=membership_id)

    if request.user != membership.user:
        messages.error(request, "You are not authorized to cancel this request.")
        return redirect('club-detail', membership.club.id)

    club_id = membership.club.id
    membership.delete()

    messages.success(request, "Your join request has been canceled.")
    return redirect('club-detail', club_id)

@login_required(login_url='sign-in')
def update_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    if not request.user.is_superuser and not club.memberships.filter(user=request.user, role__role_name="President").exists():
        messages.error(request, "You are not authorized to update this club.")
        return redirect('club-detail', club_id=club.id)

    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, f"{club.name} updated successfully!")
            return redirect('club-detail', club_id=club.id)
    else:
        form = ClubForm(instance=club)

    return render(request, 'update_club.html', {'club_form': form, 'club': club})
@login_required
def delete_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    # Permission rules:
    # 2. Superuser (site admin)
    # 3. Staff (moderators/admin panel access)
    if (request.user.is_superuser and not request.user.is_staff):
        messages.error(request, "You do not have permission to delete this club.")
        return redirect('club-detail', club_id=club.id)

    if request.method == "POST":
        club.delete()
        messages.success(request, "Club deleted successfully!")
        return redirect('club-list')

    return render(request, "delete_club_confirm.html", {"club": club})

@login_required(login_url='sign-in')
def assign_role(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    members = ClubMembership.objects.filter(club=club, confirmed=True)
    roles = ClubRole.objects.filter(club=club)

    if request.method == 'POST':
        member_id = request.POST.get('member')
        role_id = request.POST.get('role')

        member = get_object_or_404(ClubMembership, id=member_id, club=club)
        role = get_object_or_404(ClubRole, id=role_id, club=club)

        member.role = role
        member.save()
        messages.success(request, f"{member.user.username} has been assigned as {role.role_name}.")
        return redirect('club-detail', club_id=club.id)

    return render(request, 'assign_role.html', {
        'club': club,
        'members': members,
        'roles': roles
    })

@login_required(login_url='sign-in')
def add_role(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    # Optional: restrict to club creator or superuser
    if not request.user.is_superuser and not club.memberships.filter(user=request.user, role__role_name="President").exists():
        messages.error(request, "You are not authorized to add roles.")
        return redirect('club-detail', club_id=club.id)

    if request.method == 'POST':
        form = ClubRoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.club = club
            role.save()
            messages.success(request, f"Role '{role.role_name}' added successfully!")
            return redirect('assign-role', club_id=club.id)
    else:
        form = ClubRoleForm()

    return render(request, 'add_role.html', {'form': form, 'club': club})

@login_required(login_url='sign-in')
def member_list(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    members = ClubMembership.objects.filter(club=club, confirmed=True)

    return render(request, "member_list.html", {
        "club": club,
        "members": members,
    })

