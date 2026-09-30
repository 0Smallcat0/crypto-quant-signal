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

& $python -m scripts.shadow_signal *>> $logFile
"exit=$LASTEXITCODE finished=$(Get-Date -Format o)" | Add-Content $logFile

# Repair-command note, measured 2026-09-30: plain `pip install -e .[dev]` made
# zero progress in two separate ~9-minute runs here (it hangs creating the
# isolated build environment); `--no-build-isolation` resolved and installed
# immediately, so that is the form recorded above. `pyarrow` is declared in
# pyproject and its 28 MB wheel stalls on this link in three separate attempts -
# it is imported by nothing (grep over `src/` and `scripts/` returns zero hits
# apart from this comment, which is itself the only match) and is not on the
# recorder path, so it may be skipped when repairing under time pressure.
