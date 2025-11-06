from fastapi import Depends
from .grpc_catalog_client import get_catalog_stub
from . import product_pb2_grpc


async def catalog_stub_dep() -> product_pb2_grpc.CatalogServiceStub:
    return await get_catalog_stub()
