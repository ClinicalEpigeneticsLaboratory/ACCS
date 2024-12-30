from django.views.generic.list import ListView
from .models import ModelInstance


class ModelsList(ListView):
    model = ModelInstance
    template_name = "models_collection/models_list.html"
    context_object_name = "models"

    def get_queryset(self):
        models = ModelInstance.objects.order_by("-creation_date")
        return models
