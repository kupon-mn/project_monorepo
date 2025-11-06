import asyncio, grpc
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal, engine
from ..infrastructure.repositories import SqlProductRepository, CachedProductRepository
from ..services.search_strategies import SearchStrategyFactory
from ..domain.models import Product
from .. import product_pb2, product_pb2_grpc

from .logging_interceptor import LoggingInterceptor


# Placeholder embedding fn (fast no-op). Replace with real async embedder.
async def embed_query(query: str) -> list[float]:
    return [0.0] * 1536


class CatalogService(product_pb2_grpc.CatalogServiceServicer):
    def __init__(self) -> None:
        pass

    async def _get_repo(self) -> CachedProductRepository:
        session: AsyncSession = AsyncSessionLocal()
        base_repo = SqlProductRepository(session)
        return CachedProductRepository(base_repo)

    async def GetProduct(self, request, context):
        repo = await self._get_repo()
        product = await repo.get(request.id)
        if not product:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Product not found")
        return self._to_message(product)

    async def BatchGetProducts(self, request, context):
        repo = await self._get_repo()
        products = await repo.batch_get(list(request.ids))
        return product_pb2.BatchGetProductsResponse(
            products=[self._to_message(p) for p in products]
        )

    async def SearchProducts(self, request, context):
        async with AsyncSessionLocal() as session:
            factory = SearchStrategyFactory(session, embed_query)
            strategy = factory.create(request.query)
            products = await strategy.search(
                session, request.query, request.limit or 20
            )
        return product_pb2.SearchProductsResponse(
            products=[self._to_message(p) for p in products]
        )

    def _to_message(self, p: Product) -> product_pb2.Product:
        return product_pb2.Product(
            id=p.id,
            title=p.title,
            description=p.description or "",
            price=p.price,
            currency=p.currency,
            image_url=p.image_url or "",
        )


async def serve() -> None:
    server = grpc.aio.server(
        interceptors=[LoggingInterceptor()],
        options=[
            ("grpc.keepalive_time_ms", 20000),
            ("grpc.keepalive_timeout_ms", 20000),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.max_concurrent_streams", 1000),
        ],
    )
    product_pb2_grpc.add_CatalogServiceServicer_to_server(CatalogService(), server)
    server.add_insecure_port("[::]:50051")  # Istio handles mTLS
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
