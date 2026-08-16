# Registers the daily "CryptoShadowTrial88" scheduled task (self-elevating).
# Runs at 08:20 local, just after the 08:05 live runtime cycle, so the
# freshly closed daily candle is available. Safe to re-run.
#
# 2026-08-16 update: the 08-10 and 08-16 08:20 slots were MISSED (Task
# Scheduler reported NumberOfMissedRuns=1 with LastTaskResult=0, and no
# shadow_*.log was produced), costing the 2026-08-09 forward row
# permanently. Cause: this script registered the task with a bare
# New-ScheduledTaskSettingsSet, whose defaults are WakeToRun=$false,
# DisallowStartIfOnBatteries=$true and StopIfGoingOnBatteries=$true. On a
# laptop that drops any slot where the machine is asleep or on battery,
# and blocks the StartWhenAvailable catch-up as well. The live 08:05 task
# hit the identical failure on 2026-07-07 and was fixed in
# scripts/harden_daily_task.ps1 (docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md);
# the same three lines of defense are applied here:
#   WakeToRun                     arm an RTC wake (the OS "allow wake
#                                 timers" gate is already on, AC + DC)
#   AllowStartIfOnBatteries /     battery power must not cost a forward row
#   DontStopIfGoingOnBatteries
#   at-logon + on-unlock trigger  catch-up that needs no RTC wake at all.
#                                 Safe because scripts/shadow_signal.py is
#                                 idempotent: it appends only when the last
#                                 closed candle is newer than the last row,
#                                 so an extra run is a no-op.
# RestartCount is deliberately NOT set: run_shadow_track.ps1 always exits 0
# (it logs the Python exit code rather than propagating it), so a
# restart-on-failure setting could never fire and would be decoration.

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File D:\Crypto-Trading\scripts\run_shadow_track.ps1"

$daily = New-ScheduledTaskTrigger -Daily -At "08:20"
$logon = New-ScheduledTaskTrigger -AtLogOn
$logon.Delay = "PT2M"   # let the network settle after wake before fetching
$sscClass = Get-CimClass -Namespace ROOT\Microsoft\Windows\TaskScheduler `
    -ClassName MSFT_TaskSessionStateChangeTrigger
$unlock = New-CimInstance -CimClass $sscClass -ClientOnly
$unlock.StateChange = 8   # 8 = SessionUnlock
$unlock.Delay = "PT2M"

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -WakeToRun `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName "CryptoShadowTrial88" `
    -Action $action -Trigger @($daily, $logon, $unlock) -Settings $settings `
    -Description "Forward-only shadow track for trial 88 (scripts/shadow_signal.py)" `
    -Force | Out-Null

$marker = "D:\Crypto-Trading\data\runtime\shadow_runs\task_registered.txt"
New-Item -ItemType Directory -Force -Path (Split-Path $marker) | Out-Null
"registered=CryptoShadowTrial88 daily=08:20 at=$(Get-Date -Format o)" | Out-File $marker -Encoding utf8
