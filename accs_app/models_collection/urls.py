from django.urls import path
from .views import ModelsList

urlpatterns = [
    path("models-collection/", ModelsList.as_view(), name="accs-models-collection"),
]
