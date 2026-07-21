# Runs one autonomous research loop iteration headlessly.
# Called daily by the Windows scheduled task "CryptoResearchLoop".
# Contract: docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md

$ErrorActionPreference = "Continue"
Set-Location "D:\Crypto-Trading"

$runDir = "docs\research\loop_runs"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $runDir "run_$stamp.log"

# Stop-condition latch: once an edge candidate is found, iterations only
# maintain/verify (the contract's stop clause) — the prompt stays the same
# because the contract itself encodes that behavior.
$prompt = "Read docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md and execute exactly one loop iteration now, following it top to bottom."

& "$env:USERPROFILE\.local\bin\claude.exe" -p $prompt `
    --dangerously-skip-permissions `
    --max-turns 400 `
    *> $logFile

"exit=$LASTEXITCODE finished=$(Get-Date -Format o)" | Add-Content $logFile
