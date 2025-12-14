Hydra dashboard

- Open `dashboards/hydra/index.html` in a browser (or serve the `dashboards/` directory).
- To demo without the Supabase backend, append `?mock=1` to the URL to load local mock data (`mock_games.json`).
- Example (serve locally):
 - Example (serve locally):

```bash
# from repo root
python -m http.server 8088 -d dashboards
# then open: http://localhost:8088/hydra/index.html?mock=1
# or visit root: http://localhost:8088/?mock=1 (redirects to the Hydra dashboard)
```

Testing & CI
- There is a simple E2E test under `tests/` that verifies `?mock=1` renders cards. Run:

```bash
cd tests
npm ci
npm test
```

CI will run this test and deploy `dashboards/` to GitHub Pages on pushes to `main`.
- To override the Supabase endpoint or anon key, use query params: `?supabase_url=<url>&supabase_key=<key>`.
 - To override the Supabase endpoint or anon key, use query params: `?supabase_url=<url>&supabase_key=<key>`.
 - For a production-safe approach, run the included proxy and configure it with your Supabase values (see `proxy/README.md`).
	 Then set the frontend to call the proxy endpoint (same origin) or update `hydra_supabase_url` in `localStorage`.
 - To provide a Supabase anon key for local testing without committing it, run in the browser console:

```js
localStorage.setItem('hydra_supabase_key', 'your_key_here');
localStorage.setItem('hydra_supabase_url', 'https://your.supabase.co/functions/v1/check-upcoming-games');
```

This avoids leaving secrets in the static files.

If you see `Fetch error. TypeError: Failed to fetch`, it's commonly a CORS failure when calling the Supabase Edge Function; use `?mock=1` to demo locally while fixing CORS or API wiring.

Security note: avoid committing production secrets. Use query-param overrides or inject configuration at deploy time instead of leaving long-lived keys in the static file.
