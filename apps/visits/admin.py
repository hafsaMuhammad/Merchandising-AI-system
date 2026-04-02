from django.contrib import admin
from .models import Visit, ShelfImage


class ShelfImageInline(admin.TabularInline):
    model = ShelfImage
    extra = 0
    readonly_fields = ["status", "task_id", "uploaded_at"]


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ["store", "agent", "status", "scheduled_date", "started_at", "completed_at"]
    list_filter = ["status", "scheduled_date"]
    search_fields = ["store__name", "agent__username"]
    inlines = [ShelfImageInline]
    date_hierarchy = "scheduled_date"


@admin.register(ShelfImage)
class ShelfImageAdmin(admin.ModelAdmin):
    list_display = ["visit", "section_label", "status", "uploaded_at"]
    list_filter = ["status"]
    readonly_fields = ["task_id", "uploaded_at"]
