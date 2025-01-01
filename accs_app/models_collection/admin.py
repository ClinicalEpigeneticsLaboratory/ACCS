from django.contrib import admin
from .models import ModelInstance


class ModelAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "creation_date", "description"]


# Register your models here.
admin.site.register(ModelInstance, ModelAdmin)
