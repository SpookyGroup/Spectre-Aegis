Hydra proxy

This is a tiny Express proxy to avoid CORS and centrally manage the Supabase key.

Usage:

- Copy `.env.example` to `.env` and fill in `SUPABASE_URL` and `SUPABASE_KEY`.
- Start: `npm install && npm start`.
- Call: POST to `http://localhost:3000/api/check-upcoming-games` with the same JSON body the dashboard expects.

Security: keep the `.env` file out of source control and restrict CORS in production.

Features added for production-readiness:
- Rate limiting: per-IP window (default 30 requests / 60s). Configurable via `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW` env vars.
- Short in-memory caching of backend responses (default TTL 20s) via `CACHE_TTL` env var.
- Backend allowlist: set `ALLOWED_BACKENDS` as a comma-separated list of allowed backend URL prefixes.
- Simple request logging for observability.

Notes:
- This proxy is intended as a minimal, secure gateway for the frontend. For production, consider adding persistent cache, better rate limiting (Redis), authentication, and stricter CORS rules.

Run with Docker
--------------

Build and run with Docker:

```bash
# from repo root
docker build -t hydra-proxy:local proxy
docker run --env-file proxy/.env -p 3000:3000 hydra-proxy:local
```

Or use docker-compose (preferred for local dev):

```bash
cd proxy
docker compose up --build
```

Verify the service is healthy:

```bash
curl http://localhost:3000/health
```

Point the frontend at the proxy by setting the `supabase_url` query param or localStorage override, e.g.:

```
http://localhost:8088/hydra/index.html?supabase_url=http://localhost:3000/api/check-upcoming-games
```

If you prefer to run the proxy locally with Node, install Node.js and then:

```bash
cd proxy
npm ci
npm start
```

Mock mode (useful for CI or local dev without credentials)
-----------------------------------------------

Set `MOCK_UPSTREAM=1` to have the proxy return deterministic mock data (sourced from `dashboards/hydra/mock_games.json`). This mode is used by the provided `docker-compose.yml`.

Example (docker):

```bash
cd proxy
MOCK_UPSTREAM=1 docker compose up --build
```

Deploy to Render (low-cost / free tier)
-------------------------------------

1. Create a new Web Service on Render and connect your GitHub repo.
2. Use `proxy/render.yaml` (included) as the service definition.
3. Add `SUPABASE_URL` and `SUPABASE_KEY` as protected environment variables in Render dashboard.
4. Set `ALLOWED_BACKENDS` to your Supabase URL to restrict outgoing requests.

Render will run the service on the free plan for small workloads; this keeps the Supabase key server-side and avoids CORS issues for the static frontend.

