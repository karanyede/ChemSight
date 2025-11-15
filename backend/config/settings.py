"""Django settings for Chemical Equipment Visualizer."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Core configuration -------------------------------------------------------

def _split_csv(raw: str, default: List[str]) -> List[str]:
    values = [entry.strip() for entry in raw.split(",") if entry.strip()]
    return values or default

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-development-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = _split_csv(
    os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"),
    ["localhost", "127.0.0.1"],
)

INTERNAL_IPS = _split_csv(
    os.getenv("DJANGO_INTERNAL_IPS", "127.0.0.1"),
    ["127.0.0.1"],
)

# Application definition ---------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "api",
]

MIDDLEWARE = [
    "api.middleware.CorrelationIdMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database -----------------------------------------------------------------

def _resolve_sqlite_path() -> Path:
    database_path = os.getenv("DJANGO_SQLITE_PATH")
    if database_path:
        return Path(database_path).expanduser().resolve()
    return BASE_DIR / "db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _resolve_sqlite_path(),
    }
}

# Password validation ------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization -----------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# Static & media -----------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

UPLOAD_ROOT = BASE_DIR / "uploads"
REPORT_ROOT = BASE_DIR / "reports"

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
REPORT_ROOT.mkdir(parents=True, exist_ok=True)

# File upload policy -------------------------------------------------------

FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("FILE_UPLOAD_MAX_MEMORY_SIZE", 5 * 1024 * 1024))
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("DATA_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024))
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", 25 * 1024 * 1024))
ALLOWED_UPLOAD_MIME_TYPES = _split_csv(
    os.getenv("ALLOWED_UPLOAD_MIME_TYPES", "text/csv,application/vnd.ms-excel"),
    ["text/csv", "application/vnd.ms-excel"],
)
CHUNK_SIZE = int(os.getenv("CSV_CHUNK_SIZE", 50_000))

# CORS / CSRF --------------------------------------------------------------

def _json_or_csv(env_key: str, default: List[str]) -> List[str]:
    raw = os.getenv(env_key)
    if not raw:
        return default
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item)] or default
    except json.JSONDecodeError:
        pass
    return _split_csv(raw, default)

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOWED_ORIGINS = _json_or_csv("CORS_ALLOWED_ORIGINS", _default_origins)
CSRF_TRUSTED_ORIGINS = _json_or_csv("CSRF_TRUSTED_ORIGINS", _default_origins)

CORS_ALLOW_HEADERS = _json_or_csv(
    "CORS_ALLOW_HEADERS",
    [
        "accept",
        "accept-language",
        "authorization",
        "content-type",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "x-correlation-id",
    ],
)
CORS_ALLOW_METHODS = _json_or_csv(
    "CORS_ALLOW_METHODS",
    ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
)
CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true" and not DEBUG
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "true").lower() == "true" and not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# REST framework -----------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("API_PAGE_SIZE", 25)),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("API_THROTTLE_ANON", "20/min"),
        "user": os.getenv("API_THROTTLE_USER", "200/day"),
        "upload": os.getenv("API_THROTTLE_UPLOAD", "5/hour"),
        "report": os.getenv("API_THROTTLE_REPORT", "10/hour"),
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# Logging ------------------------------------------------------------------

try:
    from .logging import LOGGING
except ImportError:  # pragma: no cover
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
    }

# Celery / async tasks placeholder -----------------------------------------

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

# Misc ---------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REPORT_FILENAME_TEMPLATE = os.getenv("REPORT_FILENAME_TEMPLATE", "dataset_{dataset_id}.pdf")
METRICS_NAMESPACE = os.getenv("METRICS_NAMESPACE", "chemical_visualizer")
