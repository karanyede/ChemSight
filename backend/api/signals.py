"""Signal handlers for lifecycle hooks."""
from __future__ import annotations

import logging
from typing import Iterable

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EquipmentDataset

logger = logging.getLogger(__name__)


def _cleanup_dataset(dataset: EquipmentDataset) -> None:
    if dataset.stored_file:
        dataset.stored_file.delete(save=False)
    if dataset.report_file:
        dataset.report_file.delete(save=False)
    dataset.delete()


@receiver(post_save, sender=EquipmentDataset)
def enforce_dataset_retention(sender, instance: EquipmentDataset, **kwargs) -> None:  # type: ignore[arg-type]
    limit = 5
    datasets: Iterable[EquipmentDataset] = EquipmentDataset.objects.filter(
        uploaded_by=instance.uploaded_by
    ).order_by("-uploaded_at")
    stale = datasets[limit:]
    for dataset in stale:
        logger.info(
            "Cleaning up stale dataset",
            extra={"dataset": dataset.pk, "user": dataset.uploaded_by.username},
        )
        _cleanup_dataset(dataset)
