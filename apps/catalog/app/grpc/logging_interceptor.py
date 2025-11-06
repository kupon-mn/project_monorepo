import logging
import grpc
from grpc.aio import ServerInterceptor

logger = logging.getLogger("catalog.grpc")


class LoggingInterceptor(ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        method = (
            handler_call_details.method
        )  # e.g. /catalog.v1.CatalogService/GetProduct
        logger.info("gRPC request started", extra={"method": method})
        try:
            handler = await continuation(handler_call_details)
            return handler
        except Exception:
            logger.exception("gRPC request failed", extra={"method": method})
            raise
