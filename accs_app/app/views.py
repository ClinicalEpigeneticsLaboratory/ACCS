import ast
import json
from os.path import join

from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse

from django.views.generic import DeleteView, DetailView, CreateView, UpdateView
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
        "document": Document.objects.filter(name="legal-nothice").first(),
    }
    return render(request, "app/legal_notice.html", context)


def task_status(request):
    if request.user.is_authenticated:
        samples = Sample.objects.filter(user=request.user)

        # Prepare the data to be returned
        data = []

        for sample in samples:
            # Get the status from the associated TaskResult
            if sample.task:
                status = sample.task.status if sample.task.status else "-"
                task_id = sample.task.id if sample.task.id else "-"

                task_content = ast.literal_eval(sample.task.result)
                prediction = task_content.get("Prediction", "-")
                anomaly = task_content.get("Anomaly", "-")
                confidence = task_content.get("Confidence")

                if confidence:
                    confidence = round(max(confidence), 2)
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

    return JsonResponse({})


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
        return Sample.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["pp"] = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "pp.json",
            )
        ).to_html()

        context["ap"] = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "ap.json",
            )
        ).to_html()

        cnvs = read_json(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "cnvs.json",
            ),
            skip_invalid=True,
        )
        cnvs = cnvs.update_layout(
            title="Estimated CNVs",
            yaxis={"title": "log2 ratio of normalized intensities"},
        )
        context["cnvs"] = cnvs.to_html()

        with open(
            join(
                settings.MEDIA_ROOT,
                settings.TASKS_PATH,
                str(context["object"].id),
                "predicted.json",
            )
        ) as file:
            infer_from_idats = json.load(file)
            context["PredictedSex"] = infer_from_idats["PredictedSex"][0]
            context["Platform"] = infer_from_idats["Platform"][0]
        return context


class SampleSubmit(LoginRequiredMixin, CreateView):
    model = Sample
    template_name = "app/submit.html"
    redirect_field_name = "accs-history"
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

    def form_valid(self, form):
        sample = form.save(commit=False)
        sample.user = self.request.user
        sample.save()

        process_single_sample.delay_on_commit(sample.id, self.request.user.id)

        messages.success(
            self.request,
            f"New analysis has successfully added to queue.",
        )
        return super().form_valid(form)


class SampleDelete(LoginRequiredMixin, DeleteView):
    model = Sample
    template_name = "app/delete.html"
    redirect_field_name = "accs-login"

    def get_queryset(self):
        return Sample.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("accs-history")


class SampleUpdate(LoginRequiredMixin, UpdateView):
    model = Sample
    template_name = "app/update.html"
    redirect_field_name = "accs-login"
    fields = ["sample_name", "diagnosis", "age", "sex"]

    def get_queryset(self):
        return Sample.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("accs-history")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Sample {form.cleaned_data['sample_name']} has been updated successfully.",
        )
        return super().form_valid(form)
