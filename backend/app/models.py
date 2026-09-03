"""Central metadata registry used by Alembic and test database setup."""

from app.modules.channels.models import Channel
from app.modules.orders.models import Order, OrderItem
from app.modules.products.models import Product

__all__ = ["Channel", "Product", "Order", "OrderItem"]
