from os.path import join
from django.db import models
from django.conf import settings
from django.utils.timezone import now


# Create your models here.
class ModelInstance(models.Model):
    def path(self, file):
        return join(settings.ARTIFACTS_ROOT, str(self.name), file)

    name = models.CharField(max_length=50, unique=True)
    creation_date = models.DateTimeField(default=now)
    description = models.CharField(max_length=1024, null=True, blank=True)

    model = models.FileField(upload_to=path, max_length=255)
    scaler = models.FileField(upload_to=path, max_length=255)
    imputer = models.FileField(upload_to=path, max_length=255)
    anomaly_detector = models.FileField(upload_to=path, max_length=255)
    preprocessing_flow = models.FileField(default="", upload_to=path, max_length=255)

    def __str__(self):
        return self.name
