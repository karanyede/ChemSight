# Deploy the Web Frontend on Vercel

This guide walks through hosting the Vite/React SPA (`web-frontend/`) on Vercel so it contacts your production Django API instead of `localhost`.

## 1. Create the project

1. Open your Vercel dashboard and import the repository. Point the root to the `web-frontend/` directory so the build command runs inside the SPA workspace.
1. Select **Node.js 20+** (Vercel defaults to Node 20 on the latest platform) and keep the default `npm install`/`npm run build` lifecycle.

## 2. Build settings

- **Root Directory:** `web-frontend`
- **Install Command:** `npm ci`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

Vercel automatically deploys the generated `dist/` files as a static site.

## 3. Environment variables

Define production values under the project’s **Environment Variables** (Vercel dashboard → Settings → Environment Variables). Prefix any value with `VITE_` so Vite replaces them at build time:

| Variable            | Description                       | Suggested value                   |
| ------------------- | --------------------------------- | --------------------------------- |
| `VITE_API_BASE_URL` | Remote Django API base            | `https://api.yoursite.com/api/`   |
| `VITE_AUTH_DOMAIN`  | Optional Appwrite / auth base URL | `https://appwrite.example.com/v1` |

If you add more runtime configuration (feature flags, analytics, etc.), prefix them with `VITE_` too.

## 4. Backend readiness reminder

- Ensure the Django backend exposes the same base URL that you assign to `VITE_API_BASE_URL`. If the API is hosted at `https://api.chemical-equipment.app/api/`, the frontend must use that exact URL.
- Configure `ALLOWED_HOSTS` in `backend/.env` (or the settings module) to include the backend domain (for example, `api.chemical-equipment.app`).
- Update `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and any other host-based security lists to include the Vercel origin (e.g., `https://*.vercel.app`) so the browser can request the API.
- After deployment, inspect the browser console/network tab; `ERR_CONNECTION_REFUSED` for `/api/auth/login/` usually means the SPA still points to `localhost:8000` or the Django server is down. Confirm the Vercel env var and that the backend is accepting HTTPS requests at the configured host.

## 5. Redeploy

After updating environment variables or backend settings, trigger a redeploy from the Vercel dashboard so the SPA rebuilds with the correct `VITE_API_BASE_URL`. Monitor the deployment logs and the browser console to ensure the login flow completes successfully.
