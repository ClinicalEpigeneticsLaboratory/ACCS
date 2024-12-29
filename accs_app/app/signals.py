from os.path import join
from shutil import rmtree

from django.db.models.signals import post_delete
from django.conf import settings
from django.dispatch import receiver
from .models import Sample


@receiver(post_delete, sender=Sample)
def delete_model_local_repo(sender, instance, **kwargs):
    sample_path = join(settings.MEDIA_ROOT, settings.TASKS_PATH, str(instance.id))
    rmtree(sample_path)
