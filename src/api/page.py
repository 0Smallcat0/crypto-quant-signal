"""Static dashboard page: browser polling over the read-only JSON endpoints."""

from __future__ import annotations

DASHBOARD_HTML = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>Crypto Quant Signal MVP - Dashboard</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 2rem; background: #101418; color: #e6e6e6; }
  h1 { font-size: 1.3rem; }
  h2 { font-size: 1.05rem; margin-top: 1.6rem; border-bottom: 1px solid #333;
       padding-bottom: .3rem; }
  table { border-collapse: collapse; width: 100%; font-size: .9rem; }
  th, td { text-align: left; padding: .3rem .6rem; border-bottom: 1px solid #2a2f36; }
  .muted { color: #8a939e; font-size: .8rem; }
  .ok { color: #7bd88f; } .warn { color: #f0c674; }
  code { background: #1a2027; padding: .1rem .3rem; border-radius: 3px; }
</style>
</head>
<body>
<h1>Crypto Quant Signal MVP <span class="muted">read-only scoreboard</span></h1>
<p class="muted">Advisory signals only. This dashboard cannot place orders, change limits,
or reach any private API - permanently, by product definition.</p>

<h2>Current signals 目前訊號</h2>
<div id="signals">loading...</div>

<h2>Scoreboard account 虛擬記分板</h2>
<div id="account">loading...</div>

<h2>Latest notifications 最新通知</h2>
<div id="notifications">loading...</div>

<h2>Rejections and risk 拒單與風險</h2>
<div id="risk">loading...</div>

<h2>Validation gate 驗證閘門</h2>
<div id="gate">loading...</div>

<script>
async function poll(path, elementId, render) {
  try {
    const response = await fetch(path);
    const data = await response.json();
    document.getElementById(elementId).innerHTML = render(data);
  } catch (err) {
    document.getElementById(elementId).innerHTML =
      '<span class="warn">unavailable: ' + err + '</span>';
  }
}
function table(rows, headers) {
  if (!rows.length) { return '<p class="muted">none</p>'; }
  const head = '<tr>' + headers.map(h => '<th>' + h + '</th>').join('') + '</tr>';
  const body = rows.map(r =>
    '<tr>' + headers.map(h => '<td>' + (r[h] ?? '') + '</td>').join('') + '</tr>').join('');
  return '<table>' + head + body + '</table>';
}
function refresh() {
  poll('/api/signals/current', 'signals', d =>
    table(d.signals, ['symbol', 'exposure_fraction', 'as_of', 'reason_codes']));
  poll('/api/account', 'account', d => {
    if (d.status !== 'OK') { return '<p class="muted">no cycles yet</p>'; }
    const a = d.account;
    return '<p>equity <code>' + a.equity + '</code> · cash <code>' + a.cash +
      '</code> · realized <code>' + a.realized_pnl + '</code> · drawdown <code>' +
      a.drawdown + '</code> · as of <code>' + d.close_time + '</code></p>' +
      table(a.positions, ['symbol', 'quantity', 'average_entry_price']);
  });
  poll('/api/notifications', 'notifications', d =>
    table(d.notifications, ['decision_time', 'symbol', 'action', 'target_fraction',
                            'delta_fraction', 'decision_price', 'risk_status']));
  poll('/api/risk', 'risk', d =>
    '<h3 class="muted">risk events</h3>' +
    table(d.risk_events, ['symbol', 'event_type', 'observed_fraction']) +
    '<h3 class="muted">health</h3>' + table(d.health, ['recorded_at', 'code']));
  poll('/api/gate', 'gate', d =>
    '<p>registered trials N = <code>' + d.registered_trials_n + '</code></p>' +
    '<p>holdout: <code>' + JSON.stringify(d.holdout) + '</code></p>' +
    '<p class="muted">gate thresholds: PBO &le; ' + d.thresholds.pbo_max +
    ', DSR &ge; ' + d.thresholds.dsr_min + '</p>');
}
refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>
"""
