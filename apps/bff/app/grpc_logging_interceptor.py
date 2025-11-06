import logging
import grpc

logger = logging.getLogger("bff.grpc")


class LoggingClientInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        method = client_call_details.method
        logger.info("gRPC client call", extra={"method": method})
        try:
            response = await continuation(client_call_details, request)
            return response
        except grpc.aio.AioRpcError as e:
            logger.warning(
                "gRPC client error",
                extra={"method": method, "code": e.code().name, "details": e.details()},
            )
            raise
