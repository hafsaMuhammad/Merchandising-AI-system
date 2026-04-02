from rest_framework import serializers
from .models import Store, Product, StoreProduct


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class StoreProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = StoreProduct
        fields = ["id", "store", "product", "product_name", "product_sku", "expected_facing", "is_active"]
