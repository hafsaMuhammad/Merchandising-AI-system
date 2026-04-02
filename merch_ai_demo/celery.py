
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merch_ai_demo.settings')
app = Celery('merch_ai_demo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
