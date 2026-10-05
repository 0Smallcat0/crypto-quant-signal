# The operator channel: twelve pending choices and the path that is supposed to deliver them

**Iteration 75, 2026-10-05.** Backtest-free. No registry row, no gate report, no
holdout access, no forward read, nothing frozen edited, no new script.

## The question nobody had asked

Iterations 25 and 59-62 measured what each of the October read's three tests can
**decide**. Iteration 63 did the same for the holdout, 64 for the P3 override,
65 for gate 6, 66 for the sleeve route, 67 for the engine's parameter ceiling,
68 for a new architecture, 69 for the success exit's purchasability. Iteration 74
then asked the next question down — not what the October read decides but whether
anyone can **run** it — and found it has no executor.

Every one of those iterations ends by handing the operator a choice. The contract
now counts **twelve**. Nobody had asked the question one level further out:

> **Is there a path by which the operator learns of them?**

Six of the twelve are due before **2026-10-22**, which is **17 days** away. One
deadline has already arrived.

## Method

Read-only inspection of this repository, the sibling repository, the live event
store, the Windows scheduled tasks and the process environment. Nothing was
written to `data/runtime/`, `configs/runtime/` or `src/`; no notification was
sent; no message of any kind was transmitted to the operator by this iteration.
Discord reachability was established with an unauthenticated `GET` to the public
gateway endpoint, which transmits nothing to anyone.

## FIRST FINDING — PASS, stated first because it bounds everything below

**The publication channel is not broken, and when it had something to say it was
perfect.**

- `origin/main` is `1314662`, identical to local `main`; `git rev-list --count
  origin/main..main` is **0**. All **178** commits are pushed. Every LOOP_LOG
  entry and every result document of all 74 prior iterations is on a GitHub
  remote the operator owns.
- Delivery, measured on the live store: **10** `notification` events and **10**
  `notification_delivered` markers — **100 %**, no gap, no stuck message.
- The credentials the contract's stop condition depends on are present in this
  loop's own process environment (`DISCORD_BOT_TOKEN`, 72 characters;
  `DISCORD_CHANNEL_ID`, 19 characters), `configs/runtime/paper_runtime.yaml:115`
  selects `channel: discord`, and `https://discord.com/api/v10/gateway` answers
  **HTTP 200** (`{"url":"wss://gateway.discord.gg"}`) from this host. So the
  success exit's notification step — *"send the operator a Discord notification
  via the runtime notifier if reachable"* — is **executable today**
  (`src/notify/channels.py:129`, `scripts/run_paper_runtime.py:302`).
- The lettered attention list is **a stable identifier scheme**, not drifting
  bookkeeping. Across the four consecutive published lists dated 2026-09-25,
  2026-09-30, 2026-10-01 and 2026-10-02, item `(g)` reads *"the forward tracks
  charge no trading cost"* in all four and `(k)` reads *"holdout nomination N1
  has not named the live contract since 2026-07-31"* in all four, while the count
  grows seventeen → eighteen → nineteen → twenty (→ twenty-one on 2026-10-04).

This is why what follows is a missing clause rather than a broken machine.

## SECOND FINDING — DEFECT: the research loop has no outbound path, and never had one

`scripts/run_research_loop.ps1` is **30 lines**. Its only output is
`docs/research/loop_runs/run_<stamp>.log`, and that directory is ignored at
`.gitignore:43`: **80 logs present, 0 tracked.** This iteration's own log,
`run_20261005_213701.log`, will not be committed.

The contract authorises exactly **one** outbound act — the Discord notification
inside the stop condition — and that act is conditional on a success which
iterations 66-69 measured as unreachable by every route. So every operator-facing
output this loop has ever produced has been **pull-only**: the operator must come
and read. What they must read is **9 883 lines** of `LOOP_LOG.md`, whose newest
entry alone enumerates twenty-one items inside a single paragraph.

**And the twelve choices are collected nowhere.** Searching the whole `docs/`
tree for the ordinal phrasing, `fourth` through `twelfth operator choice` appear
only in the contract's standing answer, in `LOOP_LOG.md`, and in each item's own
result document. There is no index. There is also a gap in the program's own
count: the ordinals run **fourth to twelfth** and the strings *first*, *second*
and *third operator choice* **appear nowhere in `docs/`** — so an operator who
arrives and tries to reconstruct what they owe cannot do it from these documents
alone. Two enumerations exist (twelve ordinal choices, twenty-one lettered
items) and nothing maps one onto the other.

