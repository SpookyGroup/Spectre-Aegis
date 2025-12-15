**Handoff & Runbook**

Purpose
-------

Short, actionable guide to hand off the project to a contractor/maintainer and verify the core flows work locally and in CI.

Quick checks (first 10 minutes)
-------------------------------
- Verify the repo builds and tests run in Docker: `./scripts/run-e2e-with-docker.sh` (or `.ps1`)
- Verify `/health` returns 200 for proxy: `curl http://localhost:3000/health`
- Confirm E2E passes: `cd tests && npm test`

Local dev (fast)
----------------
1. Start proxy (mock):

```bash
cd proxy
MOCK_UPSTREAM=1 docker compose up --build
```

2. Serve dashboards (simple static server):

```bash
python -m http.server 8088 -d dashboards
# then open: http://localhost:8088/hydra/index.html?supabase_url=http://localhost:3000/api/check-upcoming-games
```

CI runbook
----------
- CI should build `proxy` and run it with `MOCK_UPSTREAM=1` and wait for `/health` to return 200 before running E2E.
- Ensure the workflow always stops and removes the container in a teardown step.

Security
--------
- Never commit `SUPABASE_KEY` or other secrets. Use the host's secret store (Render/PAAS/GHA secrets).
- `ALLOWED_BACKENDS` should be set to limit outgoing hosts.

Common issues & fixes
---------------------
- "Fetch error" in browser: often CORS or wrong `supabase_url` — use `?mock=1` to demo while debugging.
- Docker/E2E failures: ensure `docker` is installed and the `proxy` image builds locally. Use provided helper script.

Useful links
------------
- Paid trial spec: `docs/PAID_TRIAL.md`
- Paid trial issue template: `.github/ISSUE_TEMPLATE/paid-trial.md`
- Run E2E helper: `scripts/run-e2e-with-docker.sh`
