
from celery import shared_task
import time
from .models import Product
from ai_model.dummy_ai_model import predict

@shared_task
def process_ai_detection(product_id):
    import os
    product = Product.objects.get(id=product_id)
    if product.image:
        image_path = product.image.path
        label, confidence = predict(image_path)
        product.processed = True
        product.ai_label = label
        product.ai_confidence = confidence
        product.save()
    return True
