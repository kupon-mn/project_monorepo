from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Text
from pgvector.sqlalchemy import Vector
from ..db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        Vector(dim=1536), nullable=True
    )
