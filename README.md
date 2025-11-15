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

## CI and Publishing Docker images (GHCR)

The repository includes a GitHub Actions workflow that runs tests and builds artifacts. If you want CI to build and publish containers to GitHub Container Registry (GHCR), follow these steps:

1. Create a Personal Access Token (PAT) with `write:packages` and `read:packages` (and `repo` if needed for private repos).
2. Add the PAT as a repository secret: `Settings → Secrets → Actions → New repository secret` named `GHCR_PAT`.
3. If this repo belongs to an Organization, the Organization Admin must allow GitHub Actions to create and publish packages: `Organization Settings → Actions → Policies → Allow GitHub Actions to create and publish packages`.

If `GHCR_PAT` is not set, the CI still runs tests and builds artifacts but will skip publishing container images.

### Vercel & Render deployment automation (GitHub Actions)

This repository includes a `deploy.yml` workflow that automatically deploys the built frontend to Vercel and triggers a Render deployment for the backend on pushes to `main`.

Required GitHub Secrets to set for automated deployments:

- `VERCEL_TOKEN` - optional but required if you want automatic frontend deployments to Vercel. To generate: Vercel Dashboard → Settings → Tokens → Create Token.
- `GHCR_PAT` - (optional) PAT with `write:packages` and `read:packages` to push images to GHCR.
- `RENDER_API_KEY` - If hosting the backend on Render, create an API key under Account → API Keys.
- `RENDER_SERVICE_ID` - The ID of the Render Service that should be redeployed (found in the Render service settings URL or via Render API).

Setting the secrets in GitHub:

1. Go to the GitHub repo → Settings → Secrets → Actions → New repository secret.
2. Add `VERCEL_TOKEN`, `GHCR_PAT`, `RENDER_API_KEY`, and `RENDER_SERVICE_ID` as appropriate.

Once these are set up and the `deploy.yml` is on the `main` branch, pushes to `main` will automatically deploy the frontend and trigger backend redeploys.
