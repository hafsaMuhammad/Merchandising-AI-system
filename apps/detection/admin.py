from django.contrib import admin
from .models import DetectionResult, DetectionReport


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ["shelf_image", "label", "confidence", "detected_at"]
    list_filter = ["label"]
    search_fields = ["label", "shelf_image__visit__store__name"]
    readonly_fields = ["detected_at"]


@admin.register(DetectionReport)
class DetectionReportAdmin(admin.ModelAdmin):
    list_display = [
        "visit", "total_images", "total_detections",
        "unique_products", "avg_confidence", "generated_at"
    ]
    readonly_fields = ["generated_at"]
