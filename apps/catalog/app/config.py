from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "catalog"
    db_url: AnyUrl = "postgresql+asyncpg://app:app@postgres:5432/catalog"
    pgvector_dim: int = 1536

    class Config:
        env_prefix = "CATALOG_"


settings = Settings()
