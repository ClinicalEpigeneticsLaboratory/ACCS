from django.contrib import admin
from .models import Sample


class SampleAdmin(admin.ModelAdmin):
    list_display = ["sample_name", "user", "creation_date", "task"]


# Register your models here.
admin.site.register(Sample, SampleAdmin)
