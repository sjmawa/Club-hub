import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q

from clubs.models import ClubRole
from core.forms import StyledFormMixin

User = get_user_model()


class CustomRegisterForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'confirm_password', 'contact']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True  # blank=True on the model by default

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if not contact:
            return contact

        contact = contact.replace(' ', '').replace('-', '')
        if contact.startswith('+880'):
            contact = '0' + contact[4:]

        if not re.match(r'^01[3-9]\d{8}$', contact):
            raise forms.ValidationError(
                "Enter a valid Bangladeshi phone number (e.g. 017XXXXXXXX or +88017XXXXXXXX)."
            )
        return contact

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        confirm = cleaned_data.get("confirm_password")

        if password1 and confirm:
            if password1 != confirm:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                try:
                    validate_password(password1)
                except ValidationError as e:
                    self.add_error('password1', e)

        # Only clear out stale unverified accounts once everything else is valid
        if not self.errors:
            User.objects.filter(is_active=False).filter(
                Q(username=cleaned_data['username']) |
                Q(email__iexact=cleaned_data['email'])
            ).delete()

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class AssignRoleForm(StyledFormMixin, forms.Form):
    role = forms.ModelChoiceField(
        queryset=ClubRole.objects.all(),
        empty_label="Select a Role",
    )


class CreateRoleForm(StyledFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permission',
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']