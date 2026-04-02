from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DetectionResult, DetectionReport
from .serializers import DetectionResultSerializer, DetectionReportSerializer
from .tasks import generate_visit_report


class DetectionResultListView(generics.ListAPIView):
    """List all detections for a specific shelf image."""
    serializer_class = DetectionResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DetectionResult.objects.filter(
            shelf_image_id=self.kwargs["image_id"]
        ).order_by("-confidence")


class DetectionReportListView(generics.ListAPIView):
    """List all visit detection reports."""
    serializer_class = DetectionReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["visit__store"]
    ordering_fields = ["generated_at", "total_detections"]

    def get_queryset(self):
        user = self.request.user
        qs = DetectionReport.objects.select_related("visit__store", "visit__agent")
        if user.role == "agent":
            return qs.filter(visit__agent=user)
        return qs


class DetectionReportDetailView(generics.RetrieveAPIView):
    """Retrieve a single visit report."""
    serializer_class = DetectionReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DetectionReport.objects.select_related("visit__store", "visit__agent")


class RegenerateReportView(APIView):
    """Manually trigger report regeneration for a visit."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, visit_id):
        generate_visit_report.delay(visit_id)
        return Response({"detail": f"Report regeneration queued for visit {visit_id}."})
