import json
import logging
from typing import Any

import asyncpg

from app.config import settings
from app.models.event import InferenceEvent

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=5,
    )
    await _ensure_schema()
    logger.info("database pool initialised")


async def close_pool() -> None:
    if _pool:
        await _pool.close()


async def _ensure_schema() -> None:
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS inference_events (
                event_id    TEXT PRIMARY KEY,
                timestamp   TIMESTAMPTZ NOT NULL,
                model       TEXT NOT NULL,
                policy_decision TEXT NOT NULL,
                policy_reason   TEXT NOT NULL,
                caller_ip       TEXT,
                request_message_count INTEGER NOT NULL,
                metadata    JSONB NOT NULL DEFAULT '{}'
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_timestamp
            ON inference_events (timestamp DESC)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_model
            ON inference_events (model)
        """)


async def write_event(event: InferenceEvent) -> None:
    if not _pool:
        logger.warning("database pool not initialised, dropping event", extra={"event_id": event.event_id})
        return

    async with _pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO inference_events
                (event_id, timestamp, model, policy_decision, policy_reason,
                 caller_ip, request_message_count, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (event_id) DO NOTHING
        """,
            event.event_id,
            event.timestamp,
            event.model,
            event.policy_decision.value,
            event.policy_reason,
            event.caller_ip,
            event.request_message_count,
            json.dumps(event.metadata),
        )


async def list_events(limit: int = 100, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
    if not _pool:
        return [], 0

    async with _pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM inference_events
            ORDER BY timestamp DESC
            LIMIT $1 OFFSET $2
        """, limit, offset)

        total = await conn.fetchval("SELECT COUNT(*) FROM inference_events")

    return [dict(r) for r in rows], total
