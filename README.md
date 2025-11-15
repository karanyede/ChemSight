# Chemical Equipment Parameter Visualizer

Hybrid analytics platform that shares a Django REST backend between a responsive React dashboard and a PyQt desktop supervisor application. Users can upload chemical equipment CSV logs, review computed insights, and export PDF reports from either client.

## Solution Highlights

- Token-protected CSV upload pipeline with automatic schema validation, summary statistics, equipment-type distribution, and retention of the last five datasets.
- Shared REST API powering both web (React + Chart.js) and desktop (PyQt5 + Matplotlib) experiences, including PDF report generation.
- Accessibility- and mobile-friendly web UI with authentication, dashboard metrics, dataset history, and drill-down views.
- Desktop client mirrors core workflows with responsive UI threads and background workers for uploads and report downloads.

## Repository Layout

- `backend/` – Django + DRF service (Celery-ready) handling ingestion, analytics, PDF generation, and auth.
- `web-frontend/` – Vite + React (TypeScript) SPA consuming the API and rendering interactive charts.
- `desktop-app/` – PyQt5 application with reusable API client, worker threads, and Matplotlib widgets.
- `sample_data/` – Example CSV fixtures (see `sample_equipment_data.csv`).

## Prerequisites

- Python 3.11+ (backend and desktop)
- Node.js 18+ and npm 9+
- Git (for cloning)
- Optional: Redis if you plan to enable Celery background jobs

## Quick Start

### 1. Backend API

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
touch .env  # add SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS settings, etc.
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
```

Key environment variables:

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`
- `UPLOAD_ROOT`, `REPORT_ROOT`, `MAX_UPLOAD_SIZE_BYTES`

### 2. Web Frontend

```bash
cd web-frontend
npm install
echo VITE_API_BASE_URL=http://localhost:8000/api/ > .env.local
npm run dev -- --host --port 5173

# Production build
npm run build
```

Features include responsive navigation, protected routes, dataset history, distribution charts, and PDF download helper.

### 3. Desktop Client

```bash
cd desktop-app
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

Configure API host via `.env` (defaults to `http://localhost:8000/api/`). The desktop app runs uploads and report generation on worker threads to keep the UI responsive.

### 4. Sample Data

Use `sample_data/sample_equipment_data.csv` to quickly demo uploads from either client. The backend enforces retention by removing the oldest dataset once six uploads exist for a user.

## Testing & Quality

- **Backend** – `cd backend && python manage.py test` (covers CSV processor, upload flow, metrics, report API).
- **Web** – `cd web-frontend && npm run test` for Vitest suite, or use Testsprite plans under `testsprite_tests/` (`npm run test:sprite` if configured).
- **Desktop** – Launch `python main.py` and exercise upload/report workflows; add PyQt unit tests under `desktop-app/tests/` as needed.

Logs carry correlation IDs, and optional Celery/Redis support is scaffolded for asynchronous workloads.

## Deployment Notes

- Ensure persistent directories for `uploads/` and `reports/` are writable by the Django process.
- Update `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` before exposing the API publicly.
- Set `DEBUG=0` and configure HTTPS transport for production.

### Running with Docker (local testing)

You can run a simple local deployment using Docker and Docker Compose. This is useful for quick integration testing.

```bash
docker compose build
docker compose up
```

The backend will be exposed on `http://localhost:8000`, and the frontend will be served by nginx on `http://localhost:5173` (the compose file maps nginx 80 → host 5173).


## Roadmap / Cleanup Targets

- Evaluate generated artifacts and unused exploratory files (e.g., baseline SVG diagrams) before production packaging.
- Harden desktop packaging (PyInstaller or Briefcase) and add automated UI regression tests.
- Optionally integrate Celery workers for background PDF creation when large jobs arrive.
