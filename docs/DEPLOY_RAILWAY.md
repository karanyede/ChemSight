# Deploy Django Backend on Railway

Railway is one of the simplest platforms for deploying Django applications. It auto-detects your project, provisions PostgreSQL, and handles environment variables seamlessly.

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub repository connected to Railway (or use Railway CLI)

## Method 1: Deploy via Railway Dashboard (Recommended)

### 1. Create a new project

1. Go to [railway.app/new](https://railway.app/new)
2. Click **Deploy from GitHub repo**
3. Select your `ChemSight` repository
4. Railway will auto-detect the Django project

### 2. Configure the service

1. Railway should detect `backend/` as a Python project
2. If not, set **Root Directory** to `backend`
3. Railway will automatically run:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn config.wsgi:application`

### 3. Add PostgreSQL database

1. In your Railway project, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway automatically creates a `DATABASE_URL` variable
4. Django will use it via `dj-database-url` (add to requirements if needed)

### 4. Set environment variables

Click on your backend service → **Variables** tab and add:

```
DJANGO_SECRET_KEY=<generate-a-secure-random-string>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},${{RAILWAY_PRIVATE_DOMAIN}}
CORS_ALLOWED_ORIGINS=https://chemsight.vercel.app,https://*.vercel.app
CSRF_TRUSTED_ORIGINS=https://chemsight.vercel.app,https://${{RAILWAY_PUBLIC_DOMAIN}}
```

Railway provides `${{RAILWAY_PUBLIC_DOMAIN}}` automatically - use it for ALLOWED_HOSTS.

### 5. Run migrations

1. Click on your service → **Settings** → **Deploy Trigger**
2. Or use Railway CLI:
   ```bash
   railway run python manage.py migrate
   ```

### 6. Get your backend URL

- Railway assigns a URL like `chemsight-backend.up.railway.app`
- Use this as your `VITE_API_BASE_URL` in Vercel: `https://chemsight-backend.up.railway.app/api/`

## Method 2: Deploy via Railway CLI

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
# or
brew install railway
```

### 2. Login and initialize

```bash
cd backend
railway login
railway init
```

### 3. Add PostgreSQL

```bash
railway add postgresql
```

### 4. Set environment variables

```bash
railway variables set DJANGO_SECRET_KEY="your-secret-key"
railway variables set DJANGO_DEBUG=false
railway variables set DJANGO_ALLOWED_HOSTS='${{RAILWAY_PUBLIC_DOMAIN}}'
railway variables set CORS_ALLOWED_ORIGINS="https://chemsight.vercel.app"
```

### 5. Deploy

```bash
railway up
```

### 6. Run migrations

```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

## Configuration Files

Railway works best with these files in your `backend/` directory:

### railway.json (optional but recommended)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile (alternative to railway.json)

```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --noinput
```

### runtime.txt

```
python-3.11
```

## Connect Frontend to Railway Backend

In your Vercel project:

1. Go to **Settings** → **Environment Variables**
2. Set `VITE_API_BASE_URL` to your Railway URL:
   ```
   VITE_API_BASE_URL=https://chemsight-backend.up.railway.app/api/
   ```
3. Redeploy the frontend

## Health Checks

Railway doesn't require explicit health check configuration - it monitors the process automatically. The `/api/healthz/` endpoint you created will work fine.

## Troubleshooting

### Static files not loading

Add to `backend/config/settings.py`:

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

Install whitenoise:

```bash
pip install whitenoise
```

Add to `MIDDLEWARE` in settings.py:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this
    # ... rest of middleware
]
```

### Database connection issues

Railway automatically provides `DATABASE_URL`. Install:

```bash
pip install dj-database-url psycopg2-binary
```

Update `settings.py`:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}
```

## Advantages of Railway vs Render

- ✅ Simpler configuration (fewer env vars needed)
- ✅ Better error messages and logs
- ✅ Faster deployments
- ✅ Auto-restart on failure
- ✅ No health check timeout issues
- ✅ Built-in metrics and monitoring
- ✅ Free tier includes $5/month credit

## Cost

- **Free tier:** $5/month in credits (enough for small projects)
- **Hobby:** $5/month + usage
- PostgreSQL included in credits

## Next Steps

After deployment:

1. Test the `/api/healthz/` endpoint
2. Verify uploads work (check file persistence)
3. Update Vercel `VITE_API_BASE_URL`
4. Test login flow end-to-end

For persistent file storage (uploads/reports), consider:

- Railway Volumes (paid feature)
- AWS S3 / Cloudinary integration
- Railway's built-in storage (coming soon)
