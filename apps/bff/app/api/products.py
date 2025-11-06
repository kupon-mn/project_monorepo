from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import grpc
from ..schemas import Product, ProductList
from .. import product_pb2, product_pb2_grpc
from ..dependencies import catalog_stub_dep

router = APIRouter()


@router.get("/api/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    stub: product_pb2_grpc.CatalogServiceStub = Depends(catalog_stub_dep),
):
    try:
        resp = await stub.GetProduct(
            product_pb2.GetProductRequest(id=product_id),
            timeout=0.2,
        )
    except grpc.aio.AioRpcError as e:
        code = e.code()
        if code == grpc.StatusCode.NOT_FOUND:
            # DB empty or product not present → 404, not “Catalog error”
            raise HTTPException(status_code=404, detail="Product not found")
        elif code in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
            raise HTTPException(status_code=503, detail="Catalog unavailable")
        else:
            raise HTTPException(
                status_code=502,
                detail=f"Catalog error ({code.name})",
            )
    # happy path
    return Product(
        id=resp.id,
        title=resp.title,
        description=resp.description,
        price=resp.price,
        currency=resp.currency,
        image_url=resp.image_url or None,
    )


@router.get("/api/products", response_model=ProductList)
async def batch_get_products(
    ids: List[str] = Query(..., min_length=1),
    stub: product_pb2_grpc.CatalogServiceStub = Depends(catalog_stub_dep),
):
    resp = await stub.BatchGetProducts(
        product_pb2.BatchGetProductsRequest(ids=ids),
        timeout=0.3,
    )
    items = [
        Product(
            id=p.id,
            title=p.title,
            description=p.description,
            price=p.price,
            currency=p.currency,
            image_url=p.image_url or None,
        )
        for p in resp.products
    ]
    return ProductList(items=items)


@router.get("/api/products/search", response_model=ProductList)
async def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    stub: product_pb2_grpc.CatalogServiceStub = Depends(catalog_stub_dep),
):
    resp = await stub.SearchProducts(
        product_pb2.SearchProductsRequest(query=q, limit=limit),
        timeout=0.4,
    )
    items = [
        Product(
            id=p.id,
            title=p.title,
            description=p.description,
            price=p.price,
            currency=p.currency,
            image_url=p.image_url or None,
        )
        for p in resp.products
    ]
    return ProductList(items=items)
