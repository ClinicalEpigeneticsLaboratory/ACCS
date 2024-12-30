from django.apps import AppConfig


class ModelsCollectionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "models_collection"

    def ready(self):
        import models_collection.signals
