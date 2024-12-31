from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .models import User


@receiver(post_save, sender=User)
def pull_model_repo(sender, instance, created, **kwargs):
    token = settings.SLACK_TOKEN

    if created and token:
        client = WebClient(token=token)
        try:
            client.chat_postMessage(
                channel="mbcc",
                text=f"New Account has been created: {instance.username} from {instance.institution}.",
            )
        except SlackApiError as e:
            print(f"Error sending message: {e}")
