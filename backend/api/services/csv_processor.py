"""CSV ingestion helpers built around pandas."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "Equipment Name",
    "Type",
    "Flowrate",
    "Pressure",
    "Temperature",
]

NUMERIC_COLUMNS = ["Flowrate", "Pressure", "Temperature"]


class CsvProcessingError(Exception):
    """Raised when CSV validation or parsing fails."""


def _validate_columns(columns: Iterable[str]) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing:
        raise CsvProcessingError(f"Missing required columns: {', '.join(missing)}")


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isnull().any():
            raise CsvProcessingError(f"Column '{column}' contains non-numeric values or blanks")
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["Equipment Name", "Type"])
    df["Equipment Name"] = df["Equipment Name"].astype(str).str.strip()
    df["Type"] = df["Type"].astype(str).str.strip()
    return df


def load_csv_chunks(path: Path) -> Iterable[pd.DataFrame]:
    """Yield DataFrame chunks to minimize memory footprint."""

    chunk_size = getattr(settings, "CHUNK_SIZE", 50_000)
    try:
        for chunk in pd.read_csv(path, chunksize=chunk_size):
            _validate_columns(chunk.columns)
            yield _coerce_numeric(_normalize_columns(chunk))
    except CsvProcessingError:
        raise
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception("Unexpected CSV parsing failure", extra={"path": str(path)})
        raise CsvProcessingError("Unable to parse CSV file") from exc


def summarise_dataframe(df: pd.DataFrame) -> Dict[str, float]:
    return {
        "average_flowrate": float(df["Flowrate"].mean()),
        "average_pressure": float(df["Pressure"].mean()),
        "average_temperature": float(df["Temperature"].mean()),
    }


def compute_distribution(df: pd.DataFrame) -> Dict[str, int]:
    distribution = df["Type"].value_counts().to_dict()
    return {str(k): int(v) for k, v in distribution.items()}


def process_csv(path: Path) -> Tuple[List[Dict[str, str]], Dict[str, float]]:
    """Return row dictionaries and aggregate metrics for a CSV file."""

    start_time = time.perf_counter()
    total_rows = 0
    aggregate_flowrate = 0.0
    aggregate_pressure = 0.0
    aggregate_temperature = 0.0
    distribution: Dict[str, int] = {}
    rows: List[Dict[str, str]] = []

    for chunk in load_csv_chunks(path):
        chunk_records = chunk.to_dict(orient="records")
        rows.extend(
            {
                "equipment_name": record["Equipment Name"],
                "equipment_type": record["Type"],
                "flowrate": record["Flowrate"],
                "pressure": record["Pressure"],
                "temperature": record["Temperature"],
            }
            for record in chunk_records
        )
        total_rows += len(chunk_records)
        stats = summarise_dataframe(chunk)
        aggregate_flowrate += stats["average_flowrate"] * len(chunk_records)
        aggregate_pressure += stats["average_pressure"] * len(chunk_records)
        aggregate_temperature += stats["average_temperature"] * len(chunk_records)
        for key, value in compute_distribution(chunk).items():
            distribution[key] = distribution.get(key, 0) + value

    if total_rows == 0:
        raise CsvProcessingError("CSV file does not contain any valid rows")

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    summary = {
        "total_records": total_rows,
        "average_flowrate": aggregate_flowrate / total_rows,
        "average_pressure": aggregate_pressure / total_rows,
        "average_temperature": aggregate_temperature / total_rows,
        "type_distribution": distribution,
        "summary_metadata": {
            "processed_ms": round(elapsed_ms, 2),
            "chunk_size": getattr(settings, "CHUNK_SIZE", 50_000),
        },
    }

    logger.info(
        "CSV processed",
        extra={
            "path": str(path),
            "records": total_rows,
            "elapsed_ms": elapsed_ms,
            "metrics_namespace": getattr(settings, "METRICS_NAMESPACE", "chemical_visualizer"),
        },
    )

    return rows, summary
