#!/usr/bin/env python3
"""Generate dashboard.html from the markdown journals in this repo.

Reads trading_journal.md (live daily/weekly watch entries) and levels_watch.md
(current levels) and combines them with a curated summary of the 21 backtest
runs in backtest_journal.md into a single static HTML dashboard.

Run: python3 generate_dashboard.py
"""
import json
import re
import sys
from pathlib import Path

import ta_charts

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Parse trading_journal.md — one card per dated entry
# ---------------------------------------------------------------------------
ENTRY_RE = re.compile(
    r"### (\d{4}-\d{2}-\d{2})(?: \d{2}:\d{2})? — (\S+)\n"
    r"(.*?)(?=\n### |\Z)",
    re.S,
)
FIELD_RE = re.compile(r"- (.+?): (.*?)(?=\n- |\Z)", re.S)


def parse_trading_journal():
    text = (ROOT / "trading_journal.md").read_text()
    entries = []
    for m in ENTRY_RE.finditer(text):
        date, pair, body = m.group(1), m.group(2), m.group(3)
        fields = {}
        for fm in FIELD_RE.finditer(body):
            key = fm.group(1).strip().lower()
            val = re.sub(r"\s+", " ", fm.group(2)).strip()
            fields[key] = val

        snapshot = fields.get("market snapshot", "")
        rec = fields.get("recommendation/reasoning", "")
        review = fields.get("review (filled in later)", "")

        regime_m = re.search(r"Regime (BULL|BEAR)", snapshot)
        price_m = re.search(r"price ~?€?([\d,]+(?:\.\d+)?)", snapshot)
        verdict = rec.split(".")[0].strip() if rec else ""
        pending = review.strip().lower().startswith("_pending_")

        entries.append({
            "date": date,
            "pair": pair,
            "regime": regime_m.group(1) if regime_m else "?",
            "price": price_m.group(1) if price_m else "?",
            "snapshot": snapshot,
            "verdict": verdict,
            "reasoning": rec,
            "review": "Pending" if pending else review,
        })
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


# ---------------------------------------------------------------------------
# Parse levels_watch.md — current levels / last reviewed line
# ---------------------------------------------------------------------------
def parse_levels():
    text = (ROOT / "levels_watch.md").read_text()
    last_reviewed = re.search(r"Last reviewed: (.+)", text)
    levels = {}
    for pair, label in (("BTC", "BTC/EUR"), ("ETH", "ETH/EUR")):
        section = re.search(rf"## {re.escape(label)}\n(.*?)(?=\n## |\Z)", text, re.S)
        if not section:
            continue
        sec = section.group(1)
        down = re.search(r"Downside trigger.*?€([\d,]+)", sec)
        up = re.search(r"Upside trigger.*?€([\d,]+)", sec)
        state = re.search(r"Current state: (.+)", sec)
        levels[pair] = {
            "downside": down.group(1) if down else "?",
            "upside": up.group(1) if up else "?",
            "state": state.group(1).strip() if state else "",
        }
    return {
        "last_reviewed": last_reviewed.group(1).strip() if last_reviewed else "?",
        "levels": levels,
    }


