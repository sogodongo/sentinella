import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# OPA policy path for inference governance decisions.
# Maps to policies/rego/inference/authz.rego in the monorepo.
_POLICY_PATH = "v1/data/sentinella/inference/allow"


async def evaluate(input_document: dict[str, Any]) -> dict[str, Any]:
    """
    Submit an input document to OPA and return the decision result.

    OPA's REST API expects: {"input": <your_input>}
    and returns: {"result": <policy_output>}

    On timeout or connection failure we fail open in development and
    fail closed in production. The gateway applies the same logic for
    defence in depth.
    """
    payload = {"input": input_document}

    try:
        async with httpx.AsyncClient(timeout=settings.opa_timeout_seconds) as client:
            resp = await client.post(
                f"{settings.opa_url}/{_POLICY_PATH}",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            result = data.get("result", {})
            return {
                "allowed": result.get("allow", False),
                "reason": result.get("reason", "no_reason_provided"),
                "evaluated_rules": result.get("evaluated_rules", []),
            }

    except httpx.TimeoutException:
        logger.warning("OPA request timed out", extra={"path": _POLICY_PATH})
        return _fail_open_or_closed("opa_timeout")

    except httpx.HTTPStatusError as exc:
        logger.error("OPA returned error status", extra={"status": exc.response.status_code})
        return _fail_open_or_closed("opa_http_error")

    except httpx.ConnectError:
        logger.error("OPA unreachable", extra={"url": settings.opa_url})
        return _fail_open_or_closed("opa_unreachable")


def _fail_open_or_closed(reason: str) -> dict[str, Any]:
    allow = settings.sentinella_env == "development"
    return {
        "allowed": allow,
        "reason": reason,
        "evaluated_rules": [],
    }
