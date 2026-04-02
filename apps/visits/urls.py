from django.urls import path
from .views import (
    VisitListCreateView, VisitDetailView,
    StartVisitView, CompleteVisitView,
    ShelfImageUploadView, ShelfImageDetailView,
)

urlpatterns = [
    path("", VisitListCreateView.as_view(), name="visit_list"),
    path("<int:pk>/", VisitDetailView.as_view(), name="visit_detail"),
    path("<int:pk>/start/", StartVisitView.as_view(), name="visit_start"),
    path("<int:pk>/complete/", CompleteVisitView.as_view(), name="visit_complete"),
    path("images/upload/", ShelfImageUploadView.as_view(), name="image_upload"),
    path("images/<int:pk>/", ShelfImageDetailView.as_view(), name="image_detail"),
]