## THIRD FINDING — DEFECT: the deadlines have no trigger

Across `src/`, `scripts/`, `tests/` and `configs/`, the strings `2026-10-22`,
`2026-10-03` and `2026-10-01` appear **three times in total**, all three inside
comments in `scripts/run_shadow_track.ps1` (lines 36, 51, 68) about last week's
unrelated wrapper repair. There is no date check, no countdown, no expiry
assertion, and **no test that fails when a declared date passes.** The suite the
loop runs bare every iteration cannot notice a deadline.

**Measured consequence, not a worry.** Item `(m)`'s deadline was **2026-10-03**.
That was **2 days ago**, and `GATE6_BASELINE_2026-07-25.md:76` still reads:

```
- [ ] Paper period >= 3 calendar months completed
```

The pull-only channel has now been tested against a real deadline once, and it
did not meet it.

## FOURTH FINDING — DEFECT: the channel that works is wired to a subject that stopped speaking 66 days ago

- **Last message delivered: `2026-07-31T00:05:02.543130+00:00` — 66 days ago.**
- Every one of the **65** events recorded after that timestamp is `health`, and
  all **66** health events spanning 2026-07-30..2026-10-04 carry the same code,
  `WARMUP_INSUFFICIENT_HISTORY`. No signal, no target, no cycle, no quote, no
  order, no fill, no notification.
- Weekly digests: **2 ever** (`2026-W29`, `2026-W30`, the last on 2026-07-26)
  against **15** ISO weeks spanned by the paper period 2026-07-03..2026-10-05.
- **Ordering defect.** `src/runtime/engine.py:202` returns on the warmup guard
  **before** `:210` reaches `self._flush_undelivered(decision_time)`, whose own
  comment at `:208-209` promises that *"a same-day rerun after a webhook outage
  still gets the message out."* For 66 consecutive days that retry path has not
  executed. **Currently immaterial and stated as such** — 10 of 10 are delivered
  and nothing is stuck. What is measured is that the channel's self-healing is
  conditional on the runtime being healthy, which is the one state in which it is
  not needed.
- **The manual channel is down too.** The one surface that would show the
  mismatch is `/api/gate` (`src/api/app.py:160-180`), which returns
  `paper_trading.days` computed from `cycles[0].recorded_at` **beside**
  `paper_trading.cycles` — **94** against **29** as of today. It is launched only
  by hand (`scripts/run_dashboard.py`; no scheduled task references it) and
  `http://127.0.0.1:8010` is **unreachable** right now, with no listener on the
  port.

**Free corroboration of iteration 72 from a second file.** The health series'
only missing date in 2026-07-30..2026-10-04 is **2026-08-09** — the same date
permanently absent from both daily shadow tracks. Two independently written files
agree the machine was down that day.

## What the operator currently owes, collected in one place for the first time

As published by iteration 74 on 2026-10-04 (its letters, verbatim subjects, its
own deadline assignments). **This table is the only repair available to this
iteration without an unauthorised act, and it is itself pull-only.**

| Item | Subject | Deadline | Status today |
|---|---|---|---|
| (g) | the forward tracks charge no trading cost | 2026-10-22 | **17 days** |
| (h) | trial 118's forward input is anchored only on close | 2026-10-22 | **17 days** |
| (i) | the read rule states no replay depth, >= 206 bars required | 2026-10-22 | **17 days** |
| (j) | Test 2 cannot fire at 90 days | 2026-10-22 | **17 days** |
| (k) | holdout nomination N1 has not named the live contract since 2026-07-31 | 2026-10-22 | **17 days** |
| (u) | the 2026-10-22 read has no executor, no owner, no named inputs | 2026-10-22 | **17 days** |
| (m) | gate 6 cannot fail | 2026-10-03 | **PASSED 2 days ago, undeclared** |
| (l) | gate 4's variance input is analyst-controllable | none | open |
| (n) | the sleeve book cannot be graded at all | none | open |
| (o) | the gate-3 bar is unreachable; it refuses the ceiling for other columns' failures | none | open |
| (p) | gate 3 charges a novelty premium | none | open |
| (q) | gate 3's verdict is purchasable with 32 junk arms | none | open |
| (t) | the market-data host list is one entry long in practice | none | open |

Items `(a)`-`(f)`, `(r)` and `(s)` are the remaining 8 of the 21; iteration 74
assigns them no deadline state, and this iteration does not invent one.

