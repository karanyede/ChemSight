from django.contrib import admin

from .models import EquipmentDataset, EquipmentRecord


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "original_filename", "uploaded_by", "uploaded_at", "total_records")
    search_fields = ("original_filename", "uploaded_by__username")
    list_filter = ("uploaded_at",)


@admin.register(EquipmentRecord)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ("equipment_name", "equipment_type", "dataset", "flowrate")
    search_fields = ("equipment_name", "equipment_type")
    list_filter = ("equipment_type",)
