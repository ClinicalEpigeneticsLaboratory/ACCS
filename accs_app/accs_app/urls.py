"""
URL configuration for accs_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.app, name='app')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='app')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('accs/', include('accs.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("", include("users.urls")),
    path("", include("models_collection.urls")),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="accs-login",
    ),
    path(
        "logout/",
        auth_views.logout_then_login,
        name="accs-logout",
    ),
]
