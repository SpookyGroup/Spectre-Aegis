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
