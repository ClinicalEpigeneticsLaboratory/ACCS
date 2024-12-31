from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView

from .models import User
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    PasswordChangeForm,
)


# Create your views here.
@login_required
def profile_update(request):
    if request.method == "POST":
        user_update_form = UserUpdateForm(request.POST, instance=request.user)

        if user_update_form.is_valid():
            user_update_form.save()

            messages.success(
                request,
                f"Account has been successfully updated.",
            )
            return redirect("accs-profile")

        else:
            messages.warning(
                request,
                f"Ensure that the username adheres to the specified rules and that the passwords match.",
            )
    else:
        user_update_form = UserUpdateForm(instance=request.user)

    context = {
        "title": "Profile",
        "user_update_form": user_update_form,
    }

    return render(request, "users/profile.html", context)


@login_required
def password_update(request):
    if request.method == "POST":
        password_update_form = PasswordChangeForm(request.user, request.POST)

        if password_update_form.is_valid():
            user = password_update_form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                f"Password has been successfully updated.",
            )
            return redirect("accs-home")

        else:
            messages.warning(request, "Please correct the form.")
    else:
        password_update_form = PasswordChangeForm(request.user)

    context = {
        "title": "Update password",
        "password_update_form": password_update_form,
    }

    return render(request, "users/password_update.html", context)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Save the user to the database
            form.save()

            # Display success message
            user_name = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Account has been successfully created for {user_name}! You're now able to sign in.",
            )
            return redirect("accs-login")
        else:
            # If the form is invalid, display a warning message
            messages.warning(
                request, "Something went wrong, follow the rules and try again."
            )
    else:
        form = UserRegisterForm()

    return render(
        request, "users/register.html", {"form": form, "title": "Registration page"}
    )


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    redirect_field_name = "accs-login"
    template_name = "users/delete.html"
    success_message = "The account has been deleted successfully."
    success_url = reverse_lazy("accs-home")

    def get_object(self, queryset=None):
        return self.request.user


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"

    success_message = (
        "We've emailed you instructions for setting your password, "
        "If you don't receive an email, please make sure you've entered the address you registered with, "
        "and check your spam folder."
    )

    success_url = reverse_lazy("accs-home")


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
