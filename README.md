


# Docker: Local Startup Guide

### 1. Prerequisites

- Docker & Docker Compose installed
- (Optional) `curl` for quick API checks

### 2. Project layout (relevant bits)

```text
.
├── apps
│   ├── bff
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── catalog
│       ├── app/
│       ├── alembic/
│       ├── alembic.ini
│       ├── Dockerfile
│       └── requirements.txt
└── docker-compose.yml
```

### Startup guide
docker compose up --build -d
docker compose exec catalog alembic upgrade head

### BFF logs (including gRPC client logs)
docker compose logs -f bff

### Catalog logs (gRPC server, DB, etc.)
docker compose logs -f catalog

# Overview
Details about project: https://github.com/kupon-mn/kupon-mn-info

This repo is a backend-only starter for a high-throughput microservices architecture with:

- **BFF service** (FastAPI, HTTP `/api/...`)
- **Catalog service** (FastAPI + gRPC)
- **Postgres** with **pgvector**
- **Async SQLAlchemy + asyncpg + Alembic**
- **gRPC** for BFF → Catalog communication
- **Basic logging & error handling** around gRPC

---

## Architecture Overview

### Services

- **BFF (`apps/bff`)**
  - FastAPI app, all HTTP endpoints under `/api/...`
  - Talks to Catalog **only via gRPC**

- **Catalog (`apps/catalog`)**
  - FastAPI (optional HTTP for `/api/health`)

- **Postgres**
  - Image: `ankane/pgvector:latest`

- **gRPC contract**
  - BFF holds a **single async gRPC channel** and stub for high throughput

---

## Tech Stack

- **Python 3.11**
- **FastAPI** + **Uvicorn**
- **gRPC (grpcio / grpcio-tools)**
- **SQLAlchemy 2 (async) + asyncpg**
- **pgvector** (via `ankane/pgvector` image)
- **Alembic** for migrations
- **Pydantic v2** + `pydantic-settings` for configuration
- **Docker Compose** for local dev

---


# Work in process
## Week 1
Added new:

- **BFF (`apps/bff`)**
  - Endpoints:
    - `GET /api/health`
    - `GET /api/products/{id}`
    - `GET /api/products?ids=...`
    - `GET /api/products/search?q=...&limit=...`
  - Maps gRPC errors to proper HTTP:
    - `NOT_FOUND` → `404 Product not found`
    - `UNAVAILABLE` / `DEADLINE_EXCEEDED` → `503 Catalog unavailable`
    - Other gRPC errors → `502 Catalog error (...)`

- **Catalog (`apps/catalog`)**
  - gRPC server implementing `CatalogService`:
    - `GetProduct`
    - `BatchGetProducts`
    - `SearchProducts`
  - Uses **Postgres + pgvector** via async SQLAlchemy (`postgresql+asyncpg://`)
  - Domain patterns:
    - **Repository** (`ProductRepository`) for DB access
    - **Decorator** (`CachedProductRepository`) for simple read-through caching
    - **SearchStrategyFactory** (Factory + Composite) to plug keyword/vector/hybrid search
    - **Domain events** (simple Observer) to hook product read events

- **Postgres**
  - DB: `catalog`
  - User: `app` / `app`
  - Alembic migration creates:
    - `products` table
    - `vector` extension
    - `embedding` column using `pgvector`

- **gRPC contract**
  - `product.proto` shared between BFF and Catalog
  - Python stubs generated as `product_pb2.py` and `product_pb2_grpc.py` inside each service’s `app/` package
  - BFF holds a **single async gRPC channel** and stub for high throughput
