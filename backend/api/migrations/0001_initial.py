# Generated manually to initialize database tables.
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="EquipmentDataset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("original_filename", models.CharField(max_length=255)),
                (
                    "stored_file",
                    models.FileField(storage=FileSystemStorage(location=getattr(settings, "UPLOAD_ROOT", "uploads")), upload_to="datasets/%Y/%m/%d"),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="equipment_datasets", to=settings.AUTH_USER_MODEL),
                ),
                ("total_records", models.PositiveIntegerField(default=0)),
                ("average_flowrate", models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ("average_pressure", models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ("average_temperature", models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ("type_distribution", models.JSONField(default=dict)),
                ("summary_metadata", models.JSONField(blank=True, default=dict)),
                (
                    "report_file",
                    models.FileField(blank=True, null=True, storage=FileSystemStorage(location=getattr(settings, "REPORT_ROOT", "reports")), upload_to="reports/%Y/%m/%d"),
                ),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
        migrations.CreateModel(
            name="EquipmentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("equipment_name", models.CharField(max_length=255)),
                ("equipment_type", models.CharField(db_index=True, max_length=120)),
                ("flowrate", models.DecimalField(decimal_places=4, max_digits=12)),
                ("pressure", models.DecimalField(decimal_places=4, max_digits=12)),
                ("temperature", models.DecimalField(decimal_places=4, max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "dataset",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="records", to="api.equipmentdataset"),
                ),
            ],
            options={"ordering": ["equipment_name"]},
        ),
        migrations.AddIndex(
            model_name="equipmentrecord",
            index=models.Index(fields=["equipment_type"], name="api_equipm_equipment_6d2217_idx"),
        ),
        migrations.AddIndex(
            model_name="equipmentrecord",
            index=models.Index(fields=["dataset", "equipment_type"], name="api_equipm_dataset_0a3056_idx"),
        ),
    ]
