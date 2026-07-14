"""Static dashboard page: a follow-me command card first, detail below.

Single self-contained file (no CDN, no framework) per the MVP dashboard
contract. Design priority: answer "what do I do today?" before anything else.
The user's follow capital is a browser-local display multiplier (localStorage);
it never changes the fixed virtual scoreboard the validation gate depends on.
"""

from __future__ import annotations

DASHBOARD_HTML = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>今日指令</title>
<style>
  :root {
    --bg:#0b0f14; --card:#121820; --line:#1f2937; --text:#e8eef4;
    --muted:#8b9aa8; --faint:#5c6b7a; --up:#34d399; --down:#f87171;
    --warn:#fbbf24; --accent:#5b9dff; --chip:#1a2330;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body {
    background:var(--bg); color:var(--text);
    font-family:"Segoe UI","Microsoft JhengHei",system-ui,sans-serif;
    font-size:15px; line-height:1.6; padding:22px; max-width:760px; margin:0 auto;
  }
  .num { font-variant-numeric:tabular-nums; }
  header { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
  header h1 { font-size:1.15rem; font-weight:600; }
  .dot { width:9px; height:9px; border-radius:50%; background:var(--faint); margin-left:auto; }
  .dot.ok { background:var(--up); box-shadow:0 0 6px rgba(52,211,153,.6); }
  .dot.warn { background:var(--warn); } .dot.bad { background:var(--down); }
  .status-text { color:var(--muted); font-size:.82rem; }

  /* principal bar */
  .principal { display:flex; align-items:center; gap:10px; background:var(--card);
    border:1px solid var(--line); border-radius:10px; padding:10px 14px; margin-bottom:14px;
    font-size:.9rem; color:var(--muted); flex-wrap:wrap; }
  .principal input { width:120px; background:#0b1017; border:1px solid var(--line);
    border-radius:7px; color:var(--text); padding:6px 10px; font-size:1rem; font-variant-numeric:tabular-nums; }
  .principal .hint { font-size:.78rem; color:var(--faint); }

  /* command card */
  .command { background:linear-gradient(160deg,#141c26,#0f151d);
    border:1px solid #24303f; border-radius:16px; padding:22px 24px; margin-bottom:12px; }
  .command .eyebrow { color:var(--muted); font-size:.8rem; letter-spacing:.08em; margin-bottom:6px; }
  .cmd-action { display:flex; align-items:center; gap:12px; margin:6px 0 4px; flex-wrap:wrap; }
  .verb { font-size:1.5rem; font-weight:800; padding:4px 16px; border-radius:10px; }
  .verb.buy { color:var(--up); background:rgba(52,211,153,.12); }
  .verb.sell { color:var(--down); background:rgba(248,113,113,.12); }
  .verb.hold { color:var(--muted); background:var(--chip); font-size:1.25rem; }
  .cmd-amount { font-size:1.6rem; font-weight:800; }
  .cmd-amount small { font-size:1rem; font-weight:500; color:var(--muted); }
  .cmd-block { margin-top:16px; }
  .cmd-block .lbl { color:var(--muted); font-size:.8rem; margin-bottom:3px; }
  .cmd-block .txt { font-size:.98rem; }
  .target-row { display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px dashed var(--line); }
  .target-row:last-child { border-bottom:none; }
  .target-row .hold { color:var(--up); } .target-row .flat { color:var(--faint); }
  .miss-note { margin-top:14px; padding:12px 14px; background:rgba(91,157,255,.07);
    border:1px solid rgba(91,157,255,.2); border-radius:10px; font-size:.86rem; color:#bcd3f5; }

  /* observation status */
  .obs { display:flex; align-items:center; gap:8px; background:var(--card); border:1px solid var(--line);
    border-radius:10px; padding:11px 15px; margin-bottom:20px; font-size:.86rem; cursor:pointer; }
  .obs .pill { font-size:.78rem; padding:2px 9px; border-radius:20px; background:rgba(251,191,36,.12); color:var(--warn); }
  .obs .grow { color:var(--muted); }
  .obs .chev { margin-left:auto; color:var(--faint); }

  section { margin-top:22px; }
  section > h2 { font-size:.82rem; color:var(--muted); letter-spacing:.06em; margin-bottom:12px; font-weight:600; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; }
  .cards2 { display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); }
  .empty { color:var(--faint); }

  /* asset ladder */
  .asset-head { display:flex; align-items:baseline; gap:8px; margin-bottom:8px; }
  .asset-name { font-weight:700; }
  .asset-frac { margin-left:auto; font-size:1.15rem; font-weight:700; }
  .ladder { display:flex; gap:4px; margin:6px 0 10px; }
  .rung { flex:1; height:9px; border-radius:3px; background:var(--chip); }
  .rung.on { background:linear-gradient(90deg,#3b82f6,#5b9dff); }
  .chips { display:flex; flex-wrap:wrap; gap:5px; }
  .chip { font-size:.76rem; padding:2px 8px; border-radius:20px; background:var(--chip); color:var(--faint); }
  .chip.on { color:var(--up); background:rgba(52,211,153,.1); }
  .asset-note { color:var(--muted); font-size:.82rem; margin-top:8px; }

  /* scoreboard */
  .score-row { display:flex; flex-wrap:wrap; gap:22px; align-items:flex-end; }
  .metric .label { color:var(--muted); font-size:.76rem; }
  .metric .value { font-size:1.35rem; font-weight:700; }
  .metric .value.big { font-size:1.7rem; }
  .pos { color:var(--up); } .neg { color:var(--down); }
  svg.spark { width:100%; height:70px; margin-top:12px; display:block; }
  .positions { width:100%; border-collapse:collapse; margin-top:10px; font-size:.86rem; }
  .positions th { text-align:left; color:var(--faint); font-weight:500; padding:3px 8px 3px 0; }
  .positions td { padding:3px 8px 3px 0; border-top:1px solid var(--line); }
  .scoreboard-note { color:var(--faint); font-size:.78rem; margin-top:10px; }

  .kv { display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid var(--line); font-size:.86rem; }
  .kv:first-child { border-top:none; } .kv .k { color:var(--muted); }
  .bar { height:7px; border-radius:4px; background:var(--chip); overflow:hidden; margin:6px 0 12px; }
  .bar > div { height:100%; background:linear-gradient(90deg,#3b82f6,#34d399); }
  .badge { font-size:.76rem; padding:2px 9px; border-radius:20px; }
  .badge.ok { color:var(--up); background:rgba(52,211,153,.1); }
  .badge.warn { color:var(--warn); background:rgba(251,191,36,.1); }
  .risk-item { display:flex; gap:9px; padding:6px 0; border-top:1px solid var(--line); font-size:.85rem; }
  .risk-item:first-child { border-top:none; }
  .risk-when { color:var(--faint); white-space:nowrap; }

  details summary { cursor:pointer; color:var(--muted); font-size:.86rem; padding:8px 2px; user-select:none; }
  details summary:hover { color:var(--text); }
  table.log { width:100%; border-collapse:collapse; font-size:.83rem; }
  table.log th { text-align:left; color:var(--faint); font-weight:500; padding:5px 8px 5px 0; border-bottom:1px solid var(--line); }
  table.log td { padding:5px 8px 5px 0; border-bottom:1px solid #0e141b; }
  .side-buy { color:var(--up); } .side-sell { color:var(--down); }
  .code { color:var(--faint); font-family:Consolas,monospace; font-size:.74rem; }
  footer { margin-top:26px; color:var(--faint); font-size:.76rem; line-height:1.7; }
  footer a { color:var(--muted); }
  .err { color:var(--down); font-size:.85rem; }
</style>
</head>
<body>

<header>
  <h1>今日指令</h1>
  <span class="dot" id="statusDot"></span>
</header>
<div class="status-text" id="statusText" style="margin:-8px 0 14px"></div>

<div class="principal">
  我的跟單本金
  <input id="principalInput" class="num" type="number" min="1" step="1" value="1000">
  USDT
  <span class="hint">— 改一次即可，之後所有金額用它換算（只影響顯示，不影響驗證帳戶）</span>
  <span class="hint" id="principalWarn" style="color:var(--warn)"></span>
</div>

<div class="command" id="commandCard"><div class="empty">載入中…</div></div>

<div class="obs" id="obsBar" onclick="document.getElementById('gateSection').scrollIntoView({behavior:'smooth'})">
  <span class="pill" id="obsPill">觀察期</span>
  <span class="grow" id="obsText">載入中…</span>
  <span class="chev">看細節 ▾</span>
</div>

<section>
  <h2>目前各標的狀態</h2>
  <div class="cards2" id="assetGrid"></div>
</section>

<section>
  <h2>跟單成績（虛擬記分板）</h2>
  <div class="card">
    <div class="score-row" id="scoreRow"><div class="empty">載入中…</div></div>
    <svg class="spark" id="spark" preserveAspectRatio="none" viewBox="0 0 600 70"></svg>
    <div id="positionsWrap"></div>
    <div class="scoreboard-note">此為系統的虛擬驗證帳戶（假設從觀察期第一天起完全照做）。%報酬與本金無關；金額已按你的本金估算。<br>
      此策略歷史最大回撤約 52%——這是預期內的正常範圍，規則會在回撤中自動減碼。若無法承受這種浮虧，唯一該做的決定是把跟單本金降到能承受的水位。</div>
  </div>
</section>

<section id="gateSection">
  <h2>產品驗證進度</h2>
  <div class="cards2">
    <div class="card"><div id="gateBody" class="empty">載入中…</div></div>
    <div class="card"><h2 style="margin-bottom:10px">風險與系統健康</h2><div id="riskBody" class="empty">載入中…</div></div>
  </div>
</section>

<details style="margin-top:20px">
  <summary>▸ 明細紀錄（通知 / 成交 / 拒單）</summary>
  <div style="margin-top:10px; display:grid; gap:12px">
    <div class="card"><h2 style="margin-bottom:10px;font-size:.82rem;color:var(--muted)">通知歷史</h2><div id="notifLog" class="empty">—</div></div>
    <div class="card"><h2 style="margin-bottom:10px;font-size:.82rem;color:var(--muted)">記分板成交</h2><div id="fillLog" class="empty">—</div></div>
    <div class="card"><h2 style="margin-bottom:10px;font-size:.82rem;color:var(--muted)">被拒行動</h2><div id="rejLog" class="empty">—</div></div>
  </div>
</details>

<footer>
  本頁為唯讀記分板：無法下單、無法變更風險限制、永不接觸私有 API。訊號為系統性規則輸出，非投資建議；下單由你手動執行。
  <span id="refreshStamp"></span>
</footer>

<script>
"use strict";
const TAIPEI_OFFSET = 8 * 3600 * 1000;
const SMA = { 20: "20日線", 65: "65日線", 150: "150日線", 200: "200日線" };
const CODE_TEXT = {
  DISASTER_SINGLE_DAY_DROP: "單日重挫警報", REEVALUATE_REQUIRED: "建議重新評估",
  STALE_DATA_HALT: "資料過期：暫停加倉", MISSED_DAYS: "缺漏決策日",
  WARMUP_INSUFFICIENT_HISTORY: "暖身中（歷史不足200日）",
  NOTIFICATION_DELIVERY_FAILED: "通知投遞失敗（自動重試）",
  ORDER_WITHOUT_FILL_SKIPPED: "偵測未完成訂單，已安全跳過",
  DRAWDOWN_PAUSE: "回撤保護：暫停新倉", DAILY_LOSS_PAUSE: "單日虧損保護：暫停新倉",
  MIN_NOTIONAL_NOT_MET: "金額低於最小門檻", EXCHANGE_MIN_NOTIONAL_NOT_MET: "低於交易所最小金額",
  ZERO_QUANTITY_AFTER_ROUNDING: "數量過小（捨入後為零）",
};
const codeText = (c) => CODE_TEXT[c] || c;

const money = (x) => Number(x).toLocaleString("zh-TW", { maximumFractionDigits: 0 });
const money2 = (x) => Number(x).toLocaleString("zh-TW", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pct = (x, dp = 1) => (Number(x) * 100).toFixed(dp) + "%";
const qty = (x) => Number(x).toLocaleString("zh-TW", { maximumFractionDigits: 6 });
const mmdd = (iso) => { const d = new Date(iso); return `${d.getUTCMonth() + 1}月${d.getUTCDate()}日`; };
const ymd = (iso) => { const d = new Date(iso); return `${d.getUTCFullYear()}/${d.getUTCMonth() + 1}/${d.getUTCDate()}`; };
const esc = (s) => String(s).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
const daysBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);

function getPrincipal() {
  const v = Number(localStorage.getItem("followPrincipal"));
  return v > 0 ? v : (window.__defaultPrincipal || 1000);
}
/* P1-4 本金單一來源：config 是唯一真相。本頁輸入只改顯示；
   與 config 不一致時明講 Discord 推播金額照 config 算，避免兩邊數字對不上。 */
function renderPrincipalWarn() {
  const el = document.getElementById("principalWarn");
  if (!el || !window.__defaultPrincipal) return;
  el.textContent = getPrincipal() !== window.__defaultPrincipal
    ? `⚠ Discord 推播金額以 config 本金（${money(window.__defaultPrincipal)} USDT）計算；此處輸入只影響本頁顯示`
    : "";
}
async function getJson(p) { const r = await fetch(p); if (!r.ok) throw new Error(`${p} → HTTP ${r.status}`); return r.json(); }

/* ── 指令卡 ─────────────────────────────────────────── */
function aboveCount(codes) { return [20, 65, 150, 200].filter((n) => codes.includes(`ABOVE_SMA_${n}`)).length; }

function targetBlock(signals, budgets, principal, lastChangeDays) {
  const rows = signals.map((s) => {
    const frac = Number(s.exposure_fraction), budget = Number(budgets[s.symbol] || 0);
    const usdt = frac * budget * principal;
    return frac > 0
      ? `<div class="target-row"><span><b>${esc(s.symbol)}</b></span><span class="hold num">持有 ${pct(frac * budget)} ≈ ${money(usdt)} USDT</span></div>`
      : `<div class="target-row"><span><b>${esc(s.symbol)}</b></span><span class="flat">不持有</span></div>`;
  }).join("");
  const ago = lastChangeDays === null ? "" : `<span class="hint">（上次變動：${lastChangeDays === 0 ? "今天" : lastChangeDays + " 天前"}）</span>`;
  return `<div class="cmd-block"><div class="lbl">目前目標（這是準則）${ago}</div>${rows}
    <div class="target-row"><span class="flat">其餘</span><span class="flat">現金 USDT</span></div></div>`;
}

function renderCommand(notifications, signals, account, budgets) {
  const el = document.getElementById("commandCard");
  const principal = getPrincipal();
  if (account.status !== "OK") {
    el.innerHTML = `<div class="eyebrow">今日指令</div>
      <div class="cmd-action"><span class="verb hold">尚未啟動</span></div>
      <div class="cmd-block"><div class="txt">第一個決策循環尚未執行——排程每日台北 08:05 自動運行。</div></div>`;
    return;
  }
  const cycleDate = account.close_time.slice(0, 10);
  const todays = notifications.filter((n) => n.decision_time.slice(0, 10) === cycleDate);
  const lastChangeDays = notifications.length ? daysBetween(notifications[0].decision_time, account.close_time) : null;
  const execDate = new Date(new Date(account.close_time).getTime() + TAIPEI_OFFSET);
  const execStr = `${execDate.getUTCFullYear()}/${execDate.getUTCMonth() + 1}/${execDate.getUTCDate()}`;

  let head, why;
  if (!todays.length) {
    head = `<div class="cmd-action"><span class="verb hold">✓ 今天不用動作</span></div>
      <div class="cmd-block"><div class="txt">維持目前配置即可。長期沒有動作是趨勢系統的正常狀態。</div></div>`;
    why = "";
  } else {
    head = todays.map((n) => {
      const isBuy = n.action === "INCREASE_EXPOSURE";
      const budget = Number(budgets[n.symbol] || 0);
      const deltaUsdt = Number(n.delta_fraction) * budget * principal;
      return `<div class="cmd-action">
        <span class="verb ${isBuy ? "buy" : "sell"}">${isBuy ? "買入" : "賣出"}</span>
        <span>${esc(n.symbol)}</span>
        <span class="cmd-amount num">約 ${money(deltaUsdt)} <small>USDT</small></span></div>`;
    }).join("");
    why = `<div class="cmd-block"><div class="lbl">為什麼</div><div class="txt">${
      todays.map((n) => {
        const isBuy = n.action === "INCREASE_EXPOSURE";
        const above = aboveCount(n.reason_codes);
        return `${esc(n.symbol)} 收盤站上 ${above} 條均線，趨勢${isBuy ? "轉強" : "轉弱"}；目標曝險${isBuy ? "提高" : "降低"}到預算的 ${pct(Number(n.target_fraction), 0)}。`;
      }).join("<br>")
    }</div></div>`;
  }
  const when = `<div class="cmd-block"><div class="lbl">什麼時候</div>
    <div class="txt">${execStr} 台北時間 08:10 後執行，當天內完成即可；日線訊號不必分秒必爭，隔天就以新訊號為準，<b>不要追價</b>。</div></div>`;
  const miss = `<div class="miss-note">沒跟到前一則？以上面「目前目標」為準：把手上部位調整到目標金額即可，<b>不用補買每一筆</b>。</div>`;

  el.innerHTML = `<div class="eyebrow">今日指令 · ${mmdd(account.close_time)}收盤</div>${head}${why}${when}${
    targetBlock(signals, budgets, principal, lastChangeDays)}${todays.length ? miss : ""}`;
}

/* ── 觀察期狀態 ─────────────────────────────────────── */
function renderObs(gate) {
  const paper = gate.paper_trading || {};
  const days = paper.days || 0, target = 90;
  if (gate.demo_replay) {
    // Demo store replays bundled history: cycle count is NOT live paper days.
    document.getElementById("obsPill").textContent = "離線 Demo";
    document.getElementById("obsText").innerHTML =
      `<span class="grow">本頁由內建歷史資料重播產生（${paper.cycles || 0} 個決策循環），非 90 天正式觀察期。</span>`;
    return;
  }
  document.getElementById("obsPill").textContent = `觀察期 ${days}/${target} 天`;
  document.getElementById("obsText").innerHTML =
    days >= target
      ? `<span class="grow">天數已達標，仍需通過 PBO/DSR 與 holdout 才算驗證完成。建議先紙上跟單。</span>`
      : `<span class="grow">系統仍在驗證中，還沒被證明會賺錢；建議先觀察/紙上跟單，別急著投入真錢。</span>`;
}

/* ── 各資產 ─────────────────────────────────────────── */
function renderAssets(signals, budgets) {
  const grid = document.getElementById("assetGrid");
  if (!signals.length) { grid.innerHTML = `<div class="card"><div class="empty">尚無訊號。</div></div>`; return; }
  grid.innerHTML = signals.map((s) => {
    const frac = Number(s.exposure_fraction), budget = Number(budgets[s.symbol] || 0);
    const rungs = [1, 2, 3, 4].map((i) => `<div class="rung ${frac * 4 >= i ? "on" : ""}"></div>`).join("");
    const chips = [20, 65, 150, 200].map((n) => {
      const above = s.reason_codes.includes(`ABOVE_SMA_${n}`);
      return `<span class="chip ${above ? "on" : ""}">${above ? "✓" : "✗"} ${SMA[n]}</span>`;
    }).join("");
    const summary = frac === 0 ? "全數跌破，空手觀望"
      : frac === 1 ? "站上全部四條均線，滿額持有"
      : `站上 ${aboveCount(s.reason_codes)} 條均線，持有預算的 ${pct(frac, 0)}`;
    return `<div class="card">
      <div class="asset-head"><span class="asset-name">${esc(s.symbol)}</span>
        <span class="chip">預算 ${pct(budget, 0)}</span><span class="asset-frac num">${pct(frac, 0)}</span></div>
      <div class="ladder">${rungs}</div><div class="chips">${chips}</div>
      <div class="asset-note">${summary} · 佔總帳戶 ${pct(frac * budget, 1)} · ${mmdd(s.as_of)}收盤</div></div>`;
  }).join("");
}

/* ── 記分板（按本金估算） ───────────────────────────── */
function renderScoreboard(account, equitySeries) {
  const row = document.getElementById("scoreRow");
  if (account.status !== "OK") { row.innerHTML = `<div class="empty">尚無循環資料。</div>`; return; }
  const a = account.account;
  const base = Number(account.initial_cash), principal = getPrincipal();
  const scale = base > 0 ? principal / base : 1;
  const equity = Number(a.equity), ret = base > 0 ? equity / base - 1 : 0;
  row.innerHTML = `
    <div class="metric"><div class="label">累計報酬（虛擬）</div>
      <div class="value big num ${ret >= 0 ? "pos" : "neg"}">${ret >= 0 ? "+" : ""}${pct(ret)}</div></div>
    <div class="metric"><div class="label">以你的本金估算</div>
      <div class="value num">${money(equity * scale)} <small style="font-size:.8rem;color:var(--muted)">USDT</small></div></div>
    <div class="metric"><div class="label">目前回撤</div>
      <div class="value num ${Number(a.drawdown) > 0.3 ? "neg" : ""}">−${pct(a.drawdown)}</div></div>`;

  const svg = document.getElementById("spark");
  const pts = (equitySeries.points || []).map((p) => Number(p.equity));
  if (pts.length >= 2) {
    const lo = Math.min(...pts), hi = Math.max(...pts), span = hi - lo || 1;
    const xs = (i) => (i / (pts.length - 1)) * 600, ys = (v) => 64 - ((v - lo) / span) * 56;
    const path = pts.map((v, i) => `${i ? "L" : "M"}${xs(i).toFixed(1)},${ys(v).toFixed(1)}`).join("");
    const baseY = ys(base >= lo && base <= hi ? base : lo);
    svg.innerHTML = `<line x1="0" y1="${baseY}" x2="600" y2="${baseY}" stroke="#2a3542" stroke-dasharray="3 4"/>
      <path d="${path}" fill="none" stroke="#5b9dff" stroke-width="1.8"/>
      <path d="${path} L600,70 L0,70 Z" fill="rgba(91,157,255,.08)" stroke="none"/>`;
  } else svg.innerHTML = "";

  const positions = a.positions || [];
  document.getElementById("positionsWrap").innerHTML = positions.length
    ? `<table class="positions"><tr><th>持倉</th><th>數量</th><th>平均成本</th></tr>${
        positions.map((p) => `<tr class="num"><td>${esc(p.symbol)}</td><td>${qty(p.quantity)}</td><td>${money2(p.average_entry_price)}</td></tr>`).join("")}</table>`
    : `<div class="empty" style="margin-top:8px">目前空手（全數持有 USDT）。</div>`;
}

/* ── 閘門細節 ───────────────────────────────────────── */
function renderGate(gate) {
  const paper = gate.paper_trading || {}, days = paper.days || 0, target = 90;
  const h = gate.holdout;
  const badge = !h ? `<span class="badge warn">未鎖定</span>`
    : h.spent ? `<span class="badge warn">已使用</span>` : `<span class="badge ok">已鎖定·未動用</span>`;
  const paperBlock = gate.demo_replay
    ? `<div class="num" style="font-size:1.3rem;font-weight:700">${paper.cycles || 0} <span style="font-size:.9rem;color:var(--muted)">個重播決策循環</span></div>
       <div class="kv"><span class="k">觀察期進度</span><span style="color:var(--muted)">不適用——此為離線 Demo 重播，非正式 90 天 paper</span></div>`
    : `<div class="num" style="font-size:1.3rem;font-weight:700">${days} <span style="font-size:.9rem;color:var(--muted)">/ ${target} 天 paper</span></div>
       <div class="bar"><div style="width:${Math.min(100, (days / target) * 100).toFixed(1)}%"></div></div>`;
  document.getElementById("gateBody").innerHTML = `
    <h2 style="margin-bottom:8px">驗證閘門（六關，全過才算合格）</h2>
    ${paperBlock}
    <div class="kv"><span class="k">已登記試驗 N</span><b class="num">${gate.registered_trials_n}</b></div>
    <div class="kv"><span class="k">樣本外 Holdout</span>${badge}</div>
    <div class="kv"><span class="k">過關門檻</span><span class="num" style="color:var(--muted)">PBO ≤ ${gate.thresholds.pbo_max} · DSR ≥ ${gate.thresholds.dsr_min}</span></div>`;
}

function groupRuns(rows, keyOf) {
  const g = [];
  for (const r of rows) { const k = keyOf(r); const last = g[g.length - 1];
    if (last && last.key === k) { last.count++; last.until = r.recorded_at; }
    else g.push({ key: k, row: r, count: 1, from: r.recorded_at, until: r.recorded_at }); }
  return g;
}
function renderRisk(risk) {
  const events = (risk.risk_events || []).slice(0, 4).map((e) =>
    `<div class="risk-item"><span class="risk-when num">${e.recorded_at ? ymd(e.recorded_at) : ""}</span>
      <div><b>${esc(e.symbol)}</b> ${codeText(e.event_type)}（單日 −${pct(e.observed_fraction)}）</div></div>`);
  const health = groupRuns(risk.health || [], (h) => h.code).slice(0, 4).map((g) => {
    const period = g.count > 1 ? `${ymd(g.until)}～${ymd(g.from)}·${g.count}次` : ymd(g.from);
    return `<div class="risk-item"><span class="risk-when num">${period}</span><div>${codeText(g.row.code)}</div></div>`;
  });
  const items = [...events, ...health];
  document.getElementById("riskBody").innerHTML = items.length ? items.join("") : `<div class="empty">無風險事件，一切正常。</div>`;
}

function renderLogs(notifications, fills, rejections) {
  document.getElementById("notifLog").innerHTML = notifications.length
    ? `<table class="log"><tr><th>日期</th><th>動作</th><th>標的</th><th>梯位</th><th>決策價</th></tr>${
        notifications.slice(0, 20).map((n) => { const b = n.action === "INCREASE_EXPOSURE";
          return `<tr class="num"><td>${ymd(n.decision_time)}</td><td class="${b ? "side-buy" : "side-sell"}">${b ? "買入" : "賣出"}</td>
            <td>${esc(n.symbol)}</td><td>${pct(Number(n.previous_fraction), 0)}→${pct(Number(n.target_fraction), 0)}</td><td>${money2(n.decision_price)}</td></tr>`; }).join("")}</table>`
    : `<div class="empty">尚無通知。</div>`;
  document.getElementById("fillLog").innerHTML = fills.length
    ? `<table class="log"><tr><th>日期</th><th>標的</th><th>方向</th><th>數量</th><th>成交價</th><th>手續費</th></tr>${
        fills.slice(0, 20).map((f) => `<tr class="num"><td>${f.recorded_at ? ymd(f.recorded_at) : ""}</td><td>${esc(f.symbol)}</td>
          <td class="${f.side === "BUY" ? "side-buy" : "side-sell"}">${f.side === "BUY" ? "買入" : "賣出"}</td>
          <td>${qty(f.quantity)}</td><td>${money2(f.price)}</td><td>${money2(f.fee)}</td></tr>`).join("")}</table>`
    : `<div class="empty">記分板尚無成交。</div>`;
  const rg = groupRuns(rejections, (r) => `${r.symbol}|${(r.reason_codes || []).join(",")}`).slice(0, 12);
  document.getElementById("rejLog").innerHTML = rg.length
    ? `<table class="log"><tr><th>期間</th><th>標的</th><th>原因</th></tr>${
        rg.map((g) => { const period = g.count > 1 ? `${ymd(g.until)}～${ymd(g.from)}（${g.count}次）` : ymd(g.from);
          return `<tr><td class="num" style="white-space:nowrap">${period}</td><td>${esc(g.row.symbol)}</td>
            <td>${(g.row.reason_codes || []).map(codeText).map(esc).join("、")} <span class="code">${(g.row.reason_codes || []).map(esc).join(" ")}</span></td></tr>`; }).join("")}</table>`
    : `<div class="empty">無被拒行動。</div>`;
}

function renderStatus(account, risk) {
  const dot = document.getElementById("statusDot"), text = document.getElementById("statusText");
  if (account.status !== "OK") { dot.className = "dot warn"; text.textContent = "等待第一個循環"; return; }
  const codes = (risk.health || []).map((h) => h.code);
  if (codes.includes("STALE_DATA_HALT")) { dot.className = "dot warn"; text.textContent = "資料過期：已暫停加倉，等資料恢復"; }
  else if (codes.includes("NOTIFICATION_DELIVERY_FAILED")) { dot.className = "dot warn"; text.textContent = "通知投遞異常（自動重試中）"; }
  else { dot.className = "dot ok"; text.textContent = `系統正常 · 最新收盤 ${ymd(account.close_time)}`; }
}

let _budgets = {};
async function refresh() {
  try {
    const [signals, account, notifications, gate, risk, fills, rejections, equity] = await Promise.all([
      getJson("/api/signals/current"), getJson("/api/account"), getJson("/api/notifications"),
      getJson("/api/gate"), getJson("/api/risk"), getJson("/api/fills"),
      getJson("/api/rejections"), getJson("/api/equity")]);
    _budgets = signals.risk_budgets;
    window.__defaultPrincipal = Number(signals.follow_principal) || 1000;
    if (!localStorage.getItem("followPrincipal")) document.getElementById("principalInput").value = window.__defaultPrincipal;
    renderPrincipalWarn();
    renderStatus(account, risk);
    renderCommand(notifications.notifications, signals.signals, account, _budgets);
    renderObs(gate);
    renderAssets(signals.signals, _budgets);
    renderScoreboard(account, equity);
    renderGate(gate);
    renderRisk(risk);
    renderLogs(notifications.notifications, fills.fills, rejections.rejections);
    window.__last = { notifications: notifications.notifications, signals: signals.signals, account, equity };
    const n = new Date();
    document.getElementById("refreshStamp").textContent = ` · 更新於 ${String(n.getHours()).padStart(2, "0")}:${String(n.getMinutes()).padStart(2, "0")}（每 60 秒）`;
  } catch (err) {
    document.getElementById("statusDot").className = "dot bad";
    document.getElementById("statusText").textContent = "無法取得資料";
    document.getElementById("commandCard").innerHTML = `<div class="err">${esc(err.message || err)}</div>`;
  }
}

document.getElementById("principalInput").addEventListener("input", (e) => {
  const v = Number(e.target.value);
  if (v > 0) { localStorage.setItem("followPrincipal", String(v));
    renderPrincipalWarn();
    if (window.__last) { renderCommand(window.__last.notifications, window.__last.signals, window.__last.account, _budgets);
      renderScoreboard(window.__last.account, window.__last.equity); } }
});
const saved = localStorage.getItem("followPrincipal");
if (saved) document.getElementById("principalInput").value = saved;
refresh();
setInterval(refresh, 60000);
</script>
</body>
</html>
"""