# ---------------------------------------------------------------------------
# Curated summary of backtest_journal.md (21 runs) — hand-extracted highlights
# ---------------------------------------------------------------------------
BACKTEST_RUNS = [
    dict(n=1, title="BTC/USD daily, 5 weeks (hindsight)", status="info",
         result="Net +$738.70 (+7.39%)",
         takeaway="Best result followed a confirmed trend break, not a reversal call."),
    dict(n=2, title="BTC/USD weekly YTD, 23 calls (hindsight-contaminated)", status="info",
         result="Net +$4,742 (+47%), 70% hit rate",
         takeaway="Outlier result — full dataset was in context; flagged as not representative."),
    dict(n=3, title="BTC/USD weekly, strictly blind, 9 calls", status="info",
         result="Net -$1,316 (-13.2%), 33% hit rate",
         takeaway="Calling reversals/bounces was the weak spot; FLAT during chop was correct."),
    dict(n=4, title="BTC+ETH weekly, strictly blind, 11 calls each", status="info",
         result="Net +$4,167 across both, 60% hit rate",
         takeaway="Confirmed-break trades won; reversal calls lost. Reinforced Run 3 lesson."),
    dict(n=5, title="BTC/EUR daily blind — hybrid weekly/daily-when-flat", status="adopted",
         result="Net +€35.60 (+3.56%), 1W/1L over 6 weeks",
         takeaway="Adopted the hybrid, but required a break-quality filter (>=0.5-1% margin) to avoid whipsaw."),
    dict(n=6, title="Donchian breakout vs buy-and-hold (mechanical, 2yr)", status="key",
         result="BTC +30% / ETH -25.7% full; OOS Sharpe negative both",
         takeaway="THE key finding: no demonstrated alpha OOS, but trend-following roughly halves max drawdown vs buy-and-hold. Risk-reduction tool, not alpha engine."),
    dict(n=7, title="Stop-loss / take-profit brackets vs trailing stop", status="rejected",
         result="Every fixed TP turned the +30% BTC trailing result negative",
         takeaway="Adopted: trailing Donchian stop only, no fixed take-profit ever, no 'always-in'."),
    dict(n=8, title="A/B: discretionary human+news vs mechanical rule", status="adopted",
         result="Mechanical matched/beat discretionary in 3 of 4 windows",
         takeaway="Human+news layer demoted to risk oversight (veto/sizing), not entry signals."),
    dict(n=9, title="EMA 21/55 + RSI>50 crossover vs Donchian", status="adopted",
         result="EMA: BTC +37.6%/0.79 Sharpe, ETH +19.7%/0.47 Sharpe",
         takeaway="EMA cross adopted as a PARALLEL system. RSI filter inert; 'exit below 55 EMA' hurt — not adopted."),
    dict(n=10, title="Market cycles + 200d-MA bear-regime filter", status="adopted",
         result="200d filter: helped ETH, hurt BTC (whipsaw)",
         takeaway="Regime used as CONTEXT (sizing/caution), not a hard entry gate. Calendar-based cycle timing rejected (n=3, too fragile)."),
    dict(n=11, title="Mean-reversion, Adaptive-Trend (ER-gated), and ensembles", status="info",
         result="Ensemble Don+EMA+MeanRev: BTC +29%/0.78 Sharpe/-24%DD, ETH -3%/0.09/-43%DD",
         takeaway="Adaptive-Trend failed (just a timid Donchian). Trend vs mean-reversion correlation ~0 — promising lead, needed OOS validation."),
    dict(n=12, title="Walk-forward validation of the trend+mean-rev ensemble", status="rejected",
         result="Ensemble OOS Sharpe BTC -1.45, ETH -2.11 — worse than best single system",
         takeaway="QUALIFIED FAIL: zero-correlation held OOS (real), but the ensemble's in-sample 'best risk-adjusted' edge was in-sample luck. Not adopted as flagship."),
    dict(n=13, title="Forex EUR/USD — better than crypto?", status="rejected",
         result="Trend systems UNDERPERFORMED buy-and-hold on forex (opposite of crypto)",
         takeaway="Crypto + trend-following remains the better fit for an unleveraged €1k account. Forex needs leverage + mean-reversion, a different engine."),
    dict(n=14, title="Does adding shorts help? (long/short Donchian)", status="rejected",
         result="Shorts help in OOS bear but hurt full-cycle return (BTC +30% long-only vs +16% L/S); Kraken-ish carry erases the bear benefit",
         takeaway="Adopted: stay LONG-ONLY. Going to cash captures ~80% of the bear benefit without leverage/carry/liquidation risk."),
    dict(n=15, title="TradingView 'Donchian Breakout Strategy' refinements", status="rejected",
         result="Asymmetric channels & two-stage stop each helped one asset, hurt the other",
         takeaway="Convergent validation: an independent strategy landed on our exact architecture. Refinements not robust across both assets — keep the 20/10 baseline."),
    dict(n=16, title="Faithful TradingView port (corrects Run 15)", status="adopted",
         result="Structural two-stage stop improved EVERY config on both assets, both periods",
         takeaway="First refinement all session to help across the board. Grafted onto our system as the structural two-stage exit (see Run 19)."),
    dict(n=17, title="TradingView 'ML RSI / AI Classification' (Zeiierman)", status="rejected",
         result="kNN core hit-rate below majority-class baseline, in-sample AND OOS, both pairs",
         takeaway="No demonstrated edge — fails its most basic test even in-sample. Not pursued."),
    dict(n=18, title="TradingView '3Commas Bot' (EMA21/50 + ATR stop, L/S/flip)", status="rejected",
         result="Long-only version underperforms our baseline on both assets",
         takeaway="The one positive-OOS result came from shorting through a single ETH downtrend (5 trades) — not statistically meaningful. No change to long-only stance."),
    dict(n=19, title="Close-based entry + structural two-stage stop — walk-forward validated", status="adopted",
         result="Clean, no-downside refinement to the Run 7 exit rule",
         takeaway="ADOPTED and wired into the live system: backtester.py signals <PAIR> now shows tight/wide exit channels."),
    dict(n=20, title="Rob Carver range-normalized breakout (qoppac 2016)", status="rejected",
         result="No robust winner; every config negative OOS on both assets; higher turnover hurts on 0.52% round-trip fees",
         takeaway="Nothing adopted, strong endorsement of the source. Our binary Donchian + two-stage exit is the honest fit for €1k unleveraged spot."),
    dict(n=21, title="Kraken Prop evaluation simulator — funded account viability", status="rejected",
         result="P(pass) ~28-40%, roughly tracks the zero-edge gambler's-ruin rate; leverage doesn't help",
         takeaway="Not a viable profit path. The 3% daily-loss limit is the dominant killer and contradicts the no-fixed-stops rule. If attempted: lowest tier, minimum leverage, hard intraday daily-loss stop."),
]

