# Runbook: Discord Push Notifications

The signal runtime can push each day's follow-me command to a Discord channel.
Delivery is advisory only — it never places orders and never touches money.

## Secret handling (read first)

The bot token is a credential. It is loaded **only** from environment variables
at runtime and is **never** stored in any tracked file (config, code, or logs).
The token rides in the HTTP `Authorization` header, not the URL, so error text
and logs cannot leak it.

**If a token is ever pasted into a chat, an issue, or any transcript, treat it
as compromised and regenerate it** in the Discord Developer Portal
(Applications → your app → Bot → Reset Token).

## One-time setup

1. Ensure the bot is a member of the target server and can post in the channel
   (channel → Edit Channel → Permissions → the bot role needs "Send Messages").
2. Copy the bot token (Developer Portal → Bot → Reset/Copy Token) and the
   channel id (enable Developer Mode in Discord → right-click channel → Copy ID).
3. Set them as environment variables for the account that runs the daily task.
   PowerShell, persistent for the current user:

   ```powershell
   setx DISCORD_BOT_TOKEN "<your-bot-token>"
   setx DISCORD_CHANNEL_ID "<your-channel-id>"
   ```

   (Open a NEW shell afterwards — `setx` only affects future processes.)
4. In `configs/runtime/paper_runtime.yaml`, set:

   ```yaml
   notifications:
     channel: discord
     follow_principal_usdt: "1000"   # your follow capital; sizes the message
   ```

## What gets pushed

- **Ladder-change command** (the core): on any day the target exposure changes,
  e.g. `🟢 今日指令 · ETHUSDT / 買入約 125 USDT / 原因：收盤站上 1 條均線…`.
  Delivered exactly-once with persisted retry (survives a webhook outage).
- **Single-day crash alert**: on a ≥20% single-day drop (best-effort).
- **No message on quiet days** — silence is normal for a trend system; the
  dashboard always shows the current target as the backstop for missed pings.

## Verify

```powershell
$env:DISCORD_BOT_TOKEN="<token>"; $env:DISCORD_CHANNEL_ID="<id>"
.\.venv\Scripts\python.exe -m scripts.run_paper_runtime --once
```

A same-day re-run is a no-op (`ALREADY_PROCESSED`), so this is safe to repeat.

## Scheduled task

The daily task (`scripts/run_daily_cycle.cmd`, 08:05 Asia/Taipei) runs the same
`--once` path. For it to see the credentials, the env vars must be set for the
task's user account (the `setx` above handles the interactive user; for a task
running as SYSTEM, set machine-level vars instead).

## Follow capital vs the virtual account

`follow_principal_usdt` only sizes the push message and the dashboard default.
The validation scoreboard stays on its fixed 1000 USDT virtual account — that
number must not move, because the qualification gate depends on it.
