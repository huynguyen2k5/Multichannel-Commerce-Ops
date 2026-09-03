"""Product catalog definitions and master data."""

from app.modules.products.models import Product
from app.modules.products.service import ProductService, get_product_service

__all__ = [
    "Product",
    "ProductService",
    "get_product_service",
]
