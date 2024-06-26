# Generated by Django 5.0.4 on 2024-05-12 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_rename_sample_task_sample_id"),
        ("django_celery_results", "0011_taskresult_periodic_task_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="sample",
            name="task",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_celery_results.taskresult",
            ),
        ),
        migrations.DeleteModel(
            name="Task",
        ),
    ]