For reference on how long the pull channel has gone unanswered: the last operator
order recorded anywhere in the contract is dated **2026-07-27**
(`AUTONOMOUS_RESEARCH_LOOP.md:33`), **70 days** ago. This is not evidence the
operator has not read — it is the measured absence of a recorded instruction, and
it is reported as that and nothing more.

## Stated against the finding, with an outside calibration that costs it

Two things cut against reading this as a scandal.

**The loop is not authorised to notify.** Iron rule 1 keeps it away from the
runtime, and the contract's only outbound clause is the stop condition's. The
absence of a research channel is therefore a **gap in the contract**, not a
failure by the loop to use something it had.

**A deadline with no alarm being missed is the modal outcome in the best-measured
comparable.** DeVito, Bacon and Goldacre (*Lancet* 2020;395:361-369, PMID
31958402) assessed compliance with the FDAAA 2007 Final Rule, which carries a
statutory one-year reporting deadline, a public registry, and a named regulator —
every enforcement affordance this program lacks. Of **4209** trials due to
report, **1722 (40.9 %; 95 % CI 39.4-42.2)** did so within the deadline;
**2686 (63.8 %)** ever did; the median delay was **424 days**, *"59 days higher
than the legal reporting requirement of 1 year"*; and compliance *"has not
improved since July, 2018."* The authors conclude *"compliance with the FDAAA
2007 is poor, and not improving"* and their proposed remedy is *"open public
audit of compliance for each individual sponsor"* — which is, structurally,
exactly the pushed public log this program already maintains. So this program sits
at the recommended remedy and still missed its first deadline; the finding is that
the remedy is **necessary and not sufficient**, not that this program is unusual.

## The loop declines to act, which is the eighth consecutive refusal

Two acts would close the gap today and both are refused here rather than taken:

1. **Sending the operator an unsolicited Discord message.** The credentials are
   present and the endpoint answers. The contract authorises this on success
   only. A loop that grants itself an interrupt channel by reading its own
   finding as an emergency has changed the rules in its own favour, which is the
   thing iterations 66, 67, 68, 69 and 74 each refused in the one case where
   making the change would have converted a fail into a pass.
2. **Writing a notifier or a deadline test.** Iteration 74 declined to write the
   October read's harness because *"a harness built against an incomplete rule
   silently fixes the four undeclared choices in code and the code then becomes
   what is cited as the rule."* The same argument applies with more force here: a
   deadline test encodes a definition of "due" and "declared" that no contract
   states, and `pytest` then becomes the authority on what the operator owes.

## Three options, operator-only

- **A — Accept the pull channel.** Read the table above and declare the six items
  due before 2026-10-22, plus `(m)`, which is already late. Costs nothing and
  changes nothing; the next deadline will arrive exactly the same way.
- **B — Authorise a bounded push.** Extend the contract's outbound clause from
  the stop condition to a research channel: at most one Discord message per
  iteration, emitted only when a declared deadline falls within N days, via the
  existing `send_text` path and the credentials already in the environment. This
  must come with a declared rate limit and a declared definition of "due",
  because otherwise the loop decides when to interrupt.
- **C — Make the deadline bind in code.** A test that fails when a declared date
  passes with its checkbox unchecked. This needs no new channel and no new
  authority: the loop already runs `pytest` bare every iteration, so the alarm
  would be a verification failure rather than a message. It is a change to the
  verification contract, which is why it is not made here — and its first run
  would fail immediately on item `(m)`, which is the point of it.

## What this iteration did not do

No notification, message, webhook call or Discord post of any kind was sent; the
only outbound requests were the unauthenticated gateway `GET` and the Step-2
literature fetches. Nothing under `configs/runtime/`, `src/`, `scripts/`, `tests/`
or any scheduled-task definition was modified. No registry row was appended — N
is still **133** — no gate report was regenerated, no return series written. The
holdout was not read, fetched or unsealed. No forward read was performed and no
forward Sharpe or drawdown was computed; the forward files were read for row
counts and dates only. No frozen pre-registration was edited. No new script. The
`(m)` checkbox was **not** ticked by this loop: declaring a gate-6 prerequisite is
the operator's act, and ticking it would be the loop settling one of the choices
it is reporting as undelivered.

## Route closed

**No proposal may treat a pending operator choice as delivered, or a declared
deadline as monitored, on the strength of its appearance in `LOOP_LOG.md`, in
this document, or in the contract's standing answer.** Publication is not
delivery, and this repository contains no mechanism that converts one into the
other.
