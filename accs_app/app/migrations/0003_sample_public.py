# Generated by Django 5.1.4 on 2025-01-07 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
