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

# Start marker and interpreter check, added 2026-09-29. The sibling weekly
# recorder in D:\TW-Stock-Trading lost its 2026-09-26 row to a removed
# .venv and reported nothing: PowerShell resolves a command BEFORE applying
# its redirection, so the CommandNotFoundException went to the host instead
# of the log and $LASTEXITCODE kept its null value, leaving a 94-byte file
# of blank "exit=" fields. Measured, not assumed: a probe against a
# non-existent interpreter reproduces it. These two lines were latent here
# too, on the daily track that carries this program's primary forward
# evidence, where a silent week costs seven unrecoverable rows.
"started=$(Get-Date -Format o)" | Add-Content $logFile
$python = ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    "FATAL: interpreter missing at $python - nothing ran and no shadow row was recorded." | Add-Content $logFile
    "FATAL: rebuild with: py -3.12 -m venv .venv ; .venv\Scripts\python.exe -m pip install --no-build-isolation -e .[dev]" | Add-Content $logFile
    "exit=127 finished=$(Get-Date -Format o)" | Add-Content $logFile
    exit 127
}

# Dependency probe, added 2026-09-30 (iteration 71). The Test-Path guard above
# is NOT sufficient, and that is measured rather than feared: on 2026-09-29 the
# sibling repo's .venv was rebuilt with `py -3.12 -m venv .venv` and the
# dependencies were never installed, so its interpreter existed, Test-Path
# passed, and `import yaml` / `import httpx` both failed - the 2026-10-03 run
# would have lost two more rows with the guard in place. Every recorder module
# here is behind `if __name__ == "__main__":`, so importing it runs nothing and
# is a free check that the whole dependency chain resolves.
& $python -c "import scripts.shadow_signal" *>> $logFile
if ($LASTEXITCODE -ne 0) {
    "FATAL: interpreter at $python cannot import scripts.shadow_signal (exit $LASTEXITCODE) - dependencies missing; nothing ran and no shadow row was recorded." | Add-Content $logFile
    "FATAL: repair with: $python -m pip install --no-build-isolation -e .[dev]" | Add-Content $logFile
    "exit=126 finished=$(Get-Date -Format o)" | Add-Content $logFile
    exit 126
}

# The sentinel is not decoration. If command discovery fails here, PowerShell
# leaves $LASTEXITCODE untouched - and the probe above has just set it to 0, so
# without this line a vanished interpreter would be reported as a clean run.
# Measured both ways on 2026-10-01: with the sentinel the wrapper exits 125 when
# the call cannot be resolved, 0 on a healthy run, and 1 when the recorder
# itself refuses.
$global:LASTEXITCODE = 125
& $python -m scripts.shadow_signal *>> $logFile
$recorderExit = $LASTEXITCODE
"exit=$recorderExit finished=$(Get-Date -Format o)" | Add-Content $logFile

# Repair-command note, measured 2026-09-30: plain `pip install -e .[dev]` made
# zero progress in two separate ~9-minute runs here (it hangs creating the
# isolated build environment); `--no-build-isolation` resolved and installed
# immediately, so that is the form recorded above. `pyarrow` is declared in
# pyproject and its 28 MB wheel stalls on this link in three separate attempts -
# it is imported by nothing (grep over `src/` and `scripts/` returns zero hits
# apart from this comment, which is itself the only match) and is not on the
# recorder path, so it may be skipped when repairing under time pressure.

# Exit-code propagation, added 2026-10-01 (iteration 72). Until today this
# script ended on an Add-Content, so its process exit code was that cmdlet's
# success and Windows Task Scheduler recorded LastTaskResult 0 whatever the
# recorder did. Measured, not assumed: a .ps1 whose last native call exits 1
# and then writes a log line exits 0 - reproduced twice before this change.
# The recorder does exit non-zero on the failure that costs evidence here:
# fetch_candles raises SystemExit when no public REST base url is reachable
# (scripts/shadow_signal.py:79), and that is a permanently lost row, because
# the recorder never back-fills. It appends at most one row per run, guarded by
# `rows[-1]["date"] >= decision_date` (scripts/shadow_signal.py:187), so a
# missed run DELETES a session rather than delaying it: no run happened on
# 2026-08-10, the 2026-08-11 09:48 run wrote the 2026-08-10 session, and
# 2026-08-09 is gone from this program's primary forward evidence for good.
# This change makes the scheduler's record truthful. It does not make anyone
# watch it - the tracks' own row counts and dates remain the only evidence
# that counts (iteration 71).
if ($null -eq $recorderExit) { $recorderExit = 125 }
if ($recorderExit -ne 0) {
    "FATAL: recorder exited $recorderExit - this run recorded no row, and the missed session cannot be back-filled." | Add-Content $logFile
}
exit $recorderExit
