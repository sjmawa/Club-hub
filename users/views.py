from django.shortcuts import render,redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from users.forms import CustomRegisterForm,AssignRoleForm,CreateRoleForm
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
User= get_user_model()
def sign_up(request):
    if request.method == 'GET':
        form = CustomRegisterForm()
        # ensure CSRF cookie is set and log it for debugging
        token = get_token(request)
        print(f"CSRF token set on GET (get_token): {token}")
        return render(request, 'registration/sign_up.html', {'form': form})
    elif request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        # Debugging: log CSRF tokens from POST and cookies
        posted = request.POST.get('csrfmiddlewaretoken')
        cookie = request.COOKIES.get('csrftoken')
        print(f"CSRF token posted: {posted}")
        print(f"CSRF cookie: {cookie}")
        if form.is_valid():
            user = form.save(commit=False)
            print(user)  
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active= False 
            user.save()
            messages.success(request,"A confirmation email has been sent. Please check your inbox to activate your account.")
            return redirect('sign-in')
        else:
            print("Form is not valid")
            print(form.errors)
    return render(request, 'registration/sign_up.html', {'form':form})

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user= form.get_user()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'registration/login.html', {'form': form})

def activate_user(request, user_id, token):
    try:
        user= User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active= True
            user.save()
            messages.success(request, "Your account has been activated! Please log in.")
            return redirect('sign-in')
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect('sign-in')
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('sign-in')

@login_required
def sign_out(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')