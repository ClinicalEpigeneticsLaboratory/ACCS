from os.path import join
from shutil import rmtree

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.conf import settings

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .models import Sample


@receiver(post_delete, sender=Sample)
def delete_model_local_repo(sender, instance, **kwargs):
    sample_path = join(settings.MEDIA_ROOT, settings.TASKS_PATH, str(instance.id))
    rmtree(sample_path)


@receiver(post_save, sender=Sample)
def pull_model_repo(sender, instance, created, **kwargs):
    token = settings.SLACK_TOKEN

    if created and token:
        client = WebClient(token=token)
        try:
            client.chat_postMessage(
                channel="mbcc",
                text=f"New sample - {instance.sample_name} has been added to queue by {instance.user.username}.",
            )
        except SlackApiError as e:
            print(f"Error sending message: {e}")
