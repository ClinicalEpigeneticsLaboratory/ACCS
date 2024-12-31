from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from .models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    acceptance = forms.BooleanField(
        required=True,
        label=mark_safe(
            'I accept the <a href="/legal-notice/" target="_blank">Terms and Conditions</a>'
        ),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        error_messages={
            "required": "You must accept the Terms and Conditions to register."
        },
    )

    class Meta:
        model = User
        fields = ["username", "email", "institution", "password1", "password2"]

    def clean_acceptance(self):
        acceptance = self.cleaned_data.get("acceptance")
        if not acceptance:
            raise ValidationError("You must accept the Terms and Conditions.")
        return acceptance


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(disabled=True)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "institution"]


class PasswordUpdateForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["password1", "password2"]
