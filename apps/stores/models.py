from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["brand", "name"]

    def __str__(self):
        return f"{self.brand} - {self.name} ({self.sku})"


class StoreProduct(models.Model):
    """Products expected to be stocked at a specific store."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="store_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="store_assignments")
    expected_facing = models.PositiveIntegerField(default=1, help_text="Expected number of facings on shelf")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("store", "product")

    def __str__(self):
        return f"{self.store.code} — {self.product.sku}"
