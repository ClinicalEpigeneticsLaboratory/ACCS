from os.path import join
import subprocess
import json

from uuid import uuid4
from celery import shared_task
from django.conf import settings
from django_celery_results.models import TaskResult

from .models import Sample


@shared_task(bind=True)
def process_single_sample(self, sample_id: uuid4, user_name: str) -> dict:
    sample = Sample.objects.get(id=sample_id)
    model_workflow = sample.model.name

    task = TaskResult.objects.get(
        task_id=self.request.id
    )  # self.request.id is coming from celery object as long as it is a method --> bind=True
    sample.task = task
    sample.save()

    workflow_directory = join(
        settings.MEDIA_ROOT,
        settings.ARTIFACTS_PATH,
        str(model_workflow),
    )
    task_directory = join(settings.MEDIA_ROOT, settings.TASKS_PATH, str(sample_id))

    subprocess.run(
        [
            "nextflow",
            "run",
            "workflow.nf",
            "--input",
            task_directory,
            "--work-dir",
            "/temp/work",
        ],
        shell=False,
        check=True,
        cwd=workflow_directory,
    )

    results_directory = join(task_directory, "results/")
    with open(join(results_directory, "predicted.json"), "r") as file:
        results = json.load(file)

    results["Sample_name"] = sample.sample_name
    results["User"] = user_name

    return results
