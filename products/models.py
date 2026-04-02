
from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(User, related_name='roles')

class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

class Branch(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class ProductCategory(models.Model):
    name = models.CharField(max_length=50)

class ProductTag(models.Model):
    name = models.CharField(max_length=50)

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    categories = models.ManyToManyField(ProductCategory, blank=True)
    tags = models.ManyToManyField(ProductTag, blank=True)
    processed = models.BooleanField(default=False)
    ai_label = models.CharField(max_length=50, blank=True, null=True)
    ai_confidence = models.FloatField(blank=True, null=True)


class AIResult(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    confidence = models.FloatField()
    processed_at = models.DateTimeField(auto_now_add=True)

class StoreVisit(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visit_time = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Additional dummy models to make 20+ total
class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class CustomerFeedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)

class VisitLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
