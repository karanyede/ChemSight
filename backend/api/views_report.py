"""Views responsible for PDF report generation and download."""
from __future__ import annotations

import logging
from pathlib import Path

from django.core.files import File
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.views import APIView

from .models import EquipmentDataset
from .permissions import IsDatasetOwner
from .services.report_generator import generate_dataset_report

logger = logging.getLogger(__name__)


class DatasetReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDatasetOwner]
    throttle_scope = "report"

    def get(self, request, pk: int, *args, **kwargs):  # type: ignore[override]
        dataset = get_object_or_404(EquipmentDataset, pk=pk)
        self.check_object_permissions(request, dataset)

        report_path = generate_dataset_report(dataset)
        path_obj = Path(report_path)
        if not path_obj.exists():  # pragma: no cover - defensive
            raise Http404("Report not found")

        # Persist reference for re-use
        if not dataset.report_file or not Path(dataset.report_file.path).exists():
            with path_obj.open("rb") as handle:
                dataset.report_file.save(path_obj.name, File(handle), save=True)

        logger.info(
            "Report served",
            extra={"dataset": dataset.pk, "user": request.user.username},
        )
        return FileResponse(path_obj.open("rb"), filename=path_obj.name, as_attachment=True)
