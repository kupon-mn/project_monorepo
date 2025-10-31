from fastapi import FastAPI
from .routers import products
app = FastAPI(title="Catalog", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(products.router, prefix="/products", tags=["products"])
