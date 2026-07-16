@echo off
rem Daily signal cycle (Goal O gate 6): fetch latest close, decide, notify, score.
rem Idempotent: safe to re-run any number of times per day.
rem Exit code is preserved so Task Scheduler restart-on-failure works.
cd /d D:\Crypto-Trading || exit /b 1
if not exist data\runtime mkdir data\runtime
echo ==== daily cycle %date% %time% ==== >> data\runtime\daily_cycle.log
.\.venv\Scripts\python.exe -m scripts.run_paper_runtime --once >> data\runtime\daily_cycle.log 2>&1
set CYCLE_EXIT=%errorlevel%

rem Dead man's switch (docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md): ping on
rem success, ping /fail on failure. Missing env var degrades to a log note —
rem the ping URL is an operator credential and never lives in this file.
if defined HEALTHCHECK_PING_URL (
    if %CYCLE_EXIT%==0 (
        curl -fsS -m 10 --retry 5 "%HEALTHCHECK_PING_URL%" >nul 2>&1
    ) else (
        curl -fsS -m 10 --retry 5 "%HEALTHCHECK_PING_URL%/fail" >nul 2>&1
    )
) else (
    echo NOTE: HEALTHCHECK_PING_URL not set; dead-man-switch ping skipped >> data\runtime\daily_cycle.log
)

rem Off-disk backup of the runtime store (best-effort; never alters CYCLE_EXIT
rem so the dead-man-switch signal stays a pure cycle-health signal). Failures
rem are visible in C:\Backups\CryptoTrading\backup.log.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\backup_runtime_store.ps1 >nul 2>&1

exit /b %CYCLE_EXIT%
