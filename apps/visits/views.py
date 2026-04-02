from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import Visit, ShelfImage
from .serializers import VisitSerializer, VisitDetailSerializer, ShelfImageSerializer


class VisitListCreateView(generics.ListCreateAPIView):
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "store", "agent", "scheduled_date"]
    search_fields = ["store__name", "agent__username"]
    ordering_fields = ["scheduled_date", "created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Visit.objects.select_related("agent", "store")
        # Field agents only see their own visits
        if user.role == "agent":
            return qs.filter(agent=user)
        return qs

    def perform_create(self, serializer):
        # Auto-assign agent if not admin
        if self.request.user.role == "agent":
            serializer.save(agent=self.request.user)
        else:
            serializer.save()


class VisitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VisitDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Visit.objects.prefetch_related("shelf_images__detections")
        if user.role == "agent":
            return qs.filter(agent=user)
        return qs


class StartVisitView(APIView):
    """Mark a visit as in progress."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        visit = Visit.objects.get(pk=pk, agent=request.user)
        visit.status = Visit.Status.IN_PROGRESS
        visit.started_at = timezone.now()
        visit.save()
        return Response(VisitSerializer(visit).data)


class CompleteVisitView(APIView):
    """Mark a visit as completed."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        visit = Visit.objects.get(pk=pk, agent=request.user)
        visit.status = Visit.Status.COMPLETED
        visit.completed_at = timezone.now()
        visit.save()
        return Response(VisitSerializer(visit).data)


class ShelfImageUploadView(generics.CreateAPIView):
    """Upload a shelf image — triggers async YOLO detection."""
    serializer_class = ShelfImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ShelfImageDetailView(generics.RetrieveAPIView):
    queryset = ShelfImage.objects.prefetch_related("detections")
    serializer_class = ShelfImageSerializer
    permission_classes = [permissions.IsAuthenticated]
