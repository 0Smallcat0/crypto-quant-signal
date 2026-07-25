# Registers the daily "CryptoShadowTrial88" scheduled task (self-elevating).
# Runs at 08:20 local, just after the 08:05 live runtime cycle, so the
# freshly closed daily candle is available. Safe to re-run.

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File D:\Crypto-Trading\scripts\run_shadow_track.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "08:20"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 20)

Register-ScheduledTask -TaskName "CryptoShadowTrial88" `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description "Forward-only shadow track for trial 88 (scripts/shadow_signal.py)" `
    -Force | Out-Null

$marker = "D:\Crypto-Trading\data\runtime\shadow_runs\task_registered.txt"
New-Item -ItemType Directory -Force -Path (Split-Path $marker) | Out-Null
"registered=CryptoShadowTrial88 daily=08:20 at=$(Get-Date -Format o)" | Out-File $marker -Encoding utf8
