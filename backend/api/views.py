"""Core dataset API views."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EquipmentDataset, EquipmentRecord
from .permissions import IsDatasetOwner
from .serializers import (
    DatasetSummarySerializer,
    EquipmentDatasetSerializer,
    EquipmentRecordSerializer,
)

logger = logging.getLogger(__name__)


class DatasetPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 200


class DatasetListView(generics.ListAPIView):
    serializer_class = EquipmentDatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DatasetPagination

    def get_queryset(self) -> QuerySet[EquipmentDataset]:
        return EquipmentDataset.objects.filter(uploaded_by=self.request.user)


class DatasetDetailView(generics.RetrieveAPIView):
    serializer_class = EquipmentDatasetSerializer
    permission_classes = [permissions.IsAuthenticated, IsDatasetOwner]
    queryset = EquipmentDataset.objects.all()


class DatasetSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDatasetOwner]

    def get(self, request, pk: int, *args, **kwargs):  # type: ignore[override]
        dataset = get_object_or_404(EquipmentDataset, pk=pk)
        self.check_object_permissions(request, dataset)
        serializer = DatasetSummarySerializer(
            {
                "total_records": dataset.total_records,
                "average_flowrate": float(dataset.average_flowrate),
                "average_pressure": float(dataset.average_pressure),
                "average_temperature": float(dataset.average_temperature),
                "type_distribution": dataset.type_distribution,
            }
        )
        return Response(serializer.data)


class EquipmentRecordPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 500


class DatasetRecordsView(generics.ListAPIView):
    serializer_class = EquipmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsDatasetOwner]
    pagination_class = EquipmentRecordPagination

    def get_queryset(self) -> QuerySet[EquipmentRecord]:
        dataset = get_object_or_404(EquipmentDataset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, dataset)

        qs = dataset.records.all()
        equipment_type = self.request.query_params.get("type")
        if equipment_type:
            qs = qs.filter(equipment_type__iexact=equipment_type)

        sort = self.request.query_params.get("sort", "equipment_name")
        allowed_sorts = {"equipment_name", "flowrate", "pressure", "temperature"}
        if sort.lstrip("-") not in allowed_sorts:
            sort = "equipment_name"
        qs = qs.order_by(sort)

        return qs


class MetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):  # type: ignore[override]
        start = time.perf_counter()
        datasets = EquipmentDataset.objects.filter(uploaded_by=request.user)
        latest = datasets.order_by("-uploaded_at").first()
        payload: Dict[str, Any] = {
            "dataset_count": datasets.count(),
            "latest_upload": latest.uploaded_at.isoformat() if latest else None,
        }
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Metrics delivered",
            extra={"elapsed_ms": elapsed_ms, "username": request.user.username},
        )
        return Response(payload)
