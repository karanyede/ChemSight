"""API URL declarations."""
from django.urls import path

from . import views
from .views_auth import LoginView, RegisterView
from .views_report import DatasetReportView
from .views_upload import DatasetUploadView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("datasets/", views.DatasetListView.as_view(), name="dataset-list"),
    path("datasets/<int:pk>/", views.DatasetDetailView.as_view(), name="dataset-detail"),
    path("datasets/<int:pk>/summary/", views.DatasetSummaryView.as_view(), name="dataset-summary"),
    path("datasets/<int:pk>/records/", views.DatasetRecordsView.as_view(), name="dataset-records"),
    path("datasets/<int:pk>/report/", DatasetReportView.as_view(), name="dataset-report"),
    path("upload/", DatasetUploadView.as_view(), name="dataset-upload"),
    path("metrics/", views.MetricsView.as_view(), name="metrics"),
]
