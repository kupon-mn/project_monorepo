from fastapi import FastAPI
from .api import products

app = FastAPI(title="BFF", version="1.0.0")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


app.include_router(products.router)
