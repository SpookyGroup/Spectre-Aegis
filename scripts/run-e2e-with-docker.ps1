Param()
Write-Host "Starting proxy in MOCK_UPSTREAM mode..."
Push-Location -Path "$PSScriptRoot\..\proxy"
docker compose up -d --build

Write-Host "Waiting for proxy health..."
$ok = $false
for ($i=0; $i -lt 20; $i++) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -Uri http://localhost:3000/health -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $ok = $true; break }
  } catch { }
  Start-Sleep -Seconds 1
}
if (-not $ok) { Write-Host "Proxy didn't become healthy in time." }

Write-Host "Running E2E tests inside Node container (no local node required)"
docker run --rm -v "${PWD}\..\tests:/tests" -w /tests node:18 bash -lc "npm ci && npm test"

Write-Host "Tearing down proxy"
docker compose down
Pop-Location
Write-Host "Done"
