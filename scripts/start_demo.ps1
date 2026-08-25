param(
  [int]$ApiPort = 8000,
  [int]$WebPort = 5173
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Missing .venv Python runtime" }
if (-not (Test-Path (Join-Path $root "models\scenario_triage\model.joblib"))) { throw "Missing AI model bundle" }
if (-not (Test-Path (Join-Path $root "data\processed\anyang_facilities.json"))) { throw "Missing processed facility artifact" }

function Wait-Http([string]$url, [int]$seconds = 30) {
  for ($i = 0; $i -lt $seconds; $i++) {
    try { return Invoke-WebRequest -UseBasicParsing $url }
    catch { Start-Sleep -Seconds 1 }
  }
  throw "Health check timed out: $url"
}

$apiProbe = try { Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$ApiPort/api/release/readiness" } catch { $null }
if (-not $apiProbe) {
  Start-Process -WindowStyle Hidden -FilePath $python -ArgumentList @("-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", "$ApiPort") -WorkingDirectory $root | Out-Null
  $apiProbe = Wait-Http "http://127.0.0.1:$ApiPort/api/release/readiness"
}
$readiness = $apiProbe.Content | ConvertFrom-Json
if ($readiness.status -ne "READY") { $readiness | ConvertTo-Json -Depth 8; throw "Backend readiness is not READY" }

$webProbe = try { Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$WebPort/admin?demo=1" } catch { $null }
if (-not $webProbe) {
  Get-Command npm -ErrorAction Stop | Out-Null
  Start-Process -WindowStyle Hidden -FilePath "cmd.exe" -ArgumentList @("/c", "npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "$WebPort") -WorkingDirectory $root | Out-Null
  $webProbe = Wait-Http "http://127.0.0.1:$WebPort/admin?demo=1"
}
Write-Output "SAFE-Twin Anyang demo ready: http://127.0.0.1:$WebPort/admin?demo=1"
Write-Output "Backend readiness: $($readiness.status); AI: $($readiness.ai_decision)"
