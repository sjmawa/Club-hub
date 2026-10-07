import re
from django.contrib.auth.models import Group,Permission
from django.contrib.auth import get_user_model
from django import forms
from core.forms import StyledFormMixin
from django.contrib.auth.forms import AuthenticationForm
from clubs.models import ClubRole as clubrole
from users.models import CustomUser
User= get_user_model()
class CustomRegisterForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password",widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField(label="Username")
    class Meta:
        model= CustomUser
        fields= ['username', 'first_name', 'last_name', 'email', 'password1', 'confirm_password','contact']
    def clean_username(self):
        username = self.cleaned_data.get('username')
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if not existing_user.is_active:
                existing_user.delete()
            else:
                raise forms.ValidationError("This username is already taken.")
        return username
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        return password1
    def clean_email(self):
        email= self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        # if not email.endswith('@gmail.com'):
        #     raise forms.ValidationError("Only Gmail addresses are allowed.")
        return email
    def clean_contact(self):
        contact = self.cleaned_data.get('contact')

        contact = contact.replace(' ', '').replace('-', '')

        if contact.startswith('+880'):
            contact= '0' + contact[4:]

        if not re.match(r'^01[3-9]\d{8}$', contact):
            raise forms.ValidationError("Enter a valid Bangladeshi phone number (e.g. 017XXXXXXXX or +88017XXXXXXXX).")

        return contact

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password1 and confirm_password and password1 != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data        
"""
custom login form
"""
class LoginForm(StyledFormMixin , AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AssignRoleForm(StyledFormMixin, forms.Form):
    role = forms.ModelChoiceField(
        queryset=clubrole.objects.all(),
        empty_label="Select a Role"
    )
class CreateRoleForm(StyledFormMixin, forms.ModelForm):
    permissions= forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget= forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permission'
    )
    class Meta:
        model = Group
        fields= ['name','permissions']