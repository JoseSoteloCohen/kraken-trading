#!/usr/bin/env python3
"""Technical-analysis chart data + commentary for generate_dashboard.py.

Reuses backtester.py's indicator helpers and watch.py's levels_watch.md parser so the
chart shows exactly the numbers the mechanical watcher (`watch.py` / `backtester.py
signals`) already computes — read-only context for a human reviewing the journal, not
a new signal source.
"""
import backtester as bt
import watch

ENTRY_LOOKBACK = 20    # Donchian entry channel (matches watch.py / cmd_signals)
TIGHT_EXIT = 8         # two-stage exit, tight stage
WIDE_EXIT = 10         # two-stage exit, wide stage
REGIME_MA = 200        # bull/bear regime SMA


def _rolling(vals, window, fn):
    out = [None] * len(vals)
    for i in range(window, len(vals)):
        out[i] = fn(vals[i - window:i])
    return out


def _load_bars(pair):
    try:
        return bt.load(pair, refresh=True)
    except Exception:
        return bt.load(pair, refresh=False)


def build_pair_data(pair, lookback_days=150):
    bars = _load_bars(pair)
    closes = [b["c"] for b in bars]
    dates = [bt.dstr(b["t"]) for b in bars]

    ema21 = bt.ema(closes, 21)
    ema55 = bt.ema(closes, 55)
    sma200 = bt.sma(closes, REGIME_MA)
    rsi14 = bt.rsi(closes, 14)
    donchian_high = _rolling(closes, ENTRY_LOOKBACK, max)
    tight_low = _rolling(closes, TIGHT_EXIT, min)
    wide_low = _rolling(closes, WIDE_EXIT, min)

    levels = watch.parse_levels(watch.LEVELS_FILE)
    lv = levels.get(pair, {"down": None, "up": None})

    n = len(bars)
    sl = slice(max(0, n - lookback_days), n)

    data = {
        "labels": dates[sl],
        "close": closes[sl],
        "ema21": ema21[sl],
        "ema55": ema55[sl],
        "sma200": sma200[sl],
        "donchian_high": donchian_high[sl],
        "tight_low": tight_low[sl],
        "wide_low": wide_low[sl],
        "rsi": rsi14[sl],
        "down_trigger": lv.get("down"),
        "up_trigger": lv.get("up"),
        "last_date": dates[-1],
    }
    data["commentary"] = _commentary(
        closes[-1], ema21[-1], ema55[-1], sma200[-1], rsi14[-1],
        donchian_high[-1], tight_low[-1], wide_low[-1], lv,
    )
    return data


def _commentary(c, ef, es, ma200, r, ph, tight_low, wide_low, lv):
    """Factual readout mirroring watch.py / cmd_signals — no new signals, just a
    plain-language view of the numbers the mechanical watcher already computes."""
    lines = []

    if ma200 is not None:
        regime = "BULL" if c > ma200 else "BEAR"
        dist = (c / ma200 - 1) * 100
        lines.append(f"Regime: {regime} — price is {dist:+.1f}% vs the 200d SMA (€{ma200:,.0f}).")

    cross = "bullish (21 > 55)" if ef > es else "bearish (21 < 55)"
    gap = (ef / es - 1) * 100
    lines.append(f"EMA trend: {cross} — EMA21 €{ef:,.0f} vs EMA55 €{es:,.0f} ({gap:+.1f}% gap).")

    if ph is not None:
        entry_trigger = ph * (1 + watch.MARGIN)
        if c > entry_trigger:
            dist = (c / entry_trigger - 1) * 100
            lines.append(
                f"Donchian entry: CONFIRMED — close €{c:,.0f} cleared the "
                f"{ENTRY_LOOKBACK}d-high entry trigger €{entry_trigger:,.0f} by {dist:.1f}%.")
        else:
            dist = (entry_trigger / c - 1) * 100
            lines.append(
                f"Donchian entry: no trigger — close €{c:,.0f} is {dist:.1f}% below the "
                f"{ENTRY_LOOKBACK}d-high entry trigger €{entry_trigger:,.0f} "
                f"(20d-high €{ph:,.0f} + {watch.MARGIN*100:.1f}% margin).")

    if tight_low is not None and wide_low is not None:
        lines.append(
            f"Two-stage exit channels (if in a position): tight {TIGHT_EXIT}d-low "
            f"€{tight_low:,.0f} / wide {WIDE_EXIT}d-low €{wide_low:,.0f}.")

    reading = "overbought (>70)" if r > 70 else "oversold (<30)" if r < 30 else "neutral"
    lines.append(f"RSI(14): {r:.0f} — {reading}.")

    up, down = lv.get("up"), lv.get("down")
    any_break = False
    if up:
        if c >= up * (1 + watch.MARGIN):
            dist = (c / up - 1) * 100
            lines.append(
                f"** CONFIRMED UPSIDE break: close €{c:,.0f} cleared the levels_watch.md "
                f"upside trigger €{up:,.0f} by {dist:.1f}% -> review for a LONG entry.")
            any_break = True
        else:
            dist = (up / c - 1) * 100
            lines.append(f"levels_watch.md upside trigger: €{up:,.0f}, {dist:.1f}% above current price — not yet broken.")
    if down:
        if c <= down * (1 - watch.MARGIN):
            dist = (1 - c / down) * 100
            lines.append(
                f"** CONFIRMED DOWNSIDE break: close €{c:,.0f} cleared the levels_watch.md "
                f"downside trigger €{down:,.0f} by {dist:.1f}% -> review for a SHORT/exit decision.")
            any_break = True
        else:
            dist = (1 - down / c) * 100
            lines.append(f"levels_watch.md downside trigger: €{down:,.0f}, {dist:.1f}% below current price — not yet broken.")

    if any_break:
        lines.append("Bottom line: CONFIRMED BREAK — review for an entry decision (see watch.py / trading_journal.md). Do not auto-trade.")
    else:
        lines.append("Bottom line: ALL QUIET — no confirmed break; FLAT remains the default.")

    return lines
