# Generated by Django 5.0.4 on 2024-05-12 13:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_alter_sample_creation_date"),
        ("django_celery_results", "0011_taskresult_periodic_task_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sample",
            name="task",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="django_celery_results.taskresult",
            ),
        ),
    ]
