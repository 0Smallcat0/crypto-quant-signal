# Registers the daily "CryptoResearchLoop" scheduled task (self-elevating).
# Run once; safe to re-run (overwrites the task). Verifies by writing a
# marker file the non-elevated session can read.

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File D:\Crypto-Trading\scripts\run_research_loop.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "21:37"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 6)

Register-ScheduledTask -TaskName "CryptoResearchLoop" `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description "Daily autonomous edge-search iteration per docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md" `
    -Force | Out-Null

$marker = "D:\Crypto-Trading\docs\research\loop_runs\task_registered.txt"
New-Item -ItemType Directory -Force -Path (Split-Path $marker) | Out-Null
"registered=CryptoResearchLoop daily=21:37 at=$(Get-Date -Format o)" | Out-File $marker -Encoding utf8
