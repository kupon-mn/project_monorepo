from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()
_DB = {}

class Product(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    currency: str = "USD"
    category_id: Optional[str] = None
    image_url: Optional[str] = None

@router.get("", response_model=List[Product])
async def list_products(query: Optional[str] = None, limit: int = 50):
    items = list(_DB.values())
    if query:
        q = query.lower()
        items = [p for p in items if q in p.title.lower() or (p.description or "").lower().find(q) != -1]
    return items[:limit]

@router.get("/{pid}", response_model=Product)
async def get_product(pid: str):
    if pid not in _DB:
        raise HTTPException(status_code=404, detail="Product not found")
    return _DB[pid]

@router.post("", response_model=Product)
async def create_product(p: Product):
    if p.id in _DB:
        raise HTTPException(status_code=409, detail="Product already exists")
    _DB[p.id] = p
    return p

@router.post("/seed")
async def seed(n: int = 10):
    for _ in range(n):
        pid = f"sku-{random.randint(1000, 9999)}"
        _DB[pid] = Product(
            id=pid,
            title=f"Sample Product {pid}",
            description="Seeded product for groundwork demo",
            price=round(random.uniform(5.0, 200.0), 2),
            image_url=f"https://picsum.photos/seed/{pid}/400/300",
            category_id="demo"
        )
    return {"ok": True, "count": len(_DB)}
