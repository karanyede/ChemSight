"""Database models for the analytics backend."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.db import models


User = get_user_model()

dataset_storage = FileSystemStorage(location=getattr(settings, "UPLOAD_ROOT", "uploads"))
report_storage = FileSystemStorage(location=getattr(settings, "REPORT_ROOT", "reports"))


class EquipmentDataset(models.Model):
    """Represents an uploaded CSV dataset and derived analytics."""

    original_filename = models.CharField(max_length=255)
    stored_file = models.FileField(upload_to="datasets/%Y/%m/%d", storage=dataset_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="equipment_datasets",
    )

    total_records = models.PositiveIntegerField(default=0)
    average_flowrate = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("0"))
    average_pressure = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("0"))
    average_temperature = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("0"))

    type_distribution = models.JSONField(default=dict)
    summary_metadata = models.JSONField(default=dict, blank=True)

    report_file = models.FileField(upload_to="reports/%Y/%m/%d", storage=report_storage, null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - representation only
        return f"Dataset {self.pk} ({self.original_filename})"

    @property
    def storage_path(self) -> str:
        return self.stored_file.path if self.stored_file else ""

    @property
    def report_path(self) -> str:
        return self.report_file.path if self.report_file else ""

    def update_aggregates(self, aggregates: Dict[str, Any]) -> None:
        """Convenience helper to assign aggregate fields from analytics results."""
        self.total_records = int(aggregates.get("total_records", self.total_records))
        self.average_flowrate = Decimal(str(aggregates.get("average_flowrate", self.average_flowrate)))
        self.average_pressure = Decimal(str(aggregates.get("average_pressure", self.average_pressure)))
        self.average_temperature = Decimal(str(aggregates.get("average_temperature", self.average_temperature)))
        self.type_distribution = aggregates.get("type_distribution", self.type_distribution)
        self.summary_metadata = aggregates.get("summary_metadata", self.summary_metadata)
        self.save(update_fields=[
            "total_records",
            "average_flowrate",
            "average_pressure",
            "average_temperature",
            "type_distribution",
            "summary_metadata",
        ])


class EquipmentRecord(models.Model):
    """Represents a single equipment row belonging to a dataset."""

    dataset = models.ForeignKey(
        EquipmentDataset,
        on_delete=models.CASCADE,
        related_name="records",
    )
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=120, db_index=True)
    flowrate = models.DecimalField(max_digits=12, decimal_places=4)
    pressure = models.DecimalField(max_digits=12, decimal_places=4)
    temperature = models.DecimalField(max_digits=12, decimal_places=4)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["equipment_name"]
        indexes = [
            models.Index(fields=["equipment_type"]),
            models.Index(fields=["dataset", "equipment_type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - representation only
        return f"{self.equipment_name} ({self.dataset_id})"
