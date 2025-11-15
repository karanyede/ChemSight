"""Generate PDF reports for datasets."""
from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import EquipmentDataset

logger = logging.getLogger(__name__)


def _build_distribution_chart(distribution: Dict[str, int]) -> BytesIO:
    fig, ax = plt.subplots(figsize=(6, 3))
    types = list(distribution.keys())
    values = list(distribution.values())
    ax.bar(types, values, color="#4C51BF")
    ax.set_title("Equipment Type Distribution")
    ax.set_xlabel("Type")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    image_stream = BytesIO()
    fig.savefig(image_stream, format="png")
    plt.close(fig)
    image_stream.seek(0)
    return image_stream


def _write_pdf(dataset: EquipmentDataset, output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Chemical Equipment Dataset Report", styles["Title"]))
    story.append(Spacer(1, 12))

    meta_table = Table(
        [
            ["Dataset ID", str(dataset.pk)],
            ["Filename", dataset.original_filename],
            ["Uploaded By", dataset.uploaded_by.get_username()],
            ["Uploaded At", dataset.uploaded_at.strftime("%Y-%m-%d %H:%M")],
            ["Total Records", str(dataset.total_records)],
        ]
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 12))

    summary_table = Table(
        [
            ["Average Flowrate", f"{dataset.average_flowrate:.2f}"],
            ["Average Pressure", f"{dataset.average_pressure:.2f}"],
            ["Average Temperature", f"{dataset.average_temperature:.2f}"],
        ]
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 12))

    if dataset.type_distribution:
        chart_stream = _build_distribution_chart(dataset.type_distribution)
        from reportlab.platypus import Image

        image = Image(chart_stream, width=400, height=200)
        image.hAlign = "CENTER"
        story.append(image)
        story.append(Spacer(1, 12))

    if dataset.summary_metadata:
        story.append(Paragraph("Processing Metadata", styles["Heading2"]))
        metadata_rows = [[key, str(value)] for key, value in dataset.summary_metadata.items()]
        metadata_table = Table(metadata_rows)
        metadata_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(metadata_table)

    doc.build(story)


def generate_dataset_report(dataset: EquipmentDataset) -> Path:
    """Create or return a cached PDF for the given dataset."""

    reports_dir = Path(settings.REPORT_ROOT)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if dataset.report_file and Path(dataset.report_file.path).exists():
        return Path(dataset.report_file.path)

    filename = settings.REPORT_FILENAME_TEMPLATE.format(dataset_id=dataset.pk)
    output_path = reports_dir / filename

    logger.info(
        "Generating PDF report",
        extra={"dataset": dataset.pk, "output_path": str(output_path)},
    )

    _write_pdf(dataset, output_path)

    return output_path
