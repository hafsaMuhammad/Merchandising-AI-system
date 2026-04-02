from rest_framework import generics, permissions
from .models import Store, Product, StoreProduct
from .serializers import StoreSerializer, ProductSerializer, StoreProductSerializer


class StoreListCreateView(generics.ListCreateAPIView):
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "code", "city"]
    filterset_fields = ["city", "region", "is_active"]


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "sku", "brand", "barcode"]
    filterset_fields = ["brand", "category", "is_active"]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class StoreProductListView(generics.ListCreateAPIView):
    serializer_class = StoreProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StoreProduct.objects.filter(store_id=self.kwargs["store_id"], is_active=True)

    def perform_create(self, serializer):
        serializer.save(store_id=self.kwargs["store_id"])
