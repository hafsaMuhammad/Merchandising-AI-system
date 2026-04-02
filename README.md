# Merchandising AI Demo Upgraded

This upgraded project mimics a large-scale system with multiple models, async tasks, and complex relationships.

Tech Stack:
- Django 4.2
- DRF
- Celery + RabbitMQ
- Pillow
- Docker

Features:
- 20+ dummy models with realistic relationships
- 5 dummy Celery tasks: AI detection, report generation, notifications, batch processing, session cleanup
- Multiple API endpoints (CRUD, filtering)
- Scalable workflow demonstration

Setup:
1. git clone <repo>
2. Create virtual env & activate
3. pip install -r requirements.txt
4. docker-compose up -d
5. python manage.py migrate
6. python manage.py runserver
7. celery -A merch_ai_demo worker --loglevel=info
