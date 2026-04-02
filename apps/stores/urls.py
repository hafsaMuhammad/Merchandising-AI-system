from django.urls import path
from .views import (
    StoreListCreateView, StoreDetailView,
    ProductListCreateView, ProductDetailView,
    StoreProductListView,
)

urlpatterns = [
    path("", StoreListCreateView.as_view(), name="store_list"),
    path("<int:pk>/", StoreDetailView.as_view(), name="store_detail"),
    path("<int:store_id>/products/", StoreProductListView.as_view(), name="store_products"),
    path("products/", ProductListCreateView.as_view(), name="product_list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
]
