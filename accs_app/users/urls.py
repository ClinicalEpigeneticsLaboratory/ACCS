from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="accs-register"),
    path("profile/", views.profile, name="accs-profile"),
    path("update-password/", views.password_update, name="accs-update-password"),
]
