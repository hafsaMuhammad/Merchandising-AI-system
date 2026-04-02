from django.contrib import admin
from .models import Store, Product, StoreProduct


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "city", "region", "is_active", "created_at"]
    list_filter = ["city", "region", "is_active"]
    search_fields = ["name", "code"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "brand", "category", "is_active"]
    list_filter = ["brand", "category", "is_active"]
    search_fields = ["name", "sku", "barcode"]


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ["store", "product", "expected_facing", "is_active"]
    list_filter = ["is_active"]
    autocomplete_fields = ["store", "product"]
