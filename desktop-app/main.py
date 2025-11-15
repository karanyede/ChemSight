"""PyQt5 desktop client for the chemical equipment visualizer."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional

from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from api_client import ApiClient, ApiError
from workers import Worker


class ChartCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas for displaying type distributions."""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(5, 3))
        super().__init__(self.figure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # Ensure the canvas has a sensible minimum height so it doesn't get compressed
        self.setMinimumHeight(240)
        self.update_chart({})

    def update_chart(self, distribution: Dict[str, int]) -> None:
        # Ensure the underlying figure has reasonable dimensions
        try:
            self.figure.set_size_inches(6, 3)
        except Exception:
            # Some backends may not honor set_size_inches in this embed context; ignore safely
            pass
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        ax.set_title("Type distribution")
        if not distribution:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            self.draw_idle()
            return
        labels = list(distribution.keys())
        values = [distribution[label] for label in labels]
        indices = range(len(labels))
        ax.bar(indices, values, color="#4c51bf")
        ax.set_ylabel("Count")
        ax.set_xticks(list(indices))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        self.figure.tight_layout()
        # Force a redraw of the canvas to reflect new layout/size hints
        self.draw_idle()


class LoginWidget(QtWidgets.QWidget):
    authenticated = QtCore.pyqtSignal()
    status_message = QtCore.pyqtSignal(str)

    def __init__(self, api_client: ApiClient, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.api = api_client
        self.thread_pool = QtCore.QThreadPool()
        self.mode: str = "login"
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("Chemical Equipment Visualizer")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)

        self.error_label = QtWidgets.QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #b91c1c;")
        self.error_label.hide()

        form = QtWidgets.QFormLayout()
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Username")
        form.addRow("Username", self.username_input)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email (optional)")
        form.addRow("Email", self.email_input)
        self.email_input.hide()

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        form.addRow("Password", self.password_input)

        layout.addLayout(form)
        layout.addWidget(self.error_label)

        self.submit_button = QtWidgets.QPushButton("Log in")
        self.submit_button.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_button)

        self.toggle_button = QtWidgets.QPushButton("Need an account? Register")
        self.toggle_button.clicked.connect(self.toggle_mode)
        layout.addWidget(self.toggle_button)

        layout.addStretch()

    def toggle_mode(self) -> None:
        self.mode = "register" if self.mode == "login" else "login"
        if self.mode == "login":
            self.submit_button.setText("Log in")
            self.toggle_button.setText("Need an account? Register")
            self.email_input.hide()
        else:
            self.submit_button.setText("Register")
            self.toggle_button.setText("Already registered? Log in")
            self.email_input.show()
        self.error_label.hide()

    def handle_submit(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip()
        if not username or not password:
            self.show_error("Username and password are required")
            return
        self.setDisabled(True)
        self.status_message.emit("Contacting server…")
        if self.mode == "login":
            worker = Worker(self.api.login, username, password)
        else:
            worker = Worker(self.api.register, username, password, email)
        worker.signals.result.connect(self.handle_success)
        worker.signals.error.connect(self.handle_error)
        worker.signals.finished.connect(lambda: self.setDisabled(False))
        self.thread_pool.start(worker)

    def handle_success(self, _: object) -> None:
        self.error_label.hide()
        self.status_message.emit("Authenticated")
        self.authenticated.emit()

    def handle_error(self, message: str) -> None:
        self.show_error(message)
        self.status_message.emit(message)

    def show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.show()


class DashboardWidget(QtWidgets.QWidget):
    status_message = QtCore.pyqtSignal(str)
    request_logout = QtCore.pyqtSignal()

    def __init__(self, api_client: ApiClient, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.api = api_client
        self.thread_pool = QtCore.QThreadPool()
        self.current_dataset: Optional[int] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        top_bar = QtWidgets.QHBoxLayout()
        self.upload_button = QtWidgets.QPushButton("Upload CSV")
        self.upload_button.clicked.connect(self.handle_upload)
        top_bar.addWidget(self.upload_button)

        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        top_bar.addWidget(self.refresh_button)

        top_bar.addStretch()

        self.logout_button = QtWidgets.QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        top_bar.addWidget(self.logout_button)

        layout.addLayout(top_bar)

        metrics_group = QtWidgets.QGroupBox("Metrics")
        metrics_layout = QtWidgets.QFormLayout()
        self.metric_total = QtWidgets.QLabel("–")
        self.metric_latest = QtWidgets.QLabel("–")
        metrics_layout.addRow("Datasets", self.metric_total)
        metrics_layout.addRow("Latest upload", self.metric_latest)
        metrics_group.setLayout(metrics_layout)

        summary_group = QtWidgets.QGroupBox("Dataset summary")
        summary_layout = QtWidgets.QFormLayout()
        self.summary_total = QtWidgets.QLabel("–")
        self.summary_flow = QtWidgets.QLabel("–")
        self.summary_pressure = QtWidgets.QLabel("–")
        self.summary_temperature = QtWidgets.QLabel("–")
        summary_layout.addRow("Records", self.summary_total)
        summary_layout.addRow("Average flowrate", self.summary_flow)
        summary_layout.addRow("Average pressure", self.summary_pressure)
        summary_layout.addRow("Average temperature", self.summary_temperature)
        summary_group.setLayout(summary_layout)

        info_layout = QtWidgets.QHBoxLayout()
        info_layout.addWidget(metrics_group)
        info_layout.addWidget(summary_group)

        layout.addLayout(info_layout)

        self.chart = ChartCanvas()
        layout.addWidget(self.chart, stretch=1)

        self.dataset_table = QtWidgets.QTableWidget(0, 4)
        headers = ["ID", "Filename", "Uploaded", "Records"]
        self.dataset_table.setHorizontalHeaderLabels(headers)
        self.dataset_table.horizontalHeader().setStretchLastSection(True)
        self.dataset_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.dataset_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.itemSelectionChanged.connect(self.handle_selection_changed)
        layout.addWidget(self.dataset_table, stretch=2)

        report_bar = QtWidgets.QHBoxLayout()
        self.download_button = QtWidgets.QPushButton("Download PDF report")
        self.download_button.clicked.connect(self.handle_download_report)
        report_bar.addWidget(self.download_button)
        report_bar.addStretch()
        layout.addLayout(report_bar)

        self.status_label = QtWidgets.QLabel()
        layout.addWidget(self.status_label)

    def update_metrics(self, data: Dict[str, object]) -> None:
        self.metric_total.setText(str(data.get("dataset_count", "–")))
        latest = data.get("latest_upload")
        if latest:
            self.metric_latest.setText(str(latest))
        else:
            self.metric_latest.setText("–")

    def update_summary(self, data: Dict[str, object]) -> None:
        self.summary_total.setText(str(data.get("total_records", "–")))
        self.summary_flow.setText(f"{data.get('average_flowrate', 0):.2f}")
        self.summary_pressure.setText(f"{data.get('average_pressure', 0):.2f}")
        self.summary_temperature.setText(f"{data.get('average_temperature', 0):.2f}")
        distribution = data.get("type_distribution", {}) or {}
        self.chart.update_chart({str(k): int(v) for k, v in distribution.items()})

    def populate_datasets(self, response: Dict[str, object]) -> None:
        results = response.get("results", []) if isinstance(response, dict) else []
        rows = len(results)
        self.dataset_table.setRowCount(rows)
        for row, record in enumerate(results):
            dataset_id = int(record.get("id"))
            filename = str(record.get("original_filename", ""))
            uploaded = str(record.get("uploaded_at", ""))
            total = str(record.get("total_records", ""))
            for col, value in enumerate([dataset_id, filename, uploaded, total]):
                item = QtWidgets.QTableWidgetItem(str(value))
                if col == 0:
                    item.setData(QtCore.Qt.UserRole, dataset_id)
                self.dataset_table.setItem(row, col, item)
        if rows:
            self.dataset_table.selectRow(0)
        else:
            self.current_dataset = None
            self.update_summary({})

    def run_task(self, fn, *args) -> None:
        worker = Worker(fn, *args)
        worker.signals.result.connect(self.handle_task_result)
        worker.signals.error.connect(self.handle_task_error)
        worker.signals.finished.connect(self.handle_task_finished)
        self.thread_pool.start(worker)

    def handle_task_result(self, result: object) -> None:
        if not isinstance(result, dict):
            return
        marker = result.get("_marker")
        if marker == "metrics":
            self.update_metrics(result.get("payload", {}))
        elif marker == "datasets":
            self.populate_datasets(result.get("payload", {}))
        elif marker == "summary":
            self.update_summary(result.get("payload", {}))
            self.status_message.emit("Summary updated")
        elif marker == "upload":
            self.status_message.emit("Upload complete")
            payload = result.get("payload", {})
            dataset_id = payload.get("dataset", {}).get("id")
            self.refresh_dashboard(select_dataset=dataset_id)
        elif marker == "report":
            path = result.get("payload")
            self.status_message.emit(f"Report saved to {path}")

    def handle_task_error(self, message: str) -> None:
        self.status_message.emit(message)
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #b91c1c;")

    def handle_task_finished(self) -> None:
        pass

    def refresh_dashboard(self, select_dataset: Optional[int] = None) -> None:
        self.status_message.emit("Refreshing dashboard…")
        metrics_worker = Worker(self._fetch_metrics)
        metrics_worker.signals.result.connect(self.handle_task_result)
        metrics_worker.signals.error.connect(self.handle_task_error)
        self.thread_pool.start(metrics_worker)

        datasets_worker = Worker(self._fetch_datasets)
        datasets_worker.signals.result.connect(lambda r: self._handle_dataset_refresh(r, select_dataset))
        datasets_worker.signals.error.connect(self.handle_task_error)
        self.thread_pool.start(datasets_worker)

    def _handle_dataset_refresh(self, result: object, select_dataset: Optional[int]) -> None:
        if isinstance(result, dict):
            result.setdefault("_marker", "datasets")
            self.populate_datasets(result.get("payload", {}))
            if select_dataset:
                self.select_dataset_by_id(select_dataset)

    def _fetch_metrics(self) -> Dict[str, object]:
        data = self.api.get_metrics()
        return {"_marker": "metrics", "payload": data}

    def _fetch_datasets(self) -> Dict[str, object]:
        data = self.api.list_datasets()
        return {"_marker": "datasets", "payload": data}

    def handle_selection_changed(self) -> None:
        items = self.dataset_table.selectedItems()
        if not items:
            return
        dataset_id = items[0].data(QtCore.Qt.UserRole)
        if dataset_id == self.current_dataset:
            return
        self.current_dataset = dataset_id
        worker = Worker(self._fetch_summary, dataset_id)
        worker.signals.result.connect(self.handle_task_result)
        worker.signals.error.connect(self.handle_task_error)
        self.thread_pool.start(worker)

    def _fetch_summary(self, dataset_id: int) -> Dict[str, object]:
        summary = self.api.get_dataset_summary(dataset_id)
        return {"_marker": "summary", "payload": summary}

    def handle_upload(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CSV", str(Path.home()), "CSV Files (*.csv)")
        if not file_path:
            return
        path_obj = Path(file_path)
        self.status_message.emit("Uploading dataset…")
        worker = Worker(self._upload_file, path_obj)
        worker.signals.result.connect(self.handle_task_result)
        worker.signals.error.connect(self.handle_task_error)
        self.thread_pool.start(worker)

    def _upload_file(self, file_path: Path) -> Dict[str, object]:
        response = self.api.upload_dataset(file_path)
        return {"_marker": "upload", "payload": response}

    def handle_download_report(self) -> None:
        if not self.current_dataset:
            self.status_message.emit("Select a dataset first")
            return
        target, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save report",
            str(Path.home() / f"dataset-{self.current_dataset}.pdf"),
            "PDF Files (*.pdf)",
        )
        if not target:
            return
        self.status_message.emit("Downloading report…")
        worker = Worker(self._download_report, self.current_dataset, Path(target))
        worker.signals.result.connect(self.handle_task_result)
        worker.signals.error.connect(self.handle_task_error)
        self.thread_pool.start(worker)

    def _download_report(self, dataset_id: int, destination: Path) -> Dict[str, object]:
        saved = self.api.download_report(dataset_id, destination)
        return {"_marker": "report", "payload": str(saved)}

    def handle_logout(self) -> None:
        self.api.clear_token()
        self.request_logout.emit()

    def select_dataset_by_id(self, dataset_id: int) -> None:
        for row in range(self.dataset_table.rowCount()):
            item = self.dataset_table.item(row, 0)
            if item and item.data(QtCore.Qt.UserRole) == dataset_id:
                self.dataset_table.selectRow(row)
                break


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.api = api_client
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.resize(1100, 700)
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_view = LoginWidget(self.api)
        self.dashboard_view = DashboardWidget(self.api)

        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.dashboard_view)

        self.login_view.authenticated.connect(self.show_dashboard)
        self.login_view.status_message.connect(self.show_status)
        self.dashboard_view.status_message.connect(self.show_status)
        self.dashboard_view.request_logout.connect(self.show_login)

        self.show_login()

    def show_status(self, message: str) -> None:
        self.statusBar().showMessage(message, 5000)

    def show_dashboard(self) -> None:
        self.stack.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.refresh_dashboard()
        self.show_status("Dashboard ready")

    def show_login(self) -> None:
        self.stack.setCurrentWidget(self.login_view)
        self.show_status("Please sign in")


def main() -> None:
    parser = argparse.ArgumentParser(description="Desktop client for the visualizer")
    parser.add_argument("--api", dest="api", help="Base URL for the API", default=None)
    args = parser.parse_args()
    app = QtWidgets.QApplication(sys.argv)
    api_client = ApiClient(base_url=args.api)
    window = MainWindow(api_client)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
