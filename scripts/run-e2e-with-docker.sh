#!/usr/bin/env bash
set -euo pipefail
ROOT=$(dirname "$(dirname "$0")")
cd "$ROOT/proxy"
echo "Starting proxy in MOCK_UPSTREAM mode..."
docker compose up -d --build

echo "Waiting for proxy health..."
for i in {1..20}; do
  if curl -sSf http://localhost:3000/health >/dev/null 2>&1; then
    echo "proxy healthy"
    break
  fi
  sleep 1
done

echo "Running E2E tests inside Node container (no local node required)"
docker run --rm -v "$ROOT/tests":/tests -w /tests node:18 bash -lc "npm ci && npm test"

echo "Tearing down proxy"
docker compose down

echo "Done"
