"""Serializers for API payloads."""
from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import EquipmentDataset, EquipmentRecord

User = get_user_model()


class TypeDistributionField(serializers.Field):
    """Ensures type distribution JSON uses deterministic shapes."""

    def to_representation(self, value: Dict[str, Any]) -> Dict[str, Any]:
        return dict(sorted(value.items())) if isinstance(value, dict) else {}

    def to_internal_value(self, data: Any) -> Dict[str, Any]:  # pragma: no cover - not used for input
        if isinstance(data, dict):
            return data
        raise serializers.ValidationError("Type distribution must be a mapping")


class EquipmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentRecord
        fields = [
            "id",
            "dataset",
            "equipment_name",
            "equipment_type",
            "flowrate",
            "pressure",
            "temperature",
            "created_at",
        ]
        read_only_fields = ["id", "dataset", "created_at"]


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    type_distribution = TypeDistributionField()
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EquipmentDataset
        fields = [
            "id",
            "original_filename",
            "stored_file",
            "uploaded_at",
            "uploaded_by",
            "total_records",
            "average_flowrate",
            "average_pressure",
            "average_temperature",
            "type_distribution",
            "summary_metadata",
            "report_file",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
            "uploaded_by",
            "total_records",
            "average_flowrate",
            "average_pressure",
            "average_temperature",
            "type_distribution",
            "summary_metadata",
            "report_file",
        ]


class DatasetSummarySerializer(serializers.Serializer):
    total_records = serializers.IntegerField()
    average_flowrate = serializers.FloatField()
    average_pressure = serializers.FloatField()
    average_temperature = serializers.FloatField()
    type_distribution = TypeDistributionField()


class DatasetUploadResponseSerializer(serializers.Serializer):
    dataset = EquipmentDatasetSerializer()
    summary = DatasetSummarySerializer()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def create(self, validated_data: Dict[str, Any]) -> User:
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
        )
        return user
