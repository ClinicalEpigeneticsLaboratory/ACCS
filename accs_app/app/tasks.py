from uuid import uuid4
from pathlib import Path
from django.conf import settings
from celery import shared_task
from django_celery_results.models import TaskResult

from .src.inference import Inference
from .models import Sample


@shared_task(bind=True)
def process_single_sample(self, sample_id: uuid4, user_name: str) -> dict:
    sample = Sample.objects.get(id=sample_id)
    model = sample.model

    task = TaskResult.objects.get(
        task_id=self.request.id
    )  # self.request.id is coming from celery object as long as it is a method --> bind=True

    sample.task = task
    sample.save()

    path_id = Path(sample.grn_idat.path).parent.parent.name
    inf = Inference(
        settings.ARTIFACTS_ROOT,
        model.model.path,
        model.scaler.path,
        model.imputer.path,
        model.anomaly_detector.path,
        model.preprocessing_flow.path,
        settings.TASKS_ROOT,
        path_id,
    )

    (
        prediction,
        confidence,
        confidence_status,
        classes,
        anomaly_status,
        anomaly_score,
        anomaly_t,
    ) = inf.start()

    result = {
        "Sample_name": sample.sample_name,
        "User": user_name,
        "Prediction": prediction,
        "Max_confidence": round(max(confidence), 2),
        "Confidence_status": confidence_status,
        "Confidence": confidence,
        "Classes": classes,
        "Anomaly": anomaly_status,
        "Anomaly_score": anomaly_score,
        "Anomaly_thresholds": anomaly_t,
    }

    return result
