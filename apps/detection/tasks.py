"""
Celery tasks for async YOLO detection.

Flow:
  1. ShelfImage uploaded via API
  2. run_yolo_detection task dispatched to 'detection' queue
  3. Worker loads YOLO, runs inference
  4. DetectionResult rows saved to DB
  5. ShelfImage status updated to DONE (or FAILED)
  6. generate_visit_report updates DetectionReport for the visit
"""

import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="detection",
)
def run_yolo_detection(self, shelf_image_id: int):
    """
    Main async task: run YOLO on a ShelfImage and persist results.
    Retries up to 3 times on failure with 30s delay.
    """
    from apps.visits.models import ShelfImage
    from apps.detection.models import DetectionResult
    from apps.detection.yolo_service import YOLOService

    try:
        image_obj = ShelfImage.objects.select_related("visit").get(pk=shelf_image_id)
        image_path = image_obj.image.path

        service = YOLOService()
        detections = service.predict(image_path)

        with transaction.atomic():
            # Clear old results if retrying
            DetectionResult.objects.filter(shelf_image=image_obj).delete()

            DetectionResult.objects.bulk_create([
                DetectionResult(
                    shelf_image=image_obj,
                    label=d["label"],
                    confidence=d["confidence"],
                    bbox_x1=d["bbox"]["x1"],
                    bbox_y1=d["bbox"]["y1"],
                    bbox_x2=d["bbox"]["x2"],
                    bbox_y2=d["bbox"]["y2"],
                )
                for d in detections
            ])

            image_obj.status = ShelfImage.Status.DONE
            image_obj.save(update_fields=["status"])

        logger.info(f"ShelfImage {shelf_image_id}: saved {len(detections)} detections.")

        # Trigger report update
        generate_visit_report.delay(image_obj.visit_id)

    except ShelfImage.DoesNotExist:
        logger.error(f"ShelfImage {shelf_image_id} not found.")
    except Exception as exc:
        logger.exception(f"Detection failed for ShelfImage {shelf_image_id}: {exc}")

        # Mark as failed before retry
        try:
            ShelfImage.objects.filter(pk=shelf_image_id).update(
                status=ShelfImage.Status.FAILED
            )
        except Exception:
            pass

        raise self.retry(exc=exc)


@shared_task(queue="detection")
def generate_visit_report(visit_id: int):
    """
    Recalculate and save a DetectionReport for a given visit.
    Called after each image is processed.
    """
    from apps.visits.models import Visit
    from apps.detection.models import DetectionResult, DetectionReport

    try:
        visit = Visit.objects.get(pk=visit_id)
        images = visit.shelf_images.filter(status="done")
        results = DetectionResult.objects.filter(shelf_image__in=images)

        total = results.count()
        unique = results.values("label").distinct().count()
        avg_conf = (
            sum(r.confidence for r in results) / total
            if total > 0 else 0.0
        )

        DetectionReport.objects.update_or_create(
            visit=visit,
            defaults={
                "total_images": images.count(),
                "total_detections": total,
                "unique_products": unique,
                "avg_confidence": round(avg_conf, 4),
            },
        )
        logger.info(f"Report updated for Visit {visit_id}.")

    except Visit.DoesNotExist:
        logger.error(f"Visit {visit_id} not found for report generation.")
