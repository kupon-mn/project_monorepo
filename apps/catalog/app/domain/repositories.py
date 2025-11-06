from abc import ABC, abstractmethod
from typing import Sequence, Optional
from .models import Product


class ProductRepository(ABC):
    @abstractmethod
    async def get(self, product_id: str) -> Optional[Product]: ...
    @abstractmethod
    async def batch_get(self, ids: list[str]) -> Sequence[Product]: ...
    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> Sequence[Product]: ...
