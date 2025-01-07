import ast
import json
from os.path import join

from django.db.models import Q
from django.http import Http404
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.views.generic import DeleteView, DetailView, CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from plotly.io import read_json

from .tasks import process_single_sample
from .models import Sample, Document


# Create your views here.
def home(request):
    context = {
        "title": "Home",
        "document": Document.objects.filter(name="home-page").first(),
    }
    return render(request, "app/home.html", context)


def about(request):
    context = {
        "title": "About",
        "document": Document.objects.filter(name="about-page").first(),
    }
    return render(request, "app/about.html", context)


def legal_notice(request):
    context = {
        "title": "Legal notice",
        "document": Document.objects.filter(name="legal-notice").first(),
    }
    return render(request, "app/legal_notice.html", context)


@login_required(login_url="accs-login")
def task_status(request):
    samples = Sample.objects.filter(user=request.user)

    # Prepare the data to be returned
    data = []

    for sample in samples:
        # Get the status from the associated TaskResult
        if sample.task:
            status = sample.task.status if sample.task.status else "-"
            task_id = sample.task.id if sample.task.id else "-"

            task_content = ast.literal_eval(sample.task.result)
            anomaly = task_content.get("Anomaly_status", "-")
            prediction = task_content.get("Prediction", "-")
            confidence = task_content.get("Confidence")

            if confidence:
                confidence = round(confidence, 2)
            else:
                confidence = "-"

            # Add the sample name and task status to the data list
            data.append(
                {
                    "task_id": task_id,
                    "task_status": status,
                    "prediction": prediction,
                    "confidence": confidence,
                    "anomaly": anomaly,
                }
            )

    return JsonResponse(data, safe=False)


class SamplesList(LoginRequiredMixin, ListView):
    model = Sample
    template_name = "app/history.html"
    redirect_field_name = "accs-login"
    context_object_name = "samples"
    paginate_by = 3

    def get_queryset(self):
        samples = Sample.objects.filter(user=self.request.user).order_by(
            "-creation_date"
        )
        query = self.request.GET.get("q")
        if query:
            samples = samples.filter(
                Q(sample_name__icontains=query) | Q(diagnosis__icontains=query)
            )
        return samples


class SampleReport(LoginRequiredMixin, DetailView):
    model = Sample
    template_name = "app/report.html"
    redirect_field_name = "accs-login"
    context_object_name = "report"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Sample.objects.filter(Q(user=self.request.user) | Q(public=True))
        else:
            return Sample.objects.filter(public=True)

    def dispatch(self, request, *args, **kwargs):
        sample = self.get_object()

        if sample.public or request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404(
                "You do not have permission to view this report. "
                "Make sure that link is valid and sample is publicly available."
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["pp"] = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "results",
                "pp.json",
            )
        ).to_html()

        context["ap"] = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "results",
                "ap.json",
            )
        ).to_html()

        context["nf"] = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "results",
                "nanf.json",
            )
        ).to_html()

        context["cnvs"] = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "results",
                "cnvs.json",
            ),
            skip_invalid=True,
        ).to_html()

        with open(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "results",
                "results.json",
            )
        ) as file:
            predictions = json.load(file)
            context["Predicted_sex"] = predictions["Predicted_sex"][0]
            context["Predicted_platform"] = predictions["Predicted_platform"][0]

        return context


class SampleSubmit(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sample
    template_name = "app/submit.html"
    success_url = reverse_lazy("accs-history")
    fields = [
        "sample_name",
        "diagnosis",
        "age",
        "sex",
        "model",
        "grn_idat",
        "red_idat",
    ]
    success_message = ""

    def form_valid(self, form):
        sample = form.save(commit=False)
        sample.user = self.request.user
        sample.save()

        process_single_sample.delay_on_commit(sample.id, self.request.user.id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accs-history")

    def get_success_message(self, _):
        sample = self.object
        return f"Sample {sample.sample_name} has been successfully added to queue."


class SampleDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Sample
    template_name = "app/delete.html"
    success_message = ""

    def get_queryset(self):
        return Sample.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("accs-history")

    def get_success_message(self, _):
        # Access the instance of the object that was deleted
        sample = self.object  # `self.object` contains the deleted object
        return f"Sample {sample.sample_name} has been successfully deleted."


class SampleUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Sample
    template_name = "app/update.html"
    fields = ["sample_name", "diagnosis", "age", "sex", "public"]
    success_message = ""

    def get_queryset(self):
        return Sample.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("accs-history")

    def get_success_message(self, _):
        sample = self.object
        return f"Sample {sample.sample_name} has been successfully updated."
