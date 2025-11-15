"""Upload endpoint implementation."""
from __future__ import annotations

import logging
import mimetypes
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import List

from django.conf import settings
from django.core.files import File
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EquipmentDataset, EquipmentRecord
from .serializers import DatasetUploadResponseSerializer
from .services.csv_processor import CsvProcessingError, process_csv

logger = logging.getLogger(__name__)


class DatasetUploadView(APIView):
    """Accepts CSV uploads, validates schema, and stores analytics."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "upload"

    def post(self, request, *args, **kwargs):  # type: ignore[override]
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_size = upload.size or 0
        if file_size > getattr(settings, "MAX_UPLOAD_SIZE_BYTES", 25 * 1024 * 1024):
            return Response({"detail": "File exceeds maximum allowed size"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = upload.content_type or mimetypes.guess_type(upload.name)[0]
        allowed_types = getattr(settings, "ALLOWED_UPLOAD_MIME_TYPES", ["text/csv"])
        if content_type not in allowed_types:
            return Response({"detail": f"Unsupported file type: {content_type}"}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(upload.name).suffix) as tmp:
            for chunk in upload.chunks():
                tmp.write(chunk)
            tmp_path = Path(tmp.name)

        logger.info(
            "Upload received",
            extra={
                "uploaded_filename": upload.name,
                "uploaded_size": file_size,
                "uploaded_by": request.user.username,
            },
        )

        # Placeholder for external malware scanning integration
        if getattr(settings, "ENABLE_UPLOAD_SCANNING", False):  # pragma: no cover - integration hook
            logger.warning("Upload scanning enabled but not configured", extra={"file": str(tmp_path)})

        try:
            rows, summary = process_csv(tmp_path)
        except CsvProcessingError as exc:
            tmp_path.unlink(missing_ok=True)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                dataset = EquipmentDataset(
                    original_filename=upload.name,
                    uploaded_by=request.user,
                )
                dataset.save()
                with tmp_path.open("rb") as handle:
                    dataset.stored_file.save(f"{dataset.pk}_{upload.name}", File(handle), save=True)

                records: List[EquipmentRecord] = []
                for record in rows:
                    records.append(
                        EquipmentRecord(
                            dataset=dataset,
                            equipment_name=record["equipment_name"],
                            equipment_type=record["equipment_type"],
                            flowrate=Decimal(str(record["flowrate"])),
                            pressure=Decimal(str(record["pressure"])),
                            temperature=Decimal(str(record["temperature"])),
                        )
                    )
                EquipmentRecord.objects.bulk_create(records, batch_size=1000)

                dataset.update_aggregates(summary)
        except Exception as exc:  # pragma: no cover - ensures cleanup
            logger.exception("Upload processing failed", extra={"filename": upload.name})
            return Response({"detail": "Failed to persist dataset"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            tmp_path.unlink(missing_ok=True)

        serializer = DatasetUploadResponseSerializer({"dataset": dataset, "summary": summary})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
