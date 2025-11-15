"""HTTP client for the chemical equipment API."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import json


class ApiError(RuntimeError):
    """Raised when the API call fails."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    """Simple wrapper around the REST API."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 20) -> None:
        api_root = base_url or os.environ.get("VISUALIZER_API_BASE_URL", "http://localhost:8000/api/")
        self.base_url = api_root.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()
        self._token: Optional[str] = None

    def set_token(self, token: str) -> None:
        self._token = token
        self.session.headers.update({"Authorization": f"Token {token}"})

    def clear_token(self) -> None:
        self._token = None
        self.session.headers.pop("Authorization", None)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - thin wrapper
            # Try to provide a helpful error message. If the server returned JSON include
            # that JSON in the error message so the desktop UI can show meaningful text.
            try:
                parsed = response.json()
                # If JSON is a mapping, stringify it for display; otherwise show raw repr
                if isinstance(parsed, (dict, list)):
                    detail = json.dumps(parsed)
                else:
                    detail = str(parsed)
            except ValueError:
                detail = response.text
            raise ApiError(detail or str(exc), status_code=response.status_code) from exc
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError("Malformed response from server") from exc

    def login(self, username: str, password: str) -> str:
        payload = {"username": username, "password": password}
        response = self.session.post(self.base_url + "auth/login/", json=payload, timeout=self.timeout)
        data = self._handle_response(response)
        token = data.get("token")
        if not token:
            raise ApiError("Missing token in response")
        self.set_token(token)
        return token

    def register(self, username: str, password: str, email: str = "") -> str:
        payload = {"username": username, "password": password, "email": email or None}
        response = self.session.post(self.base_url + "auth/register/", json=payload, timeout=self.timeout)
        data = self._handle_response(response)
        token = data.get("token")
        if not token:
            raise ApiError("Missing token in response")
        self.set_token(token)
        return token

    def get_metrics(self) -> Dict[str, Any]:
        response = self.session.get(self.base_url + "metrics/", timeout=self.timeout)
        return self._handle_response(response)

    def list_datasets(self) -> Dict[str, Any]:
        response = self.session.get(self.base_url + "datasets/", timeout=self.timeout)
        return self._handle_response(response)

    def get_dataset_summary(self, dataset_id: int) -> Dict[str, Any]:
        response = self.session.get(
            self.base_url + f"datasets/{dataset_id}/summary/",
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def get_dataset_records(self, dataset_id: int, sort: str = "equipment_name") -> Dict[str, Any]:
        response = self.session.get(
            self.base_url + f"datasets/{dataset_id}/records/",
            params={"sort": sort},
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def upload_dataset(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists() or not file_path.is_file():
            raise ApiError("Selected file does not exist")
        with file_path.open("rb") as handle:
            files = {
                "file": (file_path.name, handle, "text/csv"),
            }
            response = self.session.post(
                self.base_url + "upload/",
                files=files,
                timeout=self.timeout,
            )
        return self._handle_response(response)

    def download_report(self, dataset_id: int, destination: Path) -> Path:
        response = self.session.get(
            self.base_url + f"datasets/{dataset_id}/report/",
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - thin wrapper
            raise ApiError("Unable to download report", status_code=response.status_code) from exc
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
        return destination


__all__ = ["ApiClient", "ApiError"]
