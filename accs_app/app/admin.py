from django.contrib import admin
from .models import Sample, Document


class SampleAdmin(admin.ModelAdmin):
    list_display = ["pk", "sample_name", "user", "creation_date", "task"]


class DocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "creation_date", "content"]


# Register your models here.
admin.site.register(Sample, SampleAdmin)
admin.site.register(Document, DocumentAdmin)
