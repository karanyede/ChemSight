"""Middleware and logging helpers for request correlation."""
from __future__ import annotations

import threading
import uuid
from typing import Any

from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def _get_correlation_id() -> str:
    return getattr(_thread_locals, "correlation_id", "n/a")


def set_correlation_id(correlation_id: str) -> None:
    _thread_locals.correlation_id = correlation_id


class CorrelationIdMiddleware(MiddlewareMixin):
    """Attach a correlation ID to each request for observability."""

    header_name = "HTTP_X_CORRELATION_ID"

    def process_request(self, request):  # type: ignore[override]
        correlation_id = request.META.get(self.header_name) or str(uuid.uuid4())
        set_correlation_id(correlation_id)
        request.correlation_id = correlation_id

    def process_response(self, request, response):  # type: ignore[override]
        correlation_id = getattr(request, "correlation_id", _get_correlation_id())
        response["X-Correlation-ID"] = correlation_id
        return response

    def process_exception(self, request, exception):  # type: ignore[override]
        set_correlation_id(getattr(request, "correlation_id", str(uuid.uuid4())))


class LoggingCorrelationFilter:
    """Logging filter that injects correlation IDs."""

    def filter(self, record: Any) -> bool:  # pragma: no cover - trivial
        record.correlation_id = _get_correlation_id()
        return True
