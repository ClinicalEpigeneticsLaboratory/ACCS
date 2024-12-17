from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import (
    SamplesList,
    SampleReport,
    SampleDelete,
    SampleSubmit,
    SampleUpdate,
)
from . import views

urlpatterns = [
    path("", views.home, name="accs-home"),
    path("tasks-status/", views.task_status, name="celery-status"),
    path("about/", views.about, name="accs-about"),
    path("legal-notice/", views.legal_notice, name="accs-legal-notice"),
    path("submit/", SampleSubmit.as_view(), name="accs-submit"),
    path("history/", SamplesList.as_view(), name="accs-history"),
    path("report/<uuid:pk>/", SampleReport.as_view(), name="accs-report"),
    path("delete/<uuid:pk>/", SampleDelete.as_view(), name="accs-delete"),
    path("update/<uuid:pk>/", SampleUpdate.as_view(), name="accs-update"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
