# Spectre-Aegis — AO-7 Core Playground

This repo is the main playground for AO-7 + Echo.

## Layout

- `dashboards/` — HUDs and UI (e.g. `hydra/` HTML dashboards)
- `hydra/` — Core HYDRA scripts (daily, weekly, sims, leagues)
- `configs/` — Future config files for AO-7 services
- `agents/` — Future automation/agent scripts
- `tools/` — Helper scripts and utilities
- `assets/` — Images, icons, static files
- `logs/` — Local logs (usually ignored by Git)
- `tmp/` — Scratch space, experiments

## Notes

- CI workflow: `.github/workflows/ao7-ci.yml` monitors pushes (heartbeat).
- This repo is the safe sandbox for new AO-7 automations before they go live.
