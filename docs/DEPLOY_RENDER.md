# Deploy the Django Backend on Render

This guide explains how to host the backend (`backend/`) on Render so it can serve a production-ready API that the Vercel frontend can call.

## 1. Provision a PostgreSQL database (recommended)

1. In the Render dashboard go to **New > PostgreSQL**.
1. Choose a plan (Start on the free tier if you are experimenting) and deploy the database in the same region as your app.
1. After creation, copy the `DATABASE_URL` Render provides—it looks like `postgres://user:pass@host:5432/dbname`.
1. Set that value as `DATABASE_URL` in the Django service’s environment variables (see step 3).

If you prefer to keep SQLite for experimentation you can skip this step, but the built-in SQLite file will not persist across deploys without extra storage configuration.

## 2. Create the Render Web Service

1. Create a **New Web Service** pointing to the `backend/` directory of this repository.
1. Select **Python 3.11+** and use the following commands:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
1. Ensure `gunicorn` is listed in `backend/requirements.txt` so the binary is available during deployment; if you add it, Render will install it during the next build. Restart the deploy if the previous run failed with `gunicorn: command not found`.
1. Set the **Environment** to `Python` and ensure the `Instance type`/`Plan` matches your expected traffic.

## 3. Configure required environment variables

Add the following (all on Render’s Environment tab for the service):

| Name                                         | Value / guidance                                                                                                            |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `DJANGO_SECRET_KEY`                          | Use a secure random string (never check this into Git).                                                                     |
| `DJANGO_DEBUG`                               | `false` for production.                                                                                                     |
| `DJANGO_ALLOWED_HOSTS`                       | Include your Render service domain (e.g., `backend-yourapp.onrender.com`) and any custom domains you add.                   |
| `DATABASE_URL`                               | From step 1 (skip if using SQLite). Render exposes this automatically if you attach the Postgres add-on.                    |
| `CORS_ALLOWED_ORIGINS`                       | JSON list or comma-separated hosts that will call the API (include `https://chemsight.vercel.app` and any preview domains). |
| `CSRF_TRUSTED_ORIGINS`                       | Mirror the same origins as CORS if you use session auth.                                                                    |
| `DEFAULT_FILE_STORAGE`                       | Leave as default unless storing uploads in S3; your current setup writes to `uploads/` and `reports/`.                      |
| `DJANGO_TIME_ZONE`                           | Optional; defaults to `UTC`.                                                                                                |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | If you wire up Redis in Render; otherwise keep defaults for local development.                                              |

## 4. Run database migrations and seeds

- After each deployment or when you update models, run `python manage.py migrate` using Render’s **Shell** console for the service.
- If you have fixtures or data seeds, execute them via the same Shell session.

## 5. Attach a custom domain and HTTPS

1. In Render’s DNS settings, add your chosen domain (for example, `api.chemsight.app`).
1. Once the domain is verified, Render automatically provisions TLS.
1. Update `DJANGO_ALLOWED_HOSTS` to include the custom hostname so Django does not reject requests.

## 6. Connect the frontend to this backend

- In your Vercel project, set `VITE_API_BASE_URL=https://<your-domain>/api/` (matching the Render service or custom domain).
- Remember to redeploy the Vercel SPA after updating the environment variable so it builds with the right endpoint.
- Add the Vercel origin (`https://chemsight.vercel.app`) to `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS` so the browser can successfully call `/api/auth/login/` and other endpoints.

## 7. Keep uploads persistent

The backend writes uploads to `uploads/` and reports to `reports/` under the repository root. Render’s ephemeral filesystem means these directories will reset between deploys. Consider one of the following if persistence is required:

- Mount a Persistent Disk (Render offers this on paid plans) and point `UPLOAD_ROOT`/`REPORT_ROOT` to that path via environment variables.
- Switch to an external blob store (e.g., AWS S3) and update Django storage settings accordingly.

## References

- `backend/config/settings.py` (ALLOWED_HOSTS, CORS, CSRF, and storage roots)
- `docs/DEPLOY_VERCEL.md` (ensuring the frontend points to the same API host)
