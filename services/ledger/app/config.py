from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    sentinella_env: str = "development"
    service_name: str = "sentinella-ledger"

    database_url: str = "postgresql://sentinella:sentinella_dev@localhost:5432/sentinella"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_events: str = "sentinella.inference.events"

    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # Maximum events returned per list query
    events_page_size: int = 100


settings = Settings()
