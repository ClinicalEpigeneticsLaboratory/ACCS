import json
from os.path import join

from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy

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


class SamplesList(LoginRequiredMixin, ListView):
    model = Sample
    template_name = "app/history.html"
    redirect_field_name = "accs-login"
    context_object_name = "samples"
    paginate_by = 3

    def get_queryset(self):
        return Sample.objects.filter(user=self.request.user).order_by("-creation_date")


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
            join(settings.TASKS_ROOT, str(context["object"].id), "pp.json")
        ).to_html()

        context["ap"] = read_json(
            join(settings.TASKS_ROOT, str(context["object"].id), "ap.json")
        ).to_html()

        with open(
            join(settings.TASKS_ROOT, str(context["object"].id), "predicted.json")
        ) as file:
            infer_from_idats = json.load(file)
            context["PredictedSex"] = infer_from_idats["PredictedSex"][0]
            context["Platform"] = infer_from_idats["Platform"][0]
        return context


class SampleSubmit(LoginRequiredMixin, CreateView):
    model = Sample
    template_name = "app/submit.html"
    redirect_field_name = "accs-history"
    fields = ["sample_name", "diagnosis", "age", "sex", "model", "grn_idat", "red_idat"]
    success_url = reverse_lazy("accs-history")

    def form_valid(self, form):
        sample = form.save(commit=False)
        sample.user = self.request.user
        sample.save()

        process_single_sample.delay_on_commit(sample.id, self.request.user.id)

        messages.success(
            self.request,
            f"New analysis has successfully started.",
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
