import grpc, asyncio
from .config import settings
from . import product_pb2_grpc
from .grpc_logging_interceptor import LoggingClientInterceptor

_channel = None
_stub = None
_lock = asyncio.Lock()


async def get_catalog_stub() -> product_pb2_grpc.CatalogServiceStub:
    global _channel, _stub
    async with _lock:
        if _stub is None:
            interceptors = [LoggingClientInterceptor()]
            _channel = grpc.aio.insecure_channel(
                settings.catalog_grpc_target,
                options=[("grpc.enable_retries", 1), ("grpc.keepalive_time_ms", 20000)],
                interceptors=interceptors,
            )
            _stub = product_pb2_grpc.CatalogServiceStub(_channel)
    return _stub