# Cumulative equity curves for the two data-rich runs (per-decision P&L, $10k notional)
RUN1_PNL = [-631.50, 2.90, 0.0, 1343.00, 24.30]
RUN2_PNL = [568, -832, -28, 1759, -868, 40, 182, 640, -394, 100, -47, 0,
            -494, 471, 402, 0, 699, 0, 177, 353, 1334, 350, 330]


def cumulative(pnls):
    total = 0
    out = []
    for p in pnls:
        total += p
        out.append(round(total, 2))
    return out


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
STATUS_COLORS = {
    "adopted": "#1e7a34",
    "rejected": "#9c2b2b",
    "key": "#7a4f00",
    "info": "#444",
}
STATUS_LABELS = {
    "adopted": "ADOPTED",
    "rejected": "NOT ADOPTED",
    "key": "KEY FINDING",
    "info": "OBSERVATION",
}

PAIR_LABELS = {"BTCEUR": "BTC/EUR", "ETHEUR": "ETH/EUR"}


def _ds(label, data, color, dash=None, hidden=False, width=1.5):
    d = {
        "label": label, "data": data, "borderColor": color,
        "backgroundColor": "transparent", "borderWidth": width,
        "pointRadius": 0, "tension": 0.1, "fill": False,
    }
    if dash:
        d["borderDash"] = dash
    if hidden:
        d["hidden"] = True
    return d


def _ta_datasets(d):
    n = len(d["labels"])
    datasets = [
        _ds("Close", d["close"], "#e6e8eb", width=1.75),
        _ds("EMA21", d["ema21"], "#4fa3ff"),
        _ds("EMA55", d["ema55"], "#f2a93b"),
        _ds("SMA200 (regime)", d["sma200"], "#9aa0ab", dash=[3, 3], hidden=True),
        _ds(f"Donchian {ta_charts.ENTRY_LOOKBACK}d-high (entry channel)",
            d["donchian_high"], "#3ddc84", dash=[6, 3]),
        _ds(f"Tight {ta_charts.TIGHT_EXIT}d-low (exit)",
            d["tight_low"], "#ff6b6b", dash=[4, 4], hidden=True),
        _ds(f"Wide {ta_charts.WIDE_EXIT}d-low (exit)",
            d["wide_low"], "#c0392b", dash=[2, 2], hidden=True),
    ]
    if d["up_trigger"]:
        datasets.append(_ds("Upside trigger (levels_watch)", [d["up_trigger"]] * n, "#c792ea", dash=[8, 4]))
    if d["down_trigger"]:
        datasets.append(_ds("Downside trigger (levels_watch)", [d["down_trigger"]] * n, "#e07b53", dash=[8, 4]))
    return datasets


