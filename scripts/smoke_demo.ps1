param([int]$ApiPort = 8000, [int]$WebPort = 5173)
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:$ApiPort"
function Get-Json([string]$url) { (Invoke-WebRequest -UseBasicParsing $url).Content | ConvertFrom-Json }
$ready = Get-Json "$base/api/release/readiness"
if ($ready.status -ne "READY") { throw "readiness=$($ready.status)" }
$scenarios = Get-Json "$base/api/admin/goal4a/scenarios"
$scenario = $scenarios.items | Where-Object { $_.scenario_id -eq "anyang-general-evacuation-competition" } | Select-Object -First 1
if (-not $scenario) { throw "competition scenario missing" }
$frame = Get-Json "$base/api/admin/goal4a/scenarios/$($scenario.scenario_id)/frames/0"
if ($frame.assignment.total_population -ne 562143) { throw "population mismatch" }
$comparisonBody = @{ scenario_a = $scenario.scenario_id; scenario_b = "anyang-general-evacuation-competition-shelter-outage"; time_minute = 0 } | ConvertTo-Json
$comparison = (Invoke-WebRequest -UseBasicParsing -Method Post -ContentType "application/json" -Body $comparisonBody "$base/api/admin/goal4a/compare").Content | ConvertFrom-Json
$screenBody = @{ candidate_count = 20; top_k = 1; seed = 5 } | ConvertTo-Json
$screen = (Invoke-WebRequest -UseBasicParsing -Method Post -ContentType "application/json" -Body $screenBody "$base/api/admin/goal5a/screen").Content | ConvertFrom-Json
if ($screen.exact_calls -ne 1 -or -not $screen.verified_shortlist[0].exact_verified) { throw "exact verification failed" }
$web = Invoke-WebRequest -UseBasicParsing "$(("http://127.0.0.1:$WebPort"))/admin?demo=1"
if ($web.StatusCode -ne 200) { throw "frontend unavailable" }
[pscustomobject]@{ readiness = $ready.status; scenario_id = $scenario.scenario_id; frame_status = $frame.computation_status; ab_delta_unserved = $comparison.delta_b_minus_a.unserved; ab_delta_assignment_cost_m = $comparison.delta_b_minus_a.assignment_cost; ab_delta_available_shelters = $comparison.delta_b_minus_a.available_shelters; ai_candidates = $screen.candidate_count; exact_calls = $screen.exact_calls; exact_verified = $screen.verified_shortlist[0].exact_verified; frontend_status = $web.StatusCode } | ConvertTo-Json -Compress
