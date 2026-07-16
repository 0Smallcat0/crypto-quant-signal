# Daily off-disk backup of the paper-run evidence (data\runtime -> C:\Backups).
# The runtime store is append-only JSONL on a single disk; losing it loses the
# 90-day qualification evidence. Scheduled task: CryptoQuantRuntimeBackup.
# Exits non-zero on robocopy failure so Task Scheduler records the failure.

$ErrorActionPreference = 'Stop'

$source   = 'D:\Crypto-Trading\data\runtime'
$destRoot = 'C:\Backups\CryptoTrading'
$stamp    = Get-Date -Format 'yyyy-MM-dd'
$logFile  = Join-Path $destRoot 'backup.log'
$keepDays = 30

New-Item -ItemType Directory -Force -Path (Join-Path $destRoot 'daily') | Out-Null

# Dated snapshot (one folder per day, idempotent re-run overwrites same day).
robocopy $source (Join-Path $destRoot "daily\$stamp") /E /R:2 /W:5 /NP /NJH /NJS | Out-Null
$dailyRc = $LASTEXITCODE

# Rolling mirror of the current state.
robocopy $source (Join-Path $destRoot 'latest') /MIR /R:2 /W:5 /NP /NJH /NJS | Out-Null
$mirrorRc = $LASTEXITCODE

# Rotate dated snapshots older than $keepDays.
Get-ChildItem (Join-Path $destRoot 'daily') -Directory |
    Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}$' -and $_.CreationTime -lt (Get-Date).AddDays(-$keepDays) } |
    Remove-Item -Recurse -Force -Confirm:$false

# robocopy: rc < 8 means success (0=no change, 1=copied, 2/3=extras).
$worst = [Math]::Max($dailyRc, $mirrorRc)
$status = if ($worst -lt 8) { 'ok' } else { 'fail' }
Add-Content -Path $logFile -Value ("{0} {1} rc={2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $status, $worst)

if ($worst -ge 8) { exit 1 }
exit 0
