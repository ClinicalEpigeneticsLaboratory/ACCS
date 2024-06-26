# Generated by Django 5.0.4 on 2024-05-13 09:26

import django.utils.timezone
import models_collection.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ModelInstance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("description", models.CharField(blank=True, null=True)),
                (
                    "model",
                    models.FileField(
                        upload_to=models_collection.models.ModelInstance.path
                    ),
                ),
                (
                    "scaler",
                    models.FileField(
                        upload_to=models_collection.models.ModelInstance.path
                    ),
                ),
                (
                    "imputer",
                    models.FileField(
                        upload_to=models_collection.models.ModelInstance.path
                    ),
                ),
                (
                    "anomaly_detector",
                    models.FileField(
                        upload_to=models_collection.models.ModelInstance.path
                    ),
                ),
            ],
        ),
    ]
