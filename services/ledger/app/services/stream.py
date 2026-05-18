import json
import logging

from aiokafka import AIOKafkaProducer

from app.config import settings
from app.models.event import InferenceEvent

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


async def init_producer() -> None:
    global _producer
    try:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
            acks="all",
            enable_idempotence=True,
        )
        await _producer.start()
        logger.info("kafka producer initialised")
    except Exception:
        # Kafka is optional in local dev — log and continue
        logger.warning("kafka unavailable, event streaming disabled")
        _producer = None


async def close_producer() -> None:
    if _producer:
        await _producer.stop()


async def publish_event(event: InferenceEvent) -> None:
    if not _producer:
        return

    try:
        await _producer.send(
            settings.kafka_topic_events,
            value=event.model_dump(mode="json"),
            key=event.event_id.encode(),
        )
    except Exception:
        # Publishing failures must never block the write path
        logger.exception("failed to publish event to kafka", extra={"event_id": event.event_id})
