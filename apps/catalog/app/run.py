import asyncio
import uvicorn
from .api.http import router as http_router
from fastapi import FastAPI
from .grpc.server import serve as grpc_serve

http_app = FastAPI(title="catalog-http", version="1.0.0")
http_app.include_router(http_router)

import logging, sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


async def main():
    # gRPC server
    grpc_task = asyncio.create_task(grpc_serve())

    # HTTP server
    config = uvicorn.Config(http_app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    http_task = asyncio.create_task(server.serve())

    await asyncio.gather(grpc_task, http_task)


if __name__ == "__main__":
    asyncio.run(main())
