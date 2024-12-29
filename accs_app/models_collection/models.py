import requests
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError


def validate_no_slash(value):
    if "/" in value or "\\" in value:
        raise ValidationError("The name cannot contain '/' or '\\'.")


def validate_url_exists(value):
    try:
        response = requests.head(value, timeout=5)
        if response.status_code >= 400:
            raise ValidationError(f"The URL {value} does not exist or is unreachable.")

    except requests.RequestException as e:
        raise ValidationError(f"Error reaching the URL {value}: {e}")


def validate_github_repo(value):
    if not value.startswith("https://github.com/"):
        raise ValidationError(f"Remote repository is not GitHub repository.")


class ModelInstance(models.Model):
    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("UNKNOWN", "Unknown"),
    ]

    name = models.CharField(max_length=50, unique=True, validators=[validate_no_slash])
    creation_date = models.DateTimeField(default=now)
    description = models.CharField(max_length=1024, null=True, blank=True)
    model_remote_repository = models.CharField(
        max_length=256,
        default="",
        validators=[validate_url_exists, validate_github_repo],
    )

    def __str__(self):
        return self.name
