from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.shared.errors import NotFoundError


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def get_by_sku(self, sku: str) -> Product:
        product = await self._repository.get_by_sku(sku)
        if product is None:
            raise NotFoundError(
                "PRODUCT_NOT_FOUND",
                f"Product SKU '{sku}' does not exist",
                details={"sku": sku},
            )
        return product
