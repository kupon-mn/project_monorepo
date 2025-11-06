from typing import Sequence, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from ..domain.models import Product
from ..domain.repositories import ProductRepository
from ..domain.events import domain_events


class SqlProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, product_id: str) -> Optional[Product]:
        stmt = select(Product).where(Product.id == product_id)
        res = await self._session.execute(stmt)
        product = res.scalar_one_or_none()
        if product:
            domain_events.publish("product_read", {"id": product.id})
        return product

    async def batch_get(self, ids: list[str]) -> Sequence[Product]:
        if not ids:
            return []
        stmt = select(Product).where(Product.id.in_(ids))
        res = await self._session.execute(stmt)
        products = res.scalars().all()
        for p in products:
            domain_events.publish("product_read", {"id": p.id})
        return products

    async def search(self, query: str, limit: int = 20) -> Sequence[Product]:
        # Simple ILIKE search; hybrid/vector added via strategy factory (below)
        stmt = select(Product).where(Product.title.ilike(f"%{query}%")).limit(limit)
        res = await self._session.execute(stmt)
        products = res.scalars().all()
        for p in products:
            domain_events.publish("product_read", {"id": p.id})
        return products


# Decorator pattern – e.g. simple read-through cache (in-memory)
class CachedProductRepository(ProductRepository):
    def __init__(self, inner: ProductRepository) -> None:
        self._inner = inner
        self._cache: dict[str, Product] = {}

    async def get(self, product_id: str) -> Optional[Product]:
        if product_id in self._cache:
            return self._cache[product_id]
        p = await self._inner.get(product_id)
        if p:
            self._cache[product_id] = p
        return p

    async def batch_get(self, ids: list[str]) -> Sequence[Product]:
        result: list[Product] = []
        missing: list[str] = []
        for pid in ids:
            if pid in self._cache:
                result.append(self._cache[pid])
            else:
                missing.append(pid)
        if missing:
            fetched = await self._inner.batch_get(missing)
            for p in fetched:
                self._cache[p.id] = p
            result.extend(fetched)
        return result

    async def search(self, query: str, limit: int = 20) -> Sequence[Product]:
        # let inner handle; caching full searches is often less useful
        return await self._inner.search(query, limit)
