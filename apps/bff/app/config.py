from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "bff"
    catalog_grpc_target: str = "catalog.dev.svc.cluster.local:50051"

    class Config:
        env_prefix = "BFF_"


settings = Settings()
