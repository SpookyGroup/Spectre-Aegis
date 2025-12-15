Blackbox Handoff — automated reviewer prompts and canned replies

Purpose
-------

This document contains exact prompts, canned replies, and step-by-step checks for Blackbox (or any assistant) to manage the paid-trial and initial PR screening.

Primary responsibilities
------------------------
- Run the E2E verification (see `scripts/run-e2e-with-docker.sh` for a Docker-based flow).
- Review paid-trial PRs: ensure CI is green, the PR follows the PR template, and no secrets are committed.
- If PR meets acceptance criteria, leave an acceptance comment and notify the maintainer for payment.

Action prompts (copy/paste-ready)
--------------------------------

- To run tests locally (Docker):
  - "Run `./scripts/run-e2e-with-docker.sh`. If it completes successfully, report `E2E PASS` and include the proxy `/health` output."

- PR review quick checklist (use this as a comment if passing):
  - "CI green: yes/no"
  - "Proxy health check (curl http://localhost:3000/health) returned 200: yes/no"
  - "E2E run: PASS/FAIL (attach logs)"
  - "No secrets committed: yes/no"

- If PR is acceptable, use this acceptance template comment:

```
Thanks — this looks good. CI is green and E2E passed locally. Please send payment details (PayPal/GitHub Sponsors/invoice) and I'll mark this as accepted.
```

Workflows and automation
------------------------

We added two workflows to automate the paid-trial flow:
- `.github/workflows/pr-verify.yml` — runs on PR open/sync: builds the proxy in `MOCK_UPSTREAM` mode, waits for `/health`, runs the E2E tests, posts a comment on the PR with pass/fail and the Actions run URL, and cleans up the container.
- `.github/workflows/auto-triage.yml` — listens for issue comments; if a comment contains `@maintainer watch` or `@blackbox watch` it will add the `monitoring` label and post a confirmation comment.

Notes on permissions
--------------------
The workflows use the default `GITHUB_TOKEN` to post comments and labels — no extra secrets are required for basic operation. If you prefer, you can create a bot account or a dedicated token with more granular permissions and add it to the repo secrets (name it `MAINTAINER_BOT_TOKEN`) then update the workflows to use it.

- If PR fails checks, use this triage comment:

```
Thanks for the PR — I ran the checks and found issues: [list issues]. Please address these and push another commit. If you need hints: start by ensuring the proxy image builds (`Dockerfile`), the CI waits for `/health`, and teardown runs in `if: always()`.
```

How to escalate
----------------
- If a PR partially passes and you need the maintainer, tag `@SpookyGroup` and add the `needs-maintainer` label.

Notes
-----
- Use `docs/PAID_TRIAL.md`, `.github/ISSUE_TEMPLATE/paid-trial.md`, and the PR template to verify scope and acceptance criteria are met.
