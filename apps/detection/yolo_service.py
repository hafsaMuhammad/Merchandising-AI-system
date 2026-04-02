"""
YOLOService: wraps Ultralytics YOLOv8 for shelf image analysis.

Loads the model once at class level to avoid reloading on every task.
"""

import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

_model = None  # Module-level singleton


def get_model():
    """Lazy-load YOLO model (only once per worker process)."""
    global _model
    if _model is None:
        from ultralytics import YOLO
        model_path = settings.YOLO_MODEL_PATH
        logger.info(f"Loading YOLO model from: {model_path}")
        _model = YOLO(model_path)
    return _model


class YOLOService:
    """
    Runs YOLOv8 inference on a given image path.

    Returns a list of detection dicts:
        [
            {
                "label": "bottle",
                "confidence": 0.87,
                "bbox": {"x1": 0.1, "y1": 0.2, "x2": 0.4, "y2": 0.8}
            },
            ...
        ]
    """

    def __init__(self):
        self.model = get_model()
        self.confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD

    def predict(self, image_path: str) -> list[dict]:
        """
        Run detection on a single image.

        Args:
            image_path: Absolute path to the image file.

        Returns:
            List of detection result dicts.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Running YOLO on {path.name}")

        results = self.model.predict(
            source=str(path),
            conf=self.confidence_threshold,
            verbose=False,
        )

        detections = []
        for result in results:
            img_h, img_w = result.orig_shape[:2]

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = result.names[cls_id]

                detections.append({
                    "label": label,
                    "confidence": round(conf, 4),
                    "bbox": {
                        # Normalize to 0–1 range
                        "x1": round(x1 / img_w, 4),
                        "y1": round(y1 / img_h, 4),
                        "x2": round(x2 / img_w, 4),
                        "y2": round(y2 / img_h, 4),
                    },
                })

        logger.info(f"Detected {len(detections)} objects in {path.name}")
        return detections
