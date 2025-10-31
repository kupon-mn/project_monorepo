from fastapi import FastAPI
import httpx, os

CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8080")
app = FastAPI(title="BFF", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/bff/product-cards")
async def product_cards(ids: str = ""):
    id_list = [i for i in ids.split(",") if i.strip()]
    if not id_list:
        return {"items": []}
    results = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for pid in id_list:
            r = await client.get(f"{CATALOG_URL}/products/{pid}")
            if r.status_code == 200:
                p = r.json()
                results.append({
                    "id": p["id"],
                    "title": p["title"],
                    "price": p["price"],
                    "image_url": p.get("image_url"),
                    "summary": (p.get("description") or "")[:128]
                })
    return {"items": results}