def render_ta_section(ta_data):
    """Returns (cards_html, scripts_js) for the Technical Analysis section."""
    cards = ""
    scripts = ""
    for pair, label in PAIR_LABELS.items():
        d = ta_data.get(pair)
        cid = pair.lower()
        if d is None:
            cards += f"""
        <div class="ta-card">
          <h3>{label}</h3>
          <p class="subtitle">Live chart data unavailable this run (Kraken API unreachable). See the
          Current Levels and journal above for the last reviewed snapshot.</p>
        </div>"""
            continue
        comment_html = "".join(f"<li>{line}</li>" for line in d["commentary"])
        cards += f"""
        <div class="ta-card">
          <h3>{label} <span class="ta-asof">as of {d['last_date']}</span></h3>
          <div class="chart-wrap"><canvas id="{cid}PriceChart"></canvas></div>
          <div class="chart-wrap ta-rsi"><canvas id="{cid}RsiChart"></canvas></div>
          <ul class="ta-comment">{comment_html}</ul>
        </div>"""
        scripts += (
            f"makeTAChart('{cid}PriceChart', {json.dumps(d['labels'])}, {json.dumps(_ta_datasets(d))});\n"
            f"makeRSIChart('{cid}RsiChart', {json.dumps(d['labels'])}, {json.dumps(d['rsi'])});\n"
        )
    return cards, scripts


