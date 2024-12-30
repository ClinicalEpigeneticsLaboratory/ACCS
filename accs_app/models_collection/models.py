import requests
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


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
        raise ValidationError("Remote repository is not a GitHub repository.")

    # Check if the repository contains a `workflow.nf` file
    try:
        # Convert the GitHub URL to the raw content URL for the file
        repo_url_parts = value.rstrip("/").split("/")
        if len(repo_url_parts) < 5:
            raise ValidationError("The provided GitHub URL is invalid.")

        # Assuming the repository's default branch is 'main'
        file_url = f"https://raw.githubusercontent.com/{'/'.join(repo_url_parts[3:])}/main/workflow.nf"

        response = requests.head(file_url, timeout=5)
        if response.status_code != 200:
            raise ValidationError(
                f"The repository does not contain a 'workflow.nf' file at {file_url}."
            )

    except requests.RequestException as e:
        raise ValidationError(f"Error reaching the repository or file: {e}")


class ModelInstance(models.Model):
    MODEL_TYPE = [
        ("CLASSIFIER", "Classifier"),
        ("REGRESSOR", "Regressor"),
        ("OTHER", "Other"),
    ]

    METRIC_TYPE = [
        ("BACC", "BACC"),
        ("ACC", "ACC"),
        ("MAE", "MAE"),
        ("MSE", "MSE"),
        ("R2", "R2"),
        ("OTHER", "Other"),
    ]

    name = models.CharField(max_length=50, unique=True, validators=[validate_no_slash])
    creation_date = models.DateTimeField(default=now)

    description = models.CharField(max_length=1024, null=False, default="")
    model_type = models.CharField(
        max_length=15, choices=MODEL_TYPE, null=False, default="CLASSIFIER"
    )
    evaluation_metric_type = models.CharField(
        max_length=15, choices=METRIC_TYPE, null=False, default="BACC"
    )
    evaluation_metric = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)], null=False, default=0.0
    )
    remote_repository = models.CharField(
        max_length=256,
        default="",
        validators=[validate_url_exists, validate_github_repo],
        null=False,
    )

    def __str__(self):
        return self.name
