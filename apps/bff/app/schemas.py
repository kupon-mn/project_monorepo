from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class Product(BaseModel):
    id: str
    title: str
    description: str
    price: float
    currency: str
    image_url: Optional[HttpUrl] = None


class ProductList(BaseModel):
    items: List[Product]