def render(entries, levels_info, ta_data):
    levels_html = ""
    for pair, lv in levels_info["levels"].items():
        levels_html += f"""
        <div class="level-card">
          <h3>{pair}/EUR</h3>
          <div class="level-row"><span>Downside trigger</span><span>€{lv['downside']}</span></div>
          <div class="level-row"><span>Upside trigger</span><span>€{lv['upside']}</span></div>
          <div class="level-state">{lv['state']}</div>
        </div>"""

    journal_rows = ""
    for e in entries:
        review_cls = "pending" if e["review"] == "Pending" else "done"
        journal_rows += f"""
        <div class="journal-card">
          <div class="journal-head">
            <span class="journal-date">{e['date']}</span>
            <span class="journal-pair">{e['pair']}</span>
            <span class="journal-regime regime-{e['regime'].lower()}">{e['regime']}</span>
            <span class="journal-verdict">{e['verdict']}</span>
          </div>
          <div class="journal-snapshot">{e['snapshot']}</div>
          <div class="journal-reasoning"><strong>Reasoning:</strong> {e['reasoning']}</div>
          <div class="journal-review {review_cls}"><strong>Review:</strong> {e['review']}</div>
        </div>"""

    run_rows = ""
    for r in BACKTEST_RUNS:
        color = STATUS_COLORS[r["status"]]
        label = STATUS_LABELS[r["status"]]
        run_rows += f"""
        <div class="run-card">
          <div class="run-head">
            <span class="run-num">Run {r['n']}</span>
            <span class="run-title">{r['title']}</span>
            <span class="run-status" style="background:{color}">{label}</span>
          </div>
          <div class="run-result">{r['result']}</div>
          <div class="run-takeaway">{r['takeaway']}</div>
        </div>"""

    run1_cum = cumulative(RUN1_PNL)
    run2_cum = cumulative(RUN2_PNL)
    ta_cards, ta_scripts = render_ta_section(ta_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kraken Trading Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {{
    --bg: #0f1115; --card: #1a1d24; --border: #2a2e38; --text: #e6e8eb;
    --muted: #9aa0ab; --accent: #4fa3ff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--text); padding: 24px;
  }}
  h1 {{ margin: 0 0 4px; font-size: 28px; }}
  .subtitle {{ color: var(--muted); margin-bottom: 24px; }}
  h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-top: 40px; }}
  .levels-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 16px; }}
  .level-card, .journal-card, .run-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 16px; margin-bottom: 12px;
  }}
  .level-card {{ flex: 1; min-width: 220px; }}
  .level-card h3 {{ margin: 0 0 8px; color: var(--accent); }}
  .level-row {{ display: flex; justify-content: space-between; padding: 4px 0; color: var(--muted); }}
  .level-row span:last-child {{ color: var(--text); font-weight: 600; }}
  .level-state {{ margin-top: 8px; font-size: 13px; color: var(--muted); font-style: italic; }}
  .last-reviewed {{ color: var(--muted); font-size: 14px; margin-top: 8px; }}

  .journal-head {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }}
  .journal-date {{ font-weight: 700; font-size: 16px; }}
  .journal-pair {{ background: #2a2e38; padding: 2px 8px; border-radius: 6px; font-size: 13px; }}
  .journal-regime {{ padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 700; }}
  .regime-bear {{ background: #4a1f1f; color: #ff9a9a; }}
  .regime-bull {{ background: #1f4a26; color: #9affc0; }}
  .journal-verdict {{ margin-left: auto; font-weight: 700; color: var(--accent); }}
  .journal-snapshot, .journal-reasoning, .journal-review {{ font-size: 14px; color: var(--muted); margin-top: 6px; line-height: 1.5; }}
  .journal-reasoning strong, .journal-review strong {{ color: var(--text); }}
  .journal-review.pending {{ color: #d8a657; }}

  .run-card {{ position: relative; }}
  .run-head {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }}
  .run-num {{ font-weight: 700; color: var(--accent); min-width: 56px; }}
  .run-title {{ font-weight: 600; }}
  .run-status {{ margin-left: auto; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }}
  .run-result {{ font-size: 14px; color: var(--text); margin-bottom: 4px; }}
  .run-takeaway {{ font-size: 13px; color: var(--muted); line-height: 1.5; }}

  .chart-wrap {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
  .chart-wrap h3 {{ margin-top: 0; color: var(--accent); }}
  .charts-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .charts-row .chart-wrap {{ flex: 1; min-width: 300px; }}

  .ta-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 16px; }}
  .ta-card {{ flex: 1; min-width: 420px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
  .ta-card h3 {{ margin-top: 0; color: var(--accent); }}
  .ta-asof {{ color: var(--muted); font-size: 12px; font-weight: 400; margin-left: 8px; }}
  .ta-card .chart-wrap {{ margin: 0 0 12px; padding: 12px; }}
  .ta-rsi {{ height: 120px; position: relative; }}
  .ta-rsi canvas {{ position: absolute; width: 100% !important; height: 100% !important; }}
  .ta-comment {{ list-style: none; margin: 12px 0 0; padding: 0; font-size: 14px; color: var(--muted); line-height: 1.6; }}
  .ta-comment li {{ padding: 4px 0; border-bottom: 1px solid var(--border); }}
  .ta-comment li:last-child {{ border-bottom: none; font-weight: 700; color: var(--text); }}

  .disclaimer {{ background: #2a2310; border: 1px solid #5a4a1a; border-radius: 10px; padding: 14px; margin-top: 24px; font-size: 13px; color: #e0c98a; line-height: 1.6; }}
  footer {{ margin-top: 40px; color: var(--muted); font-size: 12px; text-align: center; }}
</style>
</head>
<body>
  <h1>Kraken Trading Dashboard</h1>
  <div class="subtitle">Mechanical watch, daily journal, and backtest track record. Generated from trading_journal.md / levels_watch.md / backtest_journal.md.</div>

  <h2>Current Levels</h2>
  <div class="last-reviewed">Last reviewed: {levels_info['last_reviewed']}</div>
  <div class="levels-row">
    {levels_html}
  </div>

  <h2>Technical Analysis</h2>
  <div class="subtitle">Price with the same EMA/regime/Donchian lines the mechanical watcher
  (watch.py / backtester.py signals) computes, plus RSI(14) for context. Click legend items to
  toggle lines. The "Read" notes below each chart are a factual readout, not a new signal —
  decisions still follow watch.py / trading_journal.md.</div>
  <div class="ta-row">
    {ta_cards}
  </div>

  <h2>Daily / Weekly Trading Journal</h2>
  {journal_rows if journal_rows else "<p class='subtitle'>No entries yet.</p>"}

  <h2>Backtest Track Record (21 Runs)</h2>
  <div class="charts-row">
    <div class="chart-wrap">
      <h3>Run 1 — BTC/USD daily, 5 weeks (hindsight)</h3>
      <canvas id="run1Chart"></canvas>
    </div>
    <div class="chart-wrap">
      <h3>Run 2 — BTC/USD weekly YTD, 23 calls (hindsight-contaminated)</h3>
      <canvas id="run2Chart"></canvas>
    </div>
  </div>

  {run_rows}

  <div class="disclaimer">
    <strong>Honest framing (see Run 6 / 12 / 20):</strong> Across the whole backtest journal, no
    system demonstrated reliable out-of-sample alpha. The validated, repeatable property is
    <em>drawdown reduction</em> via trend-following with a structural two-stage trailing stop
    (Run 19, currently live). FLAT is a legitimate, often-correct answer. This dashboard is a
    risk-reduction monitoring tool, not a signal of guaranteed profit.
  </div>

  <footer>Generated by generate_dashboard.py — re-run after each daily watch / new backtest run.</footer>

<script>
const run1Labels = {json.dumps([f"#{i+1}" for i in range(len(RUN1_PNL))])};
const run1Cum = {json.dumps(run1_cum)};
const run2Labels = {json.dumps([f"W{i+1}" for i in range(len(RUN2_PNL))])};
const run2Cum = {json.dumps(run2_cum)};

function makeChart(id, labels, data) {{
  new Chart(document.getElementById(id), {{
    type: 'line',
    data: {{
      labels: labels,
      datasets: [{{
        label: 'Cumulative P&L ($10k notional)',
        data: data,
        borderColor: '#4fa3ff',
        backgroundColor: 'rgba(79,163,255,0.1)',
        fill: true,
        tension: 0.2,
        pointRadius: 3,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ labels: {{ color: '#e6e8eb' }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#9aa0ab' }}, grid: {{ color: '#2a2e38' }} }},
        y: {{ ticks: {{ color: '#9aa0ab' }}, grid: {{ color: '#2a2e38' }} }}
      }}
    }}
  }});
}}
makeChart('run1Chart', run1Labels, run1Cum);
makeChart('run2Chart', run2Labels, run2Cum);

function makeTAChart(id, labels, datasets) {{
  new Chart(document.getElementById(id), {{
    type: 'line',
    data: {{ labels: labels, datasets: datasets }},
    options: {{
      responsive: true,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#e6e8eb', boxWidth: 20 }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#9aa0ab', maxTicksLimit: 10 }}, grid: {{ color: '#2a2e38' }} }},
        y: {{ ticks: {{ color: '#9aa0ab' }}, grid: {{ color: '#2a2e38' }} }}
      }}
    }}
  }});
}}

function makeRSIChart(id, labels, rsiData) {{
  new Chart(document.getElementById(id), {{
    type: 'line',
    data: {{
      labels: labels,
      datasets: [
        {{ label: 'RSI(14)', data: rsiData, borderColor: '#c792ea', backgroundColor: 'transparent',
           borderWidth: 1.5, pointRadius: 0, tension: 0.1 }},
        {{ label: 'Overbought (70)', data: labels.map(() => 70), borderColor: '#9c2b2b',
           borderDash: [4, 4], borderWidth: 1, pointRadius: 0 }},
        {{ label: 'Oversold (30)', data: labels.map(() => 30), borderColor: '#1e7a34',
           borderDash: [4, 4], borderWidth: 1, pointRadius: 0 }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#e6e8eb', boxWidth: 20 }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#9aa0ab', maxTicksLimit: 10 }}, grid: {{ color: '#2a2e38' }} }},
        y: {{ min: 0, max: 100, ticks: {{ color: '#9aa0ab' }}, grid: {{ color: '#2a2e38' }} }}
      }}
    }}
  }});
}}
{ta_scripts}
</script>
</body>
</html>
"""
    return html


def build_ta_data():
    ta_data = {}
    for pair in PAIR_LABELS:
        try:
            ta_data[pair] = ta_charts.build_pair_data(pair)
        except Exception as e:
            print(f"warning: skipping TA charts for {pair}: {e}", file=sys.stderr)
            ta_data[pair] = None
    return ta_data


def main():
    entries = parse_trading_journal()
    levels_info = parse_levels()
    ta_data = build_ta_data()
    html = render(entries, levels_info, ta_data)
    out_path = ROOT / "dashboard.html"
    out_path.write_text(html)
    print(f"Wrote {out_path} ({len(entries)} journal entries, {len(BACKTEST_RUNS)} backtest runs)")


if __name__ == "__main__":
    main()
