from django.db import models
from apps.users.models import User
from apps.stores.models import Store


class Visit(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="visits")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="visits")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    scheduled_date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"Visit to {self.store.name} by {self.agent} on {self.scheduled_date}"


class ShelfImage(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="shelf_images")
    image = models.ImageField(upload_to="shelves/%Y/%m/%d/")
    section_label = models.CharField(max_length=100, blank=True, help_text="e.g. Aisle 3 - Top shelf")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=255, blank=True, help_text="Celery task ID")

    def __str__(self):
        return f"Image for {self.visit} — {self.section_label or 'unlabeled'}"
