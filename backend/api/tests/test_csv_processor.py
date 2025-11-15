from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from api.services.csv_processor import CsvProcessingError, process_csv


class CsvProcessorTests(SimpleTestCase):
    def _write_csv(self, rows):
        tmp = tempfile.NamedTemporaryFile("w", newline="", delete=False, suffix=".csv")
        writer = csv.writer(tmp)
        writer.writerow(["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"])
        writer.writerows(rows)
        tmp.close()
        return Path(tmp.name)

    def test_process_csv_success(self):
        path = self._write_csv([["Pump", "Pump", 10, 1.2, 30]])
        try:
            rows, summary = process_csv(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(summary["total_records"], 1)

    def test_process_csv_missing_columns(self):
        tmp = tempfile.NamedTemporaryFile("w", newline="", delete=False, suffix=".csv")
        writer = csv.writer(tmp)
        writer.writerow(["Equipment Name", "Flowrate"])
        writer.writerow(["Pump", 10])
        tmp.close()
        path = Path(tmp.name)
        with self.assertRaises(CsvProcessingError):
            process_csv(path)
        path.unlink(missing_ok=True)
