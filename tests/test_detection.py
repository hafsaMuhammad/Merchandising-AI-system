"""
Tests for ShelfScan detection pipeline.

Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

User = get_user_model()


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", password="adminpass", email="admin@test.com"
    )


@pytest.fixture
def agent_user(db):
    return User.objects.create_user(
        username="agent1", password="agentpass",
        email="agent@test.com", role="agent"
    )


@pytest.fixture
def store(db):
    from apps.stores.models import Store
    return Store.objects.create(
        name="Test Supermarket", code="TSM001",
        address="123 Main St", city="Cairo"
    )


@pytest.fixture
def visit(db, agent_user, store):
    from apps.visits.models import Visit
    from datetime import date
    return Visit.objects.create(
        agent=agent_user, store=store,
        status=Visit.Status.IN_PROGRESS,
        scheduled_date=date.today()
    )


# ─── Auth Tests ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_returns_jwt(client, agent_user):
    response = client.post("/api/v1/auth/login/", {
        "username": "agent1", "password": "agentpass"
    }, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert data["user"]["role"] == "agent"


@pytest.mark.django_db
def test_me_endpoint(client, agent_user):
    client.force_login(agent_user)
    from rest_framework.test import APIClient
    api = APIClient()
    api.force_authenticate(user=agent_user)
    response = api.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.data["username"] == "agent1"


# ─── Store Tests ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_store_list(store):
    from rest_framework.test import APIClient
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.create_user("u", "p@p.com", "pass")
    api = APIClient()
    api.force_authenticate(user=user)
    response = api.get("/api/v1/stores/")
    assert response.status_code == 200
    assert response.data["count"] >= 1


# ─── Visit Tests ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_agent_sees_only_own_visits(visit, agent_user, store, db):
    from apps.visits.models import Visit
    from django.contrib.auth import get_user_model
    from datetime import date
    other = get_user_model().objects.create_user("other", "o@o.com", "pass", role="agent")
    Visit.objects.create(agent=other, store=store, scheduled_date=date.today())

    from rest_framework.test import APIClient
    api = APIClient()
    api.force_authenticate(user=agent_user)
    response = api.get("/api/v1/visits/")
    assert response.status_code == 200
    for v in response.data["results"]:
        assert v["agent"] == agent_user.id


# ─── YOLO Service Tests ───────────────────────────────────────────────────────

def test_yolo_service_formats_output():
    """Test that YOLOService correctly formats YOLO output."""
    mock_box = MagicMock()
    mock_box.xyxy = [MagicMock()]
    mock_box.xyxy[0].tolist.return_value = [100, 50, 300, 200]
    mock_box.conf = [MagicMock()]
    mock_box.conf[0].__float__ = lambda self: 0.87
    mock_box.cls = [MagicMock()]
    mock_box.cls[0].__int__ = lambda self: 0

    mock_result = MagicMock()
    mock_result.orig_shape = (400, 640)
    mock_result.boxes = [mock_box]
    mock_result.names = {0: "bottle"}

    with patch("apps.detection.yolo_service.get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.predict.return_value = [mock_result]
        mock_get_model.return_value = mock_model

        from apps.detection.yolo_service import YOLOService
        with patch("apps.detection.yolo_service.settings") as mock_settings:
            mock_settings.YOLO_MODEL_PATH = "yolov8n.pt"
            mock_settings.YOLO_CONFIDENCE_THRESHOLD = 0.45

            service = YOLOService()
            with patch("pathlib.Path.exists", return_value=True):
                results = service.predict("/fake/image.jpg")

    assert len(results) == 1
    assert results[0]["label"] == "bottle"
    assert "bbox" in results[0]
    assert all(k in results[0]["bbox"] for k in ["x1", "y1", "x2", "y2"])


# ─── Detection Task Tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
def test_detection_task_saves_results(visit):
    from apps.visits.models import ShelfImage
    from apps.detection.models import DetectionResult
    import tempfile, os
    from PIL import Image as PILImage

    # Create a real tiny image file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(f.name)
        tmp_path = f.name

    shelf_image = ShelfImage.objects.create(
        visit=visit, section_label="Test Aisle", status=ShelfImage.Status.PENDING
    )
    shelf_image.image.name = tmp_path

    mock_detections = [
        {"label": "cola", "confidence": 0.91, "bbox": {"x1": 0.1, "y1": 0.1, "x2": 0.4, "y2": 0.5}},
        {"label": "juice", "confidence": 0.75, "bbox": {"x1": 0.5, "y1": 0.1, "x2": 0.8, "y2": 0.5}},
    ]

    with patch("apps.detection.tasks.YOLOService") as MockYOLO:
        MockYOLO.return_value.predict.return_value = mock_detections
        with patch("apps.detection.tasks.generate_visit_report.delay"):
            from apps.detection.tasks import run_yolo_detection
            run_yolo_detection(shelf_image.id)

    shelf_image.refresh_from_db()
    assert shelf_image.status == ShelfImage.Status.DONE
    assert DetectionResult.objects.filter(shelf_image=shelf_image).count() == 2

    os.unlink(tmp_path)
