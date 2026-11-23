from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from events.forms import EventForm
from events.models import Event
from events.models import EventAttendance as EventParticipant

def event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'event_list.html', {'events': events})

@login_required(login_url='sign-in')
def create_event(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Only staff members can create events.")
        return redirect('event-list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('event-detail', event.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()
    
    return render(request, 'create_event.html', {'event_form': form})

@login_required(login_url='sign-in')
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Allow creator OR staff
    if event.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You are not allowed to edit this event.")
        return redirect('event-detail', event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event-detail', event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'update_event.html', {
        'event_form': form,
        'event': event
    })

@login_required(login_url='sign-in')
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You are not allowed to delete this event.")
        return redirect('event-detail', event.id)

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('event-list')

    return redirect('event-detail', event.id)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    is_joined = False
    if request.user.is_authenticated:
        is_joined = EventParticipant.objects.filter(event=event, user=request.user).exists()

    participants = EventParticipant.objects.filter(event=event)

    return render(request, 'event_detail.html', {
        'event': event,
        'is_joined': is_joined,
        'participants': participants,
    })

@login_required(login_url='sign-in')
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participant, created = EventParticipant.objects.get_or_create(event=event, user=request.user)

    if created:
        messages.success(request, f"You have joined '{event.title}'!")
    else:
        messages.info(request, "You already joined this event.")
    return redirect('event-detail', event.id)

@login_required(login_url='sign-in')
def leave_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participant = EventParticipant.objects.filter(event=event, user=request.user)

    if participant.exists():
        participant.delete()
        messages.success(request, f"You have left '{event.title}'.")
    else:
        messages.info(request, "You are not part of this event.")
    return redirect('event-detail', event.id)

