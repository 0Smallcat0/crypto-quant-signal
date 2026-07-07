# Hardens the CryptoQuantDailySignalCycle scheduled task for the Goal O 90-day
# paper run (docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md). Task Scheduler requires
# elevation to modify this task, so the script self-elevates via UAC.
#
# 2026-07-07 update: the 07-07 08:05 run was MISSED — the machine was asleep
# (S3) and WakeToRun did nothing because the OS-level "Allow wake timers" gate
# was off, so no RTC wake was ever armed; StartWhenAvailable also failed to
# catch up on unlock. This script now closes that gap with three independent
# lines of defense.
#
# What it sets and why:
#   Allow wake timers (AC+DC)  the OS gate WakeToRun silently depends on
#   at-logon + on-unlock trigger  catch-up that does NOT need RTC wake at all:
#                           the moment you touch the machine, the idempotent
#                           cycle runs (no-op if 08:05 already succeeded). This
#                           is the reliable line — you always wake the machine.
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

# 1. Allow wake timers (BD3B718A... under SUB_SLEEP), AC and DC, so WakeToRun
#    can actually arm an RTC wake. Without this the task's WakeToRun is inert.
$subSleep = "238C9FA8-0AAD-41ED-83F4-97BE242C8F20"
$allowWake = "BD3B718A-0680-4D9D-8AB2-E1D2B4AC806D"
powercfg /SETACVALUEINDEX SCHEME_CURRENT $subSleep $allowWake 1
powercfg /SETDCVALUEINDEX SCHEME_CURRENT $subSleep $allowWake 1
powercfg /SETACTIVE SCHEME_CURRENT
Write-Host "Wake timers enabled (AC + DC)." -ForegroundColor Green

# 2. Triggers: keep the daily 08:05, add log-on + unlock catch-up (2-min delay
#    so the network settles after wake before the cycle fetches public data).
$daily = New-ScheduledTaskTrigger -Daily -At 8:05am
$logon = New-ScheduledTaskTrigger -AtLogOn
$logon.Delay = "PT2M"
$sscClass = Get-CimClass -Namespace ROOT\Microsoft\Windows\TaskScheduler `
    -ClassName MSFT_TaskSessionStateChangeTrigger
$unlock = New-CimInstance -CimClass $sscClass -ClientOnly
$unlock.StateChange = 8   # 8 = SessionUnlock — exactly the 07-07 wake-unlock case
$unlock.Delay = "PT2M"
Set-ScheduledTask -TaskName $taskName -Trigger @($daily, $logon, $unlock) | Out-Null

# 3. Hardened settings.
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

Write-Host "`nApplied. Triggers now:" -ForegroundColor Green
(Get-ScheduledTask -TaskName $taskName).Triggers |
    Format-Table @{N = 'Type'; E = { $_.CimClass.CimClassName -replace 'MSFT_Task', '' } }, `
    StartBoundary, Delay -AutoSize
Write-Host "Settings:" -ForegroundColor Green
$task = Get-ScheduledTask -TaskName $taskName
$task.Settings | Format-List WakeToRun, StartWhenAvailable, DisallowStartIfOnBatteries, `
    StopIfGoingOnBatteries, RestartCount, RestartInterval, ExecutionTimeLimit, MultipleInstances
Write-Host "Wake timers (expect 0x1):"
powercfg /query SCHEME_CURRENT $subSleep $allowWake | Select-String "Current AC|Current DC"
$info = Get-ScheduledTaskInfo -TaskName $taskName
Write-Host ("Next run: " + $info.NextRunTime)
Read-Host "Press Enter to close"
