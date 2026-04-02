from rest_framework import serializers
from .models import Visit, ShelfImage
from apps.detection.tasks import run_yolo_detection


class ShelfImageSerializer(serializers.ModelSerializer):
    detection_count = serializers.SerializerMethodField()

    class Meta:
        model = ShelfImage
        fields = ["id", "visit", "image", "section_label", "status", "uploaded_at", "task_id", "detection_count"]
        read_only_fields = ["status", "task_id", "uploaded_at"]

    def get_detection_count(self, obj):
        return obj.detections.count()

    def create(self, validated_data):
        image = super().create(validated_data)
        # Dispatch async YOLO task after upload
        task = run_yolo_detection.apply_async(args=[image.id], queue="detection")
        image.task_id = task.id
        image.status = ShelfImage.Status.PROCESSING
        image.save(update_fields=["task_id", "status"])
        return image


class VisitSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source="agent.get_full_name", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            "id", "agent", "agent_name", "store", "store_name",
            "status", "scheduled_date", "started_at", "completed_at",
            "notes", "image_count", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_image_count(self, obj):
        return obj.shelf_images.count()


class VisitDetailSerializer(VisitSerializer):
    shelf_images = ShelfImageSerializer(many=True, read_only=True)

    class Meta(VisitSerializer.Meta):
        fields = VisitSerializer.Meta.fields + ["shelf_images"]
