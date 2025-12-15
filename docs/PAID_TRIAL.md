Paid Trial: CI proxy + E2E
==========================

Purpose
-------

This paid trial is a small, well-scoped piece of work intended to verify CI reliability and provide a low-effort, paid onboarding task for contractors. It validates end-to-end behavior for the `hydra-proxy` mock mode and E2E tests.

Task
----

1. Ensure the CI workflow builds the `proxy` Docker image and runs it with `MOCK_UPSTREAM=1`.
2. Add a robust wait-for-health step that polls `http://localhost:3000/health` with retries/backoff up to a reasonable timeout (e.g., 20s).
3. Run the existing E2E tests (`cd tests && npm test`) after the proxy is confirmed healthy.
4. Always tear down the proxy container in a cleanup step.

Acceptance criteria
-------------------

- A PR that changes CI (or adds a new workflow) and passes on GitHub Actions.
- Local reproduction steps are documented in the PR.
- The change is small and well-tested; it should not modify production secrets or commit keys.

How to test locally
-------------------

Use the included helper scripts (works with Docker):

```bash
./scripts/run-e2e-with-docker.sh
# or PowerShell on Windows:
./scripts/run-e2e-with-docker.ps1
```

Deliverable
-----------

- A Pull Request against `main` with clear description and acceptance checklist.

Payment
-------

This trial is compensated on completion/acceptance. Payment details are managed off-repo between the maintainer and contractor.
