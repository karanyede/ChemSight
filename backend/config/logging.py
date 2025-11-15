"""Central logging configuration with correlation identifiers."""
from __future__ import annotations

from typing import Any, Dict

from django.utils.log import DEFAULT_LOGGING

_default_request_logger = (
    DEFAULT_LOGGING.get("loggers", {}).get(
        "django.request",
        {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    )
)

LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s] (%(correlation_id)s) %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(correlation_id)s",
        },
    },
    "filters": {
        "correlation": {
            "()": "api.middleware.LoggingCorrelationFilter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["correlation"],
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    "django.request": _default_request_logger,
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "api": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
