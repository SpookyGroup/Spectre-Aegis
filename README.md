# Spectre-Aegis — AO-7 Core Repo

This repo is the central playground for AO-7 and Echo.

- `dashboards/hydra/` — Hydra sports HUD & related assets
- Future dirs: `agents/`, `scripts/`, `pipelines/`, `docs/`

Goal: one place where Termux, AO-7 automations, and GitHub Actions all meet.
# AO-7 Playground

This repository is the operational sandbox for the AO-7 ecosystem.
It contains:

- HYDRA prediction engine
- AO-7 automations
- Agents, configs, dashboards, and tools
- Active GitHub Actions (heartbeat + forge pipeline)
- Space for Sentinel, AEGIS, Catalyst, Labyrinth modules

This repository is Commander Payne’s official development ground for all future AO-7 operations.

Developer tools
---------------
- We recommend installing the BLACKBOXAI VS Code extensions for faster iteration: search for `BLACKBOXAI` in the Extensions view and sign in to your Blackbox account from the extension's sidebar. The extensions are optional but helpful for code completion, refactoring, and agent features.
- Note: workspace `.vscode` settings are intentionally not committed; add your local preferences and extension recommendations to your editor to enable them for your environment.

Quick local dev (no Node required)
---------------------------------

If you don't want to install Node locally, you can run the proxy and E2E tests using Docker (works on Windows/Mac/Linux):

```bash
# from repo root
./scripts/run-e2e-with-docker.sh
# or on Windows PowerShell:
./scripts/run-e2e-with-docker.ps1
```

This brings up the proxy in MOCK_UPSTREAM mode and runs the E2E test inside a Node container, then tears down the proxy.
