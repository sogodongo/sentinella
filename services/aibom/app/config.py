from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    sentinella_env: str = "development"
    service_name: str = "sentinella-aibom"
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "sentinella"
    minio_secret_key: str = "sentinella_dev"
    minio_bucket: str = "sentinella-bom"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"


settings = Settings()
