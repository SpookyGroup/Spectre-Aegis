Hiring prompts, screening checklist, and evaluation rubric

Use these prompts when messaging candidates, reviewing PRs, and conducting the paid trial.

Initial message to candidate
----------------------------
Hi <name>,

Thanks for your interest. We have a short paid trial: "Start proxy container in CI (MOCK_UPSTREAM=1), wait for /health, run E2E tests, and tear down." Estimated 1–4 hours. If you accept, open a PR and when CI is green we'll review and pay.

Trial PR review checklist
------------------------
- Does CI build the `proxy` image and run it in mock mode? (check logs)
- Does CI poll `/health` and wait until it returns 200 before running tests?
- Are teardown steps present in `if: always()` or an equivalent `finally` step?
- Does the PR include clear local reproduction steps and documentation?
- Are changes minimal and well-scoped?

Screening questions (short interview)
-----------------------------------
1. Describe how you'd protect secrets (Supabase key) when a static frontend needs to call server-side endpoints.
2. How would you make the proxy more robust for production (caching, rate limiting, monitoring)?
3. Tools: which CI runners and container registries have you used; comfortable with Docker, GitHub Actions, and small Node services?

Evaluation rubric (1–5)
----------------------
- Code correctness & tests: 40% (Are tests passing and PR clean?)
- Communication & docs: 25% (Is the PR descriptive and reproducible?)
- Speed & scope control: 20% (Completed within expected time and limited scope) 
- Security awareness: 15% (No secrets committed, allowlist enforced)

Suggested reply when offering acceptance
--------------------------------------
Thanks — PR looks good and CI is green. Please provide a short note with how you'd like to be paid (PayPal, GitHub Sponsors, or invoice). We'll transfer the agreed payment on acceptance.
