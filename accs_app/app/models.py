import uuid
from os.path import join
from django.db import models
from django.utils.timezone import now
from django_celery_results.models import TaskResult
from django.core.validators import RegexValidator
from tinymce import models as tinymce_models

from models_collection.models import ModelInstance
from users.models import User


class Document(models.Model):
    name = models.SlugField(primary_key=True)
    creation_date = models.DateTimeField(default=now)
    content = tinymce_models.HTMLField(null=True, blank=True)


class Sex(models.TextChoices):
    Male = "Male"
    Female = "Female"


# Create your models here.
class Sample(models.Model):
    def file_path(self, file):
        return join("tasks", str(self.id), "idats/", file)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    public = models.BooleanField(
        default=False,
        help_text=f"If made public, the report will be accessible to anyone with the appropriate link.",
    )
    task = models.OneToOneField(
        TaskResult, null=True, blank=True, on_delete=models.CASCADE
    )

    model = models.ForeignKey(ModelInstance, null=True, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=now)

    sample_name = models.CharField(max_length=50)
    diagnosis = models.CharField(max_length=50)

    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField(choices=Sex.choices, max_length=7, blank=True, null=True)

    grn_idat = models.FileField(
        upload_to=file_path,
        validators=[
            RegexValidator(
                r".*_Grn.idat*",
                "Expected file suffix is _Grn.idat or _Grn.idat.gz",
                "iDAT error",
            )
        ],
    )
    red_idat = models.FileField(
        upload_to=file_path,
        validators=[
            RegexValidator(
                r".*_Red.idat*",
                "Expected file suffix is _Red.idat or _Red.idat.gz",
                "iDAT error",
            )
        ],
    )

    def __str__(self):
        return self.sample_name
