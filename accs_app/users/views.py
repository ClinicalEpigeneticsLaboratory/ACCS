from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    PasswordChangeForm,
)
from .models import Profile


# Create your views here.
@login_required
def profile(request):
    if request.method == "POST":
        user_update_form = UserUpdateForm(request.POST, instance=request.user)
        profile_update_form = ProfileUpdateForm(
            request.POST, instance=request.user.profile
        )

        if user_update_form.is_valid() and profile_update_form.is_valid():
            user_update_form.save()
            profile_update_form.save()

            messages.success(
                request,
                f"Account has been successfully updated.",
            )
            return redirect("accs-profile")

        else:
            messages.warning(request, "Please correct the form.")

    user_update_form = UserUpdateForm(instance=request.user)
    profile_update_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "title": "Profile",
        "user_update_form": user_update_form,
        "profile_update_form": profile_update_form,
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
            form.save()
            user_name = form.cleaned_data.get("username")
            institution_name = form.cleaned_data.get("institution")

            user = User.objects.get(username=user_name)
            user_profile = Profile.objects.create(
                user=user, institution=institution_name
            )
            user_profile.save()

            messages.success(
                request,
                f"Account has been successfully created for {user_name}! You're now able to sign in.",
            )
            return redirect("accs-login")

        else:
            messages.warning(request, "Please correct the form.")

    form = UserRegisterForm()
    return render(
        request, "users/register.html", {"form": form, "title": "Registration page"}
    )


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
