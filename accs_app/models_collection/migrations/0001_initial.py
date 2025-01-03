# Generated by Django 5.1.4 on 2025-01-01 12:06

import django.core.validators
import django.utils.timezone
import models_collection.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelInstance',
            fields=[
                ('model_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True, validators=[models_collection.models.validate_no_slash])),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.CharField(default='', max_length=1024)),
                ('model_type', models.CharField(choices=[('CLASSIFIER', 'Classifier'), ('REGRESSOR', 'Regressor'), ('OTHER', 'Other')], default='CLASSIFIER', max_length=15)),
                ('evaluation_metric_type', models.CharField(choices=[('BACC', 'BACC'), ('ACC', 'ACC'), ('MAE', 'MAE'), ('MSE', 'MSE'), ('R2', 'R2'), ('OTHER', 'Other')], default='BACC', max_length=15)),
                ('evaluation_metric', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('remote_repository', models.CharField(default='', max_length=256, validators=[models_collection.models.validate_url_exists, models_collection.models.validate_github_repo])),
            ],
        ),
    ]
