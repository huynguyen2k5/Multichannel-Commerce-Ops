"""Central metadata registry used by Alembic and test database setup."""

from app.modules.channels.models import Channel
from app.modules.products.models import Product
from app.modules.orders.models import Order, OrderItem

__all__ = ["Channel", "Product", "Order", "OrderItem"]
