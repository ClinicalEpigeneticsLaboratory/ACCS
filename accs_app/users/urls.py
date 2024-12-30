from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="accs-register"),
    path("profile/", views.profile_update, name="accs-profile"),
    path("update-password/", views.password_update, name="accs-update-password"),
    path(
        "password-reset/",
        views.ResetPasswordView.as_view(),
        name="accs-reset-password",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="accs-password-reset-confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
