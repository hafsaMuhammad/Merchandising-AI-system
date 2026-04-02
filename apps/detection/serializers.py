from rest_framework import serializers
from .models import DetectionResult, DetectionReport


class BBoxSerializer(serializers.Serializer):
    x1 = serializers.FloatField()
    y1 = serializers.FloatField()
    x2 = serializers.FloatField()
    y2 = serializers.FloatField()


class DetectionResultSerializer(serializers.ModelSerializer):
    bbox = BBoxSerializer(read_only=True)

    class Meta:
        model = DetectionResult
        fields = ["id", "shelf_image", "label", "confidence", "bbox", "detected_at"]


class DetectionReportSerializer(serializers.ModelSerializer):
    visit_id = serializers.IntegerField(source="visit.id", read_only=True)
    store_name = serializers.CharField(source="visit.store.name", read_only=True)
    agent_name = serializers.CharField(source="visit.agent.get_full_name", read_only=True)

    class Meta:
        model = DetectionReport
        fields = [
            "id", "visit_id", "store_name", "agent_name",
            "total_images", "total_detections", "unique_products",
            "avg_confidence", "generated_at",
        ]
