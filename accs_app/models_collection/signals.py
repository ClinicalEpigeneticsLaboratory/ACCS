import subprocess
from os.path import join
from shutil import rmtree
from os.path import exists
from glob import glob

from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.dispatch import receiver
from .models import ModelInstance


@receiver(post_save, sender=ModelInstance)
def pull_model_repo(sender, instance, created, **kwargs):
    model_remote_repository = instance.remote_repository
    model_destination_path = join(
        settings.MEDIA_ROOT, settings.ARTIFACTS_PATH, str(instance.model_id)
    )
    if created:
        subprocess.run(
            ["git", "clone", model_remote_repository, model_destination_path],
            check=True,
            shell=False,
        )

        if exists(join(model_destination_path, "bin")):
            executables_py = glob(join(model_destination_path, "bin", "*.py"))
            executables_r = glob(join(model_destination_path, "bin", "*.R"))

            for file in [*executables_r, *executables_py]:
                subprocess.run(["chmod", "+x", file], check=True, shell=False)


@receiver(post_delete, sender=ModelInstance)
def delete_model_local_repo(sender, instance, **kwargs):
    model_destination_path = join(
        settings.MEDIA_ROOT, settings.ARTIFACTS_PATH, str(instance.model_id)
    )
    rmtree(model_destination_path)
