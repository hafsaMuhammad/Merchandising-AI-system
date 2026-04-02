from django.db import models
from apps.visits.models import ShelfImage


class DetectionResult(models.Model):
    """One bounding box / detected object from a shelf image."""
    shelf_image = models.ForeignKey(ShelfImage, on_delete=models.CASCADE, related_name="detections")

    label = models.CharField(max_length=200)
    confidence = models.FloatField()

    # Bounding box (normalized 0–1 relative to image size)
    bbox_x1 = models.FloatField()
    bbox_y1 = models.FloatField()
    bbox_x2 = models.FloatField()
    bbox_y2 = models.FloatField()

    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-confidence"]

    def __str__(self):
        return f"{self.label} ({self.confidence:.0%}) on image {self.shelf_image_id}"

    @property
    def bbox(self):
        return {
            "x1": self.bbox_x1,
            "y1": self.bbox_y1,
            "x2": self.bbox_x2,
            "y2": self.bbox_y2,
        }


class DetectionReport(models.Model):
    """Aggregated detection summary per visit."""
    visit = models.OneToOneField("visits.Visit", on_delete=models.CASCADE, related_name="detection_report")
    total_images = models.PositiveIntegerField(default=0)
    total_detections = models.PositiveIntegerField(default=0)
    unique_products = models.PositiveIntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)
    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for Visit #{self.visit_id}"
