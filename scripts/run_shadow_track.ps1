# Appends one day to the trial-88 shadow track.
# Called daily by the Windows scheduled task "CryptoShadowTrial88",
# just after the 08:05 live runtime cycle. Read-only observer: it never
# touches the live runtime, its config, or its event store.

$ErrorActionPreference = "Continue"
Set-Location "D:\Crypto-Trading"

$runDir = "data\runtime\shadow_runs"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $runDir "shadow_$stamp.log"

& ".venv\Scripts\python.exe" -m scripts.shadow_signal *> $logFile
"exit=$LASTEXITCODE finished=$(Get-Date -Format o)" | Add-Content $logFile
