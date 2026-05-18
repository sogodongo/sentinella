from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    sentinella_env: str = "development"
    service_name: str = "sentinella-evals"
    ledger_service_url: str = "http://localhost:8082"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_events: str = "sentinella.inference.events"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # Toxicity check — extend with a real classifier in production
    toxicity_keywords: list[str] = [
        "kill", "harm", "exploit", "attack", "malware",
        "phishing", "abuse", "illegal",
    ]
    max_response_length: int = 8000


settings = Settings()
