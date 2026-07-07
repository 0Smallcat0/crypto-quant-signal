# Runbook: Daily Cycle Reliability (Goal O 90-Day Run)

The Goal O gate needs ~90 consecutive paper days from one scheduled task on one
Windows machine. This runbook closes the two silent-failure classes found in
the 2026-07-03 optimization review (`docs/plans/PRODUCT_OPTIMIZATION_PLAN.md`):

1. **The machine misses the run** (asleep, on battery, transient network
   failure, missed schedule) — fixed by hardened Task Scheduler settings.
2. **Nobody notices a missed run** — "no Discord message" already has a
   meaning (no ladder change today), so system death must alert through an
   independent channel: a dead man's switch.

## 1. One-time: harden the scheduled task (operator, elevated)

Task Scheduler requires elevation to modify the task, so this is an operator
step. Run once:

```powershell
powershell -ExecutionPolicy Bypass -File D:\Crypto-Trading\scripts\harden_daily_task.ps1
```

(Accept the UAC prompt; the script prints the settings it applied and the next
run time.) Expected after: `WakeToRun=True`, `StartWhenAvailable=True`,
`DisallowStartIfOnBatteries=False`, `RestartCount=6`, `RestartInterval=30min`,
`ExecutionTimeLimit=2h`.

What this does NOT cover: a machine that is fully powered off at 08:05 stays
off (`WakeToRun` only wakes from sleep). `StartWhenAvailable` runs the cycle
as soon as the machine is next on — the `--once` path is idempotent and a late
run is an honest late run — and the dead man's switch (below) tells you it was
late.

### Incident 2026-07-07: missed run, and the fix

The 07-07 08:05 run was missed: the machine was asleep (S3) and `WakeToRun`
did nothing because the OS-level **"Allow wake timers" gate was off**, so no
RTC wake was ever armed; `StartWhenAvailable` also did not catch up on unlock.
The 07-06 close was recovered by a manual `--once` run (idempotent; no ladder
change that day, so zero economic impact) and the paper clock stayed
continuous (07-02..07-06).

The hardening script now closes this with three independent lines of defense:
(1) it enables "Allow wake timers" so `WakeToRun` can arm an RTC wake;
(2) it adds **at-logon and on-unlock triggers** — a catch-up that does not
depend on RTC wake at all, because the idempotent cycle runs the moment you
next touch the machine (a no-op if 08:05 already succeeded); (3) it re-asserts
the daily settings. **Re-run `scripts/harden_daily_task.ps1` (elevated) once**
to apply. Expect three triggers afterward (daily / logon / unlock) and
"Allow wake timers" reading 0x1.

If reliable local wake keeps failing, the research-flagged upgrade is to move
the decision cycle to a cloud cron (it needs only public data + the Discord
push, no keys) and leave the local machine as the dashboard — deferred unless
the catch-up triggers prove insufficient.

## 2. One-time: dead man's switch (heartbeat monitor)

Pattern (standard practice, healthchecks.io docs): the daily task pings a
unique URL **after a successful cycle**; the monitor alerts you when the ping
does NOT arrive in time. Silence in Discord stays meaningful; system death
alerts via email.

1. Create a free check at <https://healthchecks.io> (or Cronitor etc.):
   - Schedule: simple, **period = 1 day**, **grace = 6 hours**
     (run is 08:05 Asia/Taipei; grace covers late wake-ups and retries).
   - Alert channel: your email (already independent of Discord). Optionally
     also add a Discord *integration* as a second alert channel — alerts about
     the system are allowed in Discord; the signal channel's silence stays
     meaningful because routine "all good" pings never post anything.
2. Copy the ping URL (looks like `https://hc-ping.com/<uuid>`). It is a
   credential-like value: keep it out of git, set it as a user environment
   variable for the account that runs the task:

   ```powershell
   setx HEALTHCHECK_PING_URL "https://hc-ping.com/<your-uuid>"
   ```

   (Open a NEW shell afterwards; scheduled tasks pick it up on next run.)
3. Done — `scripts/run_daily_cycle.cmd` already pings on success and pings
   `.../fail` on a non-zero exit. If the variable is missing, the cycle runs
   normally and logs `dead-man-switch ping skipped` (missing monitoring never
   costs a decision day).

### Verify

```powershell
$env:HEALTHCHECK_PING_URL="https://hc-ping.com/<your-uuid>"
D:\Crypto-Trading\scripts\run_daily_cycle.cmd
```

The healthchecks dashboard should show a fresh ping (a same-day rerun of the
cycle itself is an `ALREADY_PROCESSED` no-op, so this is safe to repeat).

## 3. What "alert" means when it fires

An email from healthchecks means: **the cycle did not complete today.**

1. Check the machine is on and has network.
2. Read the tail of `data\runtime\daily_cycle.log`.
3. Run manually: `.\.venv\Scripts\python.exe -m scripts.run_paper_runtime --once`
   (idempotent; safe). A late run still records the day correctly; multi-day
   gaps are recorded honestly as `MISSED_DAYS` health events.

## 4. Execution-cost snapshots (gate 6 input, automatic)

Every processed live cycle now also captures the public best bid/ask
(bookTicker) for each decision symbol right after the decision and persists it
as an `exec_quote` event (`src/runtime/quotes.py`). This is the measurement
feed for gate 6 ("measured real costs within 1.5x of the 25-30bps
assumption") — spread + decision-to-capture drift, no private API. Capture is
best-effort: a failure logs to stderr and never breaks the cycle; a same-day
rerun dedups on the `(symbol, decision day)` key.

Nothing to operate — this note exists so the event kind is documented.
If a morning capture fails (stderr shows `exec quote capture failed`), any
same-day rerun of the cycle backfills it: the decision path is an
`ALREADY_PROCESSED` no-op while the quote capture retries, and the
`(symbol, decision day)` key keeps the first successful snapshot.
