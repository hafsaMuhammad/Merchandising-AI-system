from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="unsafe-secret-key-for-dev")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "django_celery_results",
    "drf_spectacular",

    # Local apps
    "apps.users",
    "apps.stores",
    "apps.visits",
    "apps.detection",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="shelfscan"),
        "USER": config("DB_USER", default="shelfscan_user"),
        "PASSWORD": config("DB_PASSWORD", default="shelfscan_pass"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "users.User"

# JWT Authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# OpenAPI docs
SPECTACULAR_SETTINGS = {
    "TITLE": "ShelfScan API",
    "DESCRIPTION": "Retail shelf monitoring and AI detection system",
    "VERSION": "1.0.0",
}

# Celery
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="amqp://guest:guest@rabbitmq:5672//")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_ROUTES = {
    "apps.detection.tasks.*": {"queue": "detection"},
}

# Media
MEDIA_ROOT = config("MEDIA_ROOT", default=BASE_DIR / "media")
MEDIA_URL = config("MEDIA_URL", default="/media/")

# Static
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# CORS (for mobile/frontend)
CORS_ALLOW_ALL_ORIGINS = DEBUG

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# YOLO
YOLO_MODEL_PATH = config("YOLO_MODEL_PATH", default="yolov8n.pt")
YOLO_CONFIDENCE_THRESHOLD = config("YOLO_CONFIDENCE_THRESHOLD", default=0.45, cast=float)

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
