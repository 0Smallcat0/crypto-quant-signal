# Runs one autonomous research loop iteration headlessly.
# Called daily by the Windows scheduled task "CryptoResearchLoop".
# Contract: docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md

$ErrorActionPreference = "Continue"
Set-Location "D:\Crypto-Trading"

$runDir = "docs\research\loop_runs"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $runDir "run_$stamp.log"

# Retired 2026-10-16 (docs/research/CLOSING_2026-10-16.md). The scheduled task
# is meant to be disabled; if it still fires, return here, before claude.exe,
# so the run spends no model quota and commits or pushes nothing. To restart
# the loop, record the operator order the closing record names and delete
# this block.
"skipped=retired $(Get-Date -Format o) see docs/research/CLOSING_2026-10-16.md" | Add-Content $logFile
exit 0

# Stop-condition latch: once an edge candidate is found, iterations only
# maintain/verify (the contract's stop clause) — the prompt stays the same
# because the contract itself encodes that behavior.
$prompt = "Read docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md and execute exactly one loop iteration now, following it top to bottom."

# Start marker, written before the iteration begins. Iteration 41 and the
# 2026-08-18 miss both had to be diagnosed from the Windows System event log,
# because a run killed mid-flight leaves a zero-byte file indistinguishable
# from a run that never started. With this line present, a log holding
# "started=" but no "exit=" is unambiguously an interrupted iteration.
"started=$(Get-Date -Format o)" | Add-Content $logFile

& "$env:USERPROFILE\.local\bin\claude.exe" -p $prompt `
    --dangerously-skip-permissions `
    --max-turns 400 `
    *>> $logFile

"exit=$LASTEXITCODE finished=$(Get-Date -Format o)" | Add-Content $logFile
