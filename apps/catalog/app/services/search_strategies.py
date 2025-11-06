from abc import ABC, abstractmethod
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..domain.models import Product


class SearchStrategy(ABC):
    @abstractmethod
    async def search(
        self, session: AsyncSession, query: str, limit: int
    ) -> Sequence[Product]: ...


class KeywordSearchStrategy(SearchStrategy):
    async def search(
        self, session: AsyncSession, query: str, limit: int
    ) -> Sequence[Product]:
        stmt = text(
            """
            SELECT * FROM products
            WHERE title ILIKE :q OR description ILIKE :q
            ORDER BY id
            LIMIT :limit
        """
        )
        res = await session.execute(stmt, {"q": f"%{query}%", "limit": limit})
        return res.scalars().all()


class VectorSearchStrategy(SearchStrategy):
    def __init__(self, embedding_fn) -> None:
        self._embed = embedding_fn  # e.g. async call to embedding service

    async def search(
        self, session: AsyncSession, query: str, limit: int
    ) -> Sequence[Product]:
        vec = await self._embed(query)  # returns list[float] of length dim
        stmt = text(
            """
            SELECT * FROM products
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> :vec
            LIMIT :limit
        """
        )
        res = await session.execute(stmt, {"vec": vec, "limit": limit})
        return res.scalars().all()


class HybridSearchStrategy(SearchStrategy):
    """Composite: combines two strategies, merges results."""

    def __init__(self, primary: SearchStrategy, secondary: SearchStrategy) -> None:
        self._primary = primary
        self._secondary = secondary

    async def search(
        self, session: AsyncSession, query: str, limit: int
    ) -> Sequence[Product]:
        p = await self._primary.search(session, query, limit)
        s = await self._secondary.search(session, query, limit)
        seen = set()
        merged = []
        for item in list(p) + list(s):
            if item.id not in seen:
                seen.add(item.id)
                merged.append(item)
            if len(merged) >= limit:
                break
        return merged


class SearchStrategyFactory:
    def __init__(self, session: AsyncSession, embedding_fn=None) -> None:
        self._session = session
        self._embedding_fn = embedding_fn

    def create(self, query: str) -> SearchStrategy:
        # simple heuristic: short queries → hybrid, long queries → vector
        if self._embedding_fn:
            keyword = KeywordSearchStrategy()
            vector = VectorSearchStrategy(self._embedding_fn)
            return HybridSearchStrategy(keyword, vector)
        return KeywordSearchStrategy()
