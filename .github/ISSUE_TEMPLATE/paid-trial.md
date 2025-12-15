name: Paid Trial — CI proxy + E2E
about: Small paid trial to validate CI starts the proxy in mock mode and runs the E2E test suite.
title: "Paid Trial: Start proxy container in CI, wait for /health, run E2E tests"
labels: paid-trial, help wanted
assignees: ''

---

## Summary

This paid trial task verifies that the repo's CI reliably spins up the `hydra-proxy` container in `MOCK_UPSTREAM` mode, waits for `/health`, runs the existing E2E tests under `tests/`, and tears down the container. The goal is to make local and CI runs deterministic and resilient.

Estimated time: 1–4 hours. Budget: negotiable per candidate (paid trial).

## Acceptance criteria

- CI (GitHub Actions) has a step that builds the `proxy` image, runs it with `MOCK_UPSTREAM=1`, and waits (with retries/backoff) for `http://localhost:3000/health` to return 200.
- The CI job runs `cd tests && npm test` after the proxy is healthy.
- The CI always stops and removes the container in a `finally`/`always`/`if: always()` step.
- Provide a short PR that passes CI on `main` branch (or a feature branch with CI enabled).
- Include a short description of changes and how to test locally (using `docker compose` or scripts/run-e2e-with-docker.sh).

## Deliverables

- Pull Request with changes to `.github/workflows/ci.yml` or new workflow file.
- Small README or PR note explaining how to run the test locally and what was changed.

## How to run locally (suggested)

1. Start the proxy in mock mode using Docker Compose:

```bash
cd proxy
MOCK_UPSTREAM=1 docker compose up --build
```

2. Verify health:

```bash
curl http://localhost:3000/health
```

3. Run the tests:

```bash
cd tests
npm ci
npm test
```

4. Tear down:

```bash
docker compose down
```

If you prefer, use `./scripts/run-e2e-with-docker.sh` from the repo root to run it end-to-end.

---

If selected, this trial will be paid upon acceptance (PR merged and CI green). Submit the PR and ensure CI passes. Maintainers will review and merge.
