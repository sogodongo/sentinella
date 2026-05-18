from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    sentinella_env: str = "development"
    opa_url: str = "http://localhost:8181"
    service_name: str = "sentinella-policy"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # How long to wait for OPA to respond before returning a fail-open decision
    opa_timeout_seconds: float = 2.0


settings = Settings()
