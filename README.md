# Chemical Equipment Parameter Visualizer

Chemical Equipment Parameter Visualizer is a hybrid analytics experience. A Django REST backend ingests CSV equipment logs, a Vite/React SPA surfaces insights in the browser, and a PyQt desktop supervisor app mirrors the same workflows for on-premise users.

## What it does

- Accepts CSV uploads, validates each row, and retains the five most recent datasets per user while computing summary statistics and distributions.
- Serves a single REST API (`/api/`) that handles authentication, dataset management, report generation, and lightweight metrics.
- Powers three UIs: the responsive React dashboard, the PyQt desktop client, and a future-proof API for scheduled jobs or automation.

## How the pieces connect

1. **Upload & validation** – users POST a CSV to `backend/api/upload/`; the backend runs schema checks, computes averages, and stores metadata before queuing report rendering.
2. **API-first design** – every UI talks to the same Django REST endpoints, so tokens, throttling, and permissions are centralized under `backend/api/`.
3. **Web dashboard** – the SPA authenticates via token/session routes, lists dataset history, and renders distribution charts plus PDF download buttons.
4. **Desktop supervisor** – PyQt workers reuse the API client to upload files, poll status, download reports, and keep the GUI responsive even during long-running uploads.

## Repository walkthrough

- `backend/` – Django project with `config/` for settings (including CORS and host rules), `api/` for upload/auth/report views, `uploads/` & `reports/` folders for storing binaries, and Celery-ready hooks for async work.
- `web-frontend/` – Vite + React (TypeScript). `src/` contains reusable hooks, API clients, and Chart.js components; `vite.config.ts` orchestrates env vars like `VITE_API_BASE_URL`; `public/` holds shared assets.
- `desktop-app/` – PyQt5 application with `main.py`, reusable `api_client.py`, and worker threads that keep uploads and report downloads non-blocking while feeding Matplotlib widgets.
- `sample_data/` – curated CSV fixtures (`sample_equipment_data.csv`) you can drop into either client for fast demos, helping QA and documentation.
- `docs/` – deployment guides (`DEPLOY_RENDER.md`, `DEPLOY_VERCEL.md`), the new `VIDEO_SCRIPT.md`, and supporting notes on production readiness.

## Getting started

### Backend service

1. ```bash
   cd backend
   python -m venv .venv
   source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Create `.env` with `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and optional storage overrides.
3. ```bash
   python manage.py migrate
   python manage.py createsuperuser  # optional
   python manage.py runserver
   ```
4. Uploads land in `uploads/`, PDF reports in `reports/`, and background metrics are exposed under `/api/metrics/`.

### Web frontend

1. ```bash
   cd web-frontend
   npm install
   echo VITE_API_BASE_URL=http://localhost:8000/api/ > .env.local
   ```
2. `npm run dev -- --host --port 5173` boots the SPA and proxies API calls to the local backend.
3. `npm run build` produces a production-ready `dist/` folder; the site relies on `VITE_API_BASE_URL`, `VITE_AUTH_DOMAIN`, and any feature flags you add (all prefixed with `VITE_`).

### Desktop supervisor

1. ```bash
   cd desktop-app
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -r requirements.txt
   python main.py
   ```
2. The desktop client shares the backend API client, so configure `.env` to match the web UI and point to the same `VITE_API_BASE_URL` equivalent.
3. Worker threads ensure uploads/reports run without freezing the PyQt GUI while status dialogs and Matplotlib charts stay interactive.

### Sample data

- Use `sample_data/sample_equipment_data.csv` to seed the upload pipeline from either client.
- The ingestion logic limits retention to five uploads per user; older files are pruned automatically.

## Testing

- **Backend:** `cd backend && python manage.py test` (covers upload logic, auth views, serializers, and report APIs).
- **Web:** `cd web-frontend && npm run test` or `npm run test:sprite` if Testsprite plans are configured.
- **Desktop:** Launch `python main.py` and exercise upload/report flows, optionally adding PyQt unit tests under `desktop-app/tests/`.

## Deployment

- **Frontend:** follow `docs/DEPLOY_VERCEL.md` to build the SPA on Vercel and set `VITE_API_BASE_URL` to your backend.
- **Backend (recommended):** follow `docs/DEPLOY_RAILWAY.md` for the simplest deployment experience with auto-provisioned PostgreSQL and zero config health checks.
- **Backend (alternative):** follow `docs/DEPLOY_RENDER.md` for Render deployment with PostgreSQL setup, gunicorn config, and manual health check configuration.
- Keep uploads/reports persistent via platform volumes or an external blob store, and rerun migrations whenever the schema changes.

## Video walkthrough script

See `docs/VIDEO_SCRIPT.md` for a narrated, scene-by-scene breakdown that you can cue into a screen recording session or AI video generator. The script covers project motivation, architecture, live demos, deployment notes, and how to continue development.
