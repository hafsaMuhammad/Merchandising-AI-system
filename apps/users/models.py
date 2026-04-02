from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        AGENT = "agent", "Field Agent"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AGENT)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_field_agent(self):
        return self.role == self.Role.AGENT

    @property
    def is_manager(self):
        return self.role in [self.Role.MANAGER, self.Role.ADMIN]
