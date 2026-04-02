from django.urls import path
from .views import (
    DetectionResultListView,
    DetectionReportListView,
    DetectionReportDetailView,
    RegenerateReportView,
)

urlpatterns = [
    path("images/<int:image_id>/results/", DetectionResultListView.as_view(), name="detection_results"),
    path("reports/", DetectionReportListView.as_view(), name="report_list"),
    path("reports/<int:pk>/", DetectionReportDetailView.as_view(), name="report_detail"),
    path("reports/regenerate/<int:visit_id>/", RegenerateReportView.as_view(), name="regenerate_report"),
]
