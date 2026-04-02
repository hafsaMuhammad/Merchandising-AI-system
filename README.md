# 🛒 ShelfScan — Retail Shelf Monitoring System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)
![Celery](https://img.shields.io/badge/Celery-5.3-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A production-ready backend system for retail merchandising operations. Field agents visit stores, upload shelf images, and the system automatically detects products using **YOLOv8** — processing everything asynchronously via **Celery + RabbitMQ**.

---

## 📐 Architecture

```
┌──────────────┐     JWT Auth      ┌─────────────────────────┐
│  Mobile App  │ ────────────────► │                         │
│  (Agent)     │                   │   Django REST API        │
└──────────────┘                   │   (Gunicorn / runserver) │
                                   │                         │
┌──────────────┐   Admin Panel     │   ┌─────────────────┐   │
│   Browser    │ ────────────────► │   │  Django Admin   │   │
│  (Manager)   │                   │   └─────────────────┘   │
└──────────────┘                   └───────────┬─────────────┘
                                               │
                                    Upload Image & Dispatch Task
                                               │
                                               ▼
                                   ┌─────────────────────┐
                                   │   RabbitMQ Broker   │
                                   │   (detection queue) │
                                   └──────────┬──────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │   Celery Worker     │
                                   │                     │
                                   │  ┌───────────────┐  │
                                   │  │  YOLOv8 Model │  │
                                   │  │  (Ultralytics)│  │
                                   │  └───────────────┘  │
                                   └──────────┬──────────┘
                                              │
                                    Save DetectionResults
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │    PostgreSQL DB     │
                                   └─────────────────────┘
```

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.2 + Django REST Framework |
| Auth | JWT (SimpleJWT) |
| AI Detection | YOLOv8 (Ultralytics) + OpenCV |
| Task Queue | Celery 5.3 |
| Message Broker | RabbitMQ |
| Database | PostgreSQL 15 |
| Containerization | Docker + Docker Compose |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Testing | pytest + pytest-django |

---

## 📁 Project Structure

```
shelfscan/
├── config/                  # Django settings, URLs, WSGI
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── celery_app/              # Celery configuration
│   └── __init__.py
├── apps/
│   ├── users/               # Custom user model, JWT auth, roles
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── stores/              # Store & product management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── visits/              # Store visits & shelf image uploads
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   └── detection/           # YOLO integration, Celery tasks, reports
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       ├── yolo_service.py  # Core AI service wrapper
│       ├── tasks.py         # Celery async tasks
│       └── management/
│           └── commands/
│               └── seed_demo.py
├── tests/
│   └── test_detection.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Docker & Docker Compose installed
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/shelfscan.git
cd shelfscan
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env if needed — defaults work out of the box for local dev
```

### 3. Build and start all services

```bash
docker compose up --build
```

This starts:
- `web` — Django on http://localhost:8000
- `celery_worker` — processes detection tasks
- `celery_beat` — periodic task scheduler
- `rabbitmq` — message broker (management UI: http://localhost:15672)
- `db` — PostgreSQL

### 4. Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Seed demo data

```bash
docker compose exec web python manage.py seed_demo
```

This creates:
- **Admin:** `admin` / `admin123`
- **Agents:** `agent1`, `agent2`, `agent3` / `agent123`
- 3 stores, 6 products, sample visits

### 6. Access the system

| URL | Description |
|---|---|
| http://localhost:8000/admin/ | Django Admin Panel |
| http://localhost:8000/api/docs/ | Swagger API Docs |
| http://localhost:8000/api/redoc/ | ReDoc API Docs |
| http://localhost:15672 | RabbitMQ Dashboard |

---

## 🔑 API Overview

### Authentication

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "agent1",
  "password": "agent123"
}
```

**Response:**
```json
{
  "access": "<JWT_TOKEN>",
  "refresh": "<REFRESH_TOKEN>",
  "user": {
    "id": 2,
    "username": "agent1",
    "role": "agent"
  }
}
```

Use the token in subsequent requests:
```http
Authorization: Bearer <JWT_TOKEN>
```

---

### Core Endpoints

#### Stores
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/stores/` | List all stores |
| POST | `/api/v1/stores/` | Create store |
| GET | `/api/v1/stores/{id}/` | Store detail |
| GET | `/api/v1/stores/{id}/products/` | Products in store |

#### Visits
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/visits/` | List visits (agents see own only) |
| POST | `/api/v1/visits/` | Create visit |
| GET | `/api/v1/visits/{id}/` | Visit detail with images |
| POST | `/api/v1/visits/{id}/start/` | Mark visit started |
| POST | `/api/v1/visits/{id}/complete/` | Mark visit completed |

#### Image Upload (triggers YOLO)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/visits/images/upload/` | Upload shelf image → triggers async detection |
| GET | `/api/v1/visits/images/{id}/` | Image status + detection count |

#### Detection Results
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/detection/images/{id}/results/` | All detections for an image |
| GET | `/api/v1/detection/reports/` | All visit reports |
| GET | `/api/v1/detection/reports/{id}/` | Single visit report |

---

## 🔄 Detection Flow

```
1. Agent uploads shelf image via POST /api/v1/visits/images/upload/
        │
        ▼
2. ShelfImage saved to DB (status: "processing")
        │
        ▼
3. Celery task `run_yolo_detection` dispatched to RabbitMQ queue
        │
        ▼
4. Celery worker picks up task
        │
        ▼
5. YOLOv8 runs inference on the image
        │
        ▼
6. DetectionResult rows bulk-created in DB
        │
        ▼
7. ShelfImage status updated to "done"
        │
        ▼
8. `generate_visit_report` task triggered
        │
        ▼
9. DetectionReport aggregated (totals, confidence, unique products)
```

---

## 🧠 YOLO Integration

The `YOLOService` class in `apps/detection/yolo_service.py` wraps YOLOv8:

```python
from apps.detection.yolo_service import YOLOService

service = YOLOService()
detections = service.predict("/path/to/shelf.jpg")

# Returns:
# [
#   {"label": "cola_bottle", "confidence": 0.91, "bbox": {"x1": 0.1, "y1": 0.2, "x2": 0.4, "y2": 0.8}},
#   {"label": "chips_bag",   "confidence": 0.78, "bbox": {"x1": 0.5, "y1": 0.1, "x2": 0.9, "y2": 0.7}},
# ]
```

- The model is **lazy-loaded once per worker process** (singleton pattern) to avoid reloading on every task
- Bounding boxes are **normalized to 0–1** relative to image dimensions
- Confidence threshold is configurable via `YOLO_CONFIDENCE_THRESHOLD` in `.env`
- Default model: `yolov8n.pt` (nano — fast). Swap for `yolov8m.pt` or a custom-trained model

### Using a custom-trained model

If you have a custom YOLO model trained on your product dataset:

```env
# .env
YOLO_MODEL_PATH=/app/models/my_products.pt
```

---

## 👥 User Roles

| Role | Permissions |
|---|---|
| `admin` | Full access, create users, view all data |
| `manager` | View all visits and reports |
| `agent` | Own visits only, upload images |

---

## 🧪 Running Tests

```bash
docker compose exec web pytest tests/ -v
```

Tests cover:
- JWT login and token payload
- Role-based visit filtering
- YOLO service output formatting
- Celery task saving DetectionResults

---

## 🌱 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (required) | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `DB_NAME` | `shelfscan` | PostgreSQL database name |
| `DB_USER` | `shelfscan_user` | PostgreSQL user |
| `DB_PASSWORD` | `shelfscan_pass` | PostgreSQL password |
| `DB_HOST` | `db` | PostgreSQL host |
| `CELERY_BROKER_URL` | `amqp://guest:guest@rabbitmq:5672//` | RabbitMQ connection |
| `YOLO_MODEL_PATH` | `yolov8n.pt` | Path to YOLO model weights |
| `YOLO_CONFIDENCE_THRESHOLD` | `0.45` | Min confidence for detections |

---

## 📊 Django Admin

The admin panel at `/admin/` provides full management of:

- **Users** — create/edit agents and managers
- **Stores & Products** — catalog management
- **Visits** — view visit history with inline shelf images
- **Detection Results** — browse raw bounding box results
- **Detection Reports** — aggregated per-visit summaries

---

## 📈 Extending the System

Some directions to take this further:

- **Custom YOLO training** — train on your own product dataset using Ultralytics and swap the model path
- **Planogram compliance** — compare detected facings vs `StoreProduct.expected_facing`
- **Push notifications** — use Celery to alert managers when visits complete
- **Dashboard frontend** — connect a React/Vue frontend to the existing REST API
- **Export reports** — add a CSV/PDF export endpoint for visit reports

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙋 Author

Built as a portfolio project to demonstrate:
- Django REST Framework API design
- Async task processing with Celery + RabbitMQ
- Real AI model integration (YOLOv8)
- Docker-based deployment
- Role-based access control
- Clean project structure and test coverage
