"""Safe structured request logging."""

import json
import logging
import time
from collections.abc import Mapping


class JsonFormatter(logging.Formatter):
    """Format allowlisted fields as one JSON object per log line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        fields = getattr(record, "fields", None)
        if isinstance(fields, Mapping):
            payload.update(fields)
        return json.dumps(payload, sort_keys=True)


def configure_logging() -> None:
    """Install safe JSON logging once for the application."""
    root = logging.getLogger("guardrail_rag")
    if root.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def request_fields(
    request_id: str, method: str, path: str, status: int, started: float
) -> dict[str, object]:
    """Return safe request fields; never include query, body, or headers."""
    return {
        "request_id": request_id,
        "method": method,
        "path": path,
        "status": status,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
    }
