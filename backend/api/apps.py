from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self) -> None:  # pragma: no cover - Django lifecycle hook
        from . import signals  # noqa: F401
