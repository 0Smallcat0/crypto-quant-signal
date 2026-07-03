# Hardens the CryptoQuantDailySignalCycle scheduled task for the Goal O 90-day
# paper run (docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md). Task Scheduler requires
# elevation to modify this task, so the script self-elevates via UAC.
#
# What it sets and why:
#   StartWhenAvailable      run as soon as possible after a missed 08:05
#   WakeToRun               wake the machine from sleep for the run
#   AllowStartIfOnBatteries / DontStopIfGoingOnBatteries
#                           battery power must not cost a decision day
#   RestartCount 6 / RestartInterval 30min
#                           transient network failures retry within the day
#   ExecutionTimeLimit 2h   a hung cycle is killed (the single-instance lock
#                           in run_paper_runtime treats leftovers as stale)
$ErrorActionPreference = "Stop"
$taskName = "CryptoQuantDailySignalCycle"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]$identity
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Not elevated - relaunching with UAC prompt..."
    Start-Process powershell -Verb RunAs -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`""
    )
    exit
}

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -WakeToRun `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 6 `
    -RestartInterval (New-TimeSpan -Minutes 30) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew
Set-ScheduledTask -TaskName $taskName -Settings $settings | Out-Null

Write-Host "Applied. Current settings:" -ForegroundColor Green
$task = Get-ScheduledTask -TaskName $taskName
$task.Settings | Format-List WakeToRun, StartWhenAvailable, DisallowStartIfOnBatteries, `
    StopIfGoingOnBatteries, RestartCount, RestartInterval, ExecutionTimeLimit, MultipleInstances
$info = Get-ScheduledTaskInfo -TaskName $taskName
Write-Host ("Next run: " + $info.NextRunTime)
Read-Host "Press Enter to close"
