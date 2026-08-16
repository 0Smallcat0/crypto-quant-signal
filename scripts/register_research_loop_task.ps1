# Registers the daily "CryptoResearchLoop" scheduled task (self-elevating).
# Run once; safe to re-run (overwrites the task). Verifies by writing a
# marker file the non-elevated session can read.
#
# 2026-08-16 update: the 2026-08-01 and 2026-08-02 21:37 slots produced no
# log file at all, which iteration 42 left unexplained. This task carried
# the same defect as the shadow task — a bare New-ScheduledTaskSettingsSet
# defaults to WakeToRun=$false, DisallowStartIfOnBatteries=$true and
# StopIfGoingOnBatteries=$true, so on a laptop an asleep-or-on-battery
# 21:37 drops the slot silently and blocks the StartWhenAvailable catch-up.
# That is a consistent explanation for a fileless slot, not a proven one:
# the Task Scheduler operational log is disabled on this machine, so no
# per-launch record survives. The setting is corrected either way.
#
# Deliberately NOT copied from scripts/harden_daily_task.ps1: the at-logon
# and on-unlock catch-up triggers. The shadow driver is idempotent, so an
# extra fire is a no-op; a research iteration is not — every fire writes a
# LOOP_LOG entry and consumes a working session, so unlock-triggered
# catch-up would manufacture duplicate iterations. One fire per day only.

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File D:\Crypto-Trading\scripts\run_research_loop.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "21:37"
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -WakeToRun `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 6) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName "CryptoResearchLoop" `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description "Daily autonomous edge-search iteration per docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md" `
    -Force | Out-Null

$marker = "D:\Crypto-Trading\docs\research\loop_runs\task_registered.txt"
New-Item -ItemType Directory -Force -Path (Split-Path $marker) | Out-Null
"registered=CryptoResearchLoop daily=21:37 at=$(Get-Date -Format o)" | Out-File $marker -Encoding utf8
