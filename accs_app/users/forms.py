from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    institution = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "institution", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(disabled=True)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email"]


class PasswordUpdateForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["password1", "password2"]


class ProfileUpdateForm(forms.ModelForm):
    institution = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Profile
        fields = ["institution"]
