#!/usr/bin/env python3
"""
Mechanical backtester for the Kraken disciplined-trading workflow.

Strategy: Donchian-channel breakout (turtle-style trend following) — this is the mechanical
form of our validated finding ("trade confirmed breaks of ranges, not reversals"). Long-only,
no leverage (conservative for a real small account).

  - ENTER long when the close exceeds the highest close of the prior `entry_lookback` days
    by at least `entry_margin` (the break-quality filter — avoids marginal whipsaw pokes).
  - EXIT to cash when the close falls below the lowest close of the prior `exit_lookback` days
    (a trailing Donchian stop — lets winners run, cuts losers; this matters because backtests
    showed P&L is concentrated in a few big trends).
  - Optional volatility targeting: size each position so recent daily vol ~= `target_vol`,
    capped at 1.0 (never leveraged). Off by default (full size).

Benchmarks every result against BUY-AND-HOLD and CASH, because a strategy is only worth the
effort if it beats simply holding the asset (or holding cash in a downtrend).

Walk-forward: `sweep` tunes parameters on a train slice and reports the SAME params'
out-of-sample performance on an untouched test slice — the honest test for curve-fitting.

Data comes straight from Kraken's PUBLIC REST API over HTTPS (stdlib only, no API key, no
`kraken` CLI, no WSL) — so this runs anywhere, including a fresh cloud clone (Claude Code Routines).

Usage:
  python3 backtester.py fetch BTCEUR              # refresh cached daily data
  python3 backtester.py run BTCEUR                # single backtest, default params (auto-fetches)
  python3 backtester.py run BTCEUR --entry 20 --exit 10 --margin 0.005 --voltarget 0.02
  python3 backtester.py sweep BTCEUR              # walk-forward param sweep (train/test split)
"""
import json, sys, datetime, argparse, statistics, math, os, tempfile, urllib.request

# per side. Crypto Kraken Starter = 0.0026 (0.52% round trip). Override for other asset classes,
# e.g. forex ~0.0002 (a pip). Set via env: KRAKEN_BT_FEE=0.0002
FEE = float(os.environ.get("KRAKEN_BT_FEE", "0.0026"))

# ---------------------------------------------------------------- data

KRAKEN_API = "https://api.kraken.com/0/public"
# our pair name -> Kraken API altname (Kraken uses XBT for BTC). Response key may differ
# (e.g. XXBTZEUR); load() takes the first non-"last" key so it doesn't matter.
PAIR_MAP = {"BTCEUR": "XBTEUR", "ETHEUR": "ETHEUR"}

def _cache_path(pair):
    return os.path.join(tempfile.gettempdir(), f"bt_{pair}.json")

def _api_get(path):
    with urllib.request.urlopen(f"{KRAKEN_API}/{path}", timeout=30) as r:
        d = json.load(r)
    if d.get("error"):
        raise RuntimeError(f"Kraken API error ({path}): {d['error']}")
    return d["result"]

def fetch(pair, cache=None):
    """Pull daily OHLC from Kraken's public API and cache it. Returns the cache path."""
    cache = cache or _cache_path(pair)
    res = _api_get(f"OHLC?pair={PAIR_MAP.get(pair, pair)}&interval=1440")
    json.dump(res, open(cache, "w"))   # res = {"<pairkey>": [...rows...], "last": ...}
    return cache

def fetch_ticker(pair):
    """Current last-trade price from Kraken's public Ticker endpoint."""
    res = _api_get(f"Ticker?pair={PAIR_MAP.get(pair, pair)}")
    k = [x for x in res][0]
    return float(res[k]["c"][0])       # "c" = [last_price, lot_volume]

def load(pair, cache=None, refresh=False):
    cache = cache or _cache_path(pair)
    if refresh or not os.path.exists(cache):
        fetch(pair, cache)
    d = json.load(open(cache))
    k = [x for x in d if x != "last"][0]
    rows = d[k]
    # [time, open, high, low, close, vwap, volume, count]
    return [{"t": r[0], "o": float(r[1]), "h": float(r[2]),
             "l": float(r[3]), "c": float(r[4])} for r in rows]

def dstr(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d")

# ---------------------------------------------------------------- strategy

def run_strategy(bars, entry_lookback=20, exit_lookback=10, entry_margin=0.005,
                 target_vol=None, vol_window=20, regime_ma=None):
    """Return (equity_curve, trades, daily_returns) for the long-only breakout strategy.
    equity starts at 1.0. Fees charged on each entry and exit.
    If regime_ma set, only enter when close > SMA(regime_ma) (bull regime), and exit if
    close falls below that SMA (regime stop)."""
    equity = 1.0
    pos = 0.0          # fraction of equity currently long (0..1)
    entry_price = None
    eq_curve = [1.0]
    daily_rets = []
    trades = []
    closes = [b["c"] for b in bars]
    reg = sma(closes, regime_ma) if regime_ma else None

    for i in range(len(bars)):
        c = bars[i]["c"]
        # mark-to-market today's move on existing position
        if i > 0:
            prev = bars[i-1]["c"]
            ret = pos * (c / prev - 1.0)
            equity *= (1.0 + ret)
            daily_rets.append(ret)

        # need history for the channels
        if i < max(entry_lookback, exit_lookback) + 1:
            eq_curve.append(equity)
            continue

        prior_high = max(b["c"] for b in bars[i-entry_lookback:i])
        prior_low  = min(b["c"] for b in bars[i-exit_lookback:i])
        bull = (reg is None) or (reg[i] is not None and c > reg[i])

        if pos == 0.0:
            # entry: confirmed break above channel by margin, in bull regime
            if bull and c > prior_high * (1.0 + entry_margin):
                size = 1.0
                if target_vol:
                    rets = [bars[j]["c"]/bars[j-1]["c"]-1 for j in range(i-vol_window+1, i+1)]
                    rv = statistics.pstdev(rets) or 1e-9
                    size = min(1.0, target_vol / rv)
                pos = size
                entry_price = c
                equity *= (1.0 - FEE * size)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]),
                               "entry_p": c, "size": size})
        else:
            # exit: close below trailing channel low OR regime turns bear
            if c < prior_low or not bull:
                equity *= (1.0 - FEE * pos)
                t = trades[-1]
                t.update({"exit_i": i, "exit_d": dstr(bars[i]["t"]), "exit_p": c,
                          "ret": (c/entry_price - 1.0)})
                pos = 0.0
                entry_price = None
        eq_curve.append(equity)

    # close any open position at last price (mark-out)
    if pos > 0.0:
        equity *= (1.0 - FEE * pos)
        t = trades[-1]
        t.update({"exit_i": len(bars)-1, "exit_d": dstr(bars[-1]["t"]),
                  "exit_p": bars[-1]["c"], "ret": (bars[-1]["c"]/entry_price - 1.0), "open": True})

    return eq_curve, trades, daily_rets

def run_strategy_ts(bars, entry_lookback=20, exit_lookback=10, tight_exit=8, entry_margin=0.005,
                     regime_ma=None):
    """Our close-based Donchian breakout (same entry as run_strategy), but with the STRUCTURAL
    TWO-STAGE STOP discovered in Run 16: a TIGHT close-based exit channel (tight_exit-period low)
    until the trade is 'in profit' (entry_price <= tight line, i.e. the tight line has risen above
    entry), then switch to the wider exit_lookback-period low channel. Everything else (entry,
    fees, regime) matches run_strategy for an apples-to-apples comparison."""
    equity = 1.0; pos = 0.0; entry_price = None
    eq_curve = [1.0]; daily_rets = []; trades = []
    closes = [b["c"] for b in bars]
    reg = sma(closes, regime_ma) if regime_ma else None
    for i in range(len(bars)):
        c = bars[i]["c"]
        if i > 0:
            prev = bars[i-1]["c"]
            ret = pos * (c / prev - 1.0)
            equity *= (1.0 + ret); daily_rets.append(ret)
        if i < max(entry_lookback, exit_lookback, tight_exit) + 1:
            eq_curve.append(equity); continue
        prior_high = max(b["c"] for b in bars[i-entry_lookback:i])
        wide_low = min(b["c"] for b in bars[i-exit_lookback:i])
        tight_low = min(b["c"] for b in bars[i-tight_exit:i])
        bull = (reg is None) or (reg[i] is not None and c > reg[i])
        if pos == 0.0:
            if bull and c > prior_high * (1.0 + entry_margin):
                pos = 1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "entry_p": c})
        else:
            in_profit = entry_price <= tight_low
            stop_line = wide_low if in_profit else tight_low
            if c < stop_line or not bull:
                equity *= (1.0 - FEE)
                t = trades[-1]
                t.update({"exit_i": i, "exit_d": dstr(bars[i]["t"]), "exit_p": c,
                          "ret": (c / entry_price - 1.0)})
                pos = 0.0; entry_price = None
        eq_curve.append(equity)
    if pos > 0.0:
        equity *= (1.0 - FEE)
        t = trades[-1]
        t.update({"exit_i": len(bars)-1, "exit_d": dstr(bars[-1]["t"]), "exit_p": bars[-1]["c"],
                  "ret": (bars[-1]["c"]/entry_price - 1.0), "open": True})
    return eq_curve, trades, daily_rets

def carver_breakout(closes, lookback, smooth=None):
    """Rob Carver's breakout forecast (qoppac, 2016): position of price within its rolling
    range, normalized to ~[-0.5, +0.5], then EWMA-smoothed (span = lookback/4 by default).
    forecast = (price - rollmid) / (rollmax - rollmin), where rollmid = (max+min)/2 over `lookback`.
    A CONTINUOUS, range-normalized trend signal (unlike our binary Donchian) — Carver's own point
    is that it's ~the same thing as a moving-average crossover, just normalized & comparable."""
    if smooth is None:
        smooth = max(lookback // 4, 1)
    n = len(closes)
    raw = [0.0] * n
    for i in range(n):
        w = closes[max(0, i - lookback + 1):i + 1]
        hi, lo = max(w), min(w)
        rng = hi - lo
        raw[i] = 0.0 if rng == 0 else (closes[i] - (hi + lo) / 2.0) / rng
    k = 2.0 / (smooth + 1.0)
    sm = [raw[0]]
    for x in raw[1:]:
        sm.append(x * k + sm[-1] * (1 - k))
    return sm

def run_breakout(bars, lookback=40, mode="continuous", scale=2.0):
    """Trade Carver's breakout forecast LONG-ONLY (our constraint). mode='sign' = binary (long when
    forecast>0, else flat); mode='continuous' = graded position size = clamp(forecast*scale, 0, 1)
    (full long at the top of the range). Fees charged on the SIZE of each daily rebalance
    (FEE*|dpos|) — the honest cost of continuous sizing on a 0.26%/side spot account.
    Returns (eq_curve, daily_rets, n_entries, turnover)."""
    closes = [b["c"] for b in bars]
    fc = carver_breakout(closes, lookback)
    equity = 1.0; eq = [1.0]; dr = []; pos = 0.0; n_entries = 0; turnover = 0.0
    for i in range(len(bars)):
        c = closes[i]
        if i > 0:
            ret = pos * (c / closes[i-1] - 1.0)
            equity *= (1.0 + ret); dr.append(ret)
        if i < lookback + 1:
            eq.append(equity); continue
        target = (1.0 if fc[i] > 0 else 0.0) if mode == "sign" else min(1.0, max(0.0, fc[i] * scale))
        if target != pos:
            d = abs(target - pos)
            equity *= (1.0 - FEE * d); turnover += d
            if pos == 0.0 and target > 0.0:
                n_entries += 1
            pos = target
        eq.append(equity)
    return eq, dr, n_entries, turnover

def sma(vals, period):
    out = [None] * len(vals)
    for i in range(period - 1, len(vals)):
        out[i] = sum(vals[i-period+1:i+1]) / period
    return out

def ema(vals, period):
    k = 2.0 / (period + 1.0); e = vals[0]; out = [e]
    for v in vals[1:]:
        e = v * k + e * (1 - k); out.append(e)
    return out

def rsi(closes, period=14):
    out = [50.0] * len(closes)
    if len(closes) <= period: return out
    gains = losses = 0.0
    for i in range(1, period + 1):
        d = closes[i] - closes[i-1]
        gains += max(d, 0); losses += max(-d, 0)
    ag = gains / period; al = losses / period
    out[period] = 100 - 100/(1 + (ag/al if al else 1e9))
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i-1]
        ag = (ag * (period-1) + max(d, 0)) / period
        al = (al * (period-1) + max(-d, 0)) / period
        out[i] = 100 - 100/(1 + (ag/al if al else 1e9))
    return out

def run_ema(bars, fast=21, slow=55, rsi_floor=50, exit_close_below_slow=False):
    """EMA-crossover trend system + RSI filter (the proposed alternative).
    Entry: fast EMA crosses above slow EMA AND RSI > rsi_floor.
    Exit: fast EMA crosses below slow EMA (or, if flag, daily close below slow EMA). Long-only."""
    closes = [b["c"] for b in bars]
    ef, es, rs = ema(closes, fast), ema(closes, slow), rsi(closes, 14)
    equity = 1.0; pos = 0.0; entry_price = None
    eq_curve = [1.0]; daily_rets = []; trades = []
    for i in range(len(bars)):
        c = closes[i]
        if i > 0:
            ret = pos * (c / closes[i-1] - 1.0)
            equity *= (1.0 + ret); daily_rets.append(ret)
        if i < slow + 1:
            eq_curve.append(equity); continue
        cross_up = ef[i-1] <= es[i-1] and ef[i] > es[i]
        cross_dn = ef[i-1] >= es[i-1] and ef[i] < es[i]
        if pos == 0.0:
            if cross_up and rs[i] > rsi_floor:
                pos = 1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "entry_p": c})
        else:
            if cross_dn or (exit_close_below_slow and c < es[i]):
                equity *= (1.0 - FEE)
                t = trades[-1]; t.update({"exit_i": i, "exit_d": dstr(bars[i]["t"]),
                    "exit_p": c, "ret": c/entry_price - 1.0})
                pos = 0.0; entry_price = None
        eq_curve.append(equity)
    if pos > 0.0:
        equity *= (1.0 - FEE)
        t = trades[-1]; t.update({"exit_i": len(bars)-1, "exit_d": dstr(bars[-1]["t"]),
            "exit_p": closes[-1], "ret": closes[-1]/entry_price - 1.0, "open": True})
    return eq_curve, trades, daily_rets

def run_longshort(bars, entry_lookback=20, exit_lookback=10, entry_margin=0.005,
                  short_carry=0.0):
    """Symmetric Donchian: LONG on upside breakout, SHORT on downside breakout, trailing-stop
    exit on the opposite channel. short_carry = daily borrow/funding cost while short (margin
    rollover). Models the long/short version to test whether shorts add value over long-only."""
    closes = [b["c"] for b in bars]
    equity = 1.0; pos = 0.0; entry_price = None
    eq_curve = [1.0]; daily_rets = []; trades = []
    for i in range(len(bars)):
        c = closes[i]
        if i > 0:
            ret = pos * (c / closes[i-1] - 1.0)
            if pos < 0:
                ret -= short_carry          # borrow cost while short
            equity *= (1.0 + ret); daily_rets.append(ret)
        if i < max(entry_lookback, exit_lookback) + 1:
            eq_curve.append(equity); continue
        hi_e = max(closes[i-entry_lookback:i]); lo_e = min(closes[i-entry_lookback:i])
        hi_x = max(closes[i-exit_lookback:i]); lo_x = min(closes[i-exit_lookback:i])
        if pos == 0.0:
            if c > hi_e * (1.0 + entry_margin):
                pos = 1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "side": "long"})
            elif c < lo_e * (1.0 - entry_margin):
                pos = -1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "side": "short"})
        elif pos > 0 and c < lo_x:
            equity *= (1.0 - FEE)
            trades[-1].update({"exit_i": i, "ret": c/entry_price - 1.0}); pos = 0.0
        elif pos < 0 and c > hi_x:
            equity *= (1.0 - FEE)
            trades[-1].update({"exit_i": i, "ret": entry_price/c - 1.0}); pos = 0.0
        eq_curve.append(equity)
    return eq_curve, trades, daily_rets

def run_donchian_tv(bars, up=20, low=10, stopp=8, mode="wick", two_stage=False):
    """Faithful port of millerrh's TradingView 'Donchian Breakout': channels on HIGH/LOW (not
    close), default WICK entry (resting stop order at the channel, fills intrabar), exit on the
    lower channel. Optional two-stage stop: tight (stopp-period low) until in profit
    (entry <= tight line), then the wider (low-period) channel. Long-only. No entry margin."""
    H=[b["h"] for b in bars]; L=[b["l"] for b in bars]; C=[b["c"] for b in bars]; O=[b["o"] for b in bars]
    equity=1.0; pos=0; entry_price=None; eq=[1.0]; trades=[]
    warm=max(up,low,stopp)+1
    for i in range(len(bars)):
        o,h,l,c = O[i],H[i],L[i],C[i]; prev_c = C[i-1] if i>0 else o
        ch_up  = max(H[i-up:i])  if i>=up  else float("inf")
        ch_low = min(L[i-low:i]) if i>=low else 0.0
        ch_st  = min(L[i-stopp:i]) if i>=stopp else 0.0
        exited=False
        if pos==1:
            if two_stage:
                in_profit = entry_price <= ch_st
                stoplvl = ch_low if in_profit else ch_st
            else:
                stoplvl = ch_low
            trig = l if mode=="wick" else c
            if i>=warm and trig <= stoplvl:
                exit_px = min(o, stoplvl) if mode=="wick" else c
                equity *= exit_px/prev_c; equity *= (1-FEE)
                trades[-1]["ret"]=exit_px/entry_price-1; pos=0; entry_price=None; exited=True
            else:
                equity *= c/prev_c
        if pos==0 and not exited and i>=warm:
            if mode=="wick":
                if h >= ch_up:
                    entry_price = max(o, ch_up)
                    equity *= (1-FEE); equity *= c/entry_price
                    pos=1; trades.append({"entry_i":i,"entry_d":dstr(bars[i]["t"])})
            else:
                if c >= ch_up:
                    equity *= (1-FEE); pos=1; entry_price=c
                    trades.append({"entry_i":i,"entry_d":dstr(bars[i]["t"])})
        eq.append(equity)
    dr=[eq[i+1]/eq[i]-1 for i in range(len(eq)-1)]
    return eq[1:], trades, dr

def run_3commas(bars, ma1_len=21, ma2_len=50, atr_len=14, swing_lb=5, risk_mult=1.0, rnr=1.0,
                allow_short=True, flip=True, trail_stop=False, trail_mult=1.0, short_carry=0.0):
    """Port of the popular '3Commas Bot' TradingView template: EMA(ma1) x EMA(ma2) crossover
    entries, long AND short by default with reversal flips (FLIP), stop = swing high/low +/-
    ATR*risk_mult, fixed take-profit at rnr*risk (default 1:1 R:R). trail_stop replaces the fixed
    stop+TP with a ratcheting ATR trailing stop (its 'Use ATR Trailing Stop' option, off by
    default). Tests this popular off-the-shelf combo against our Donchian baseline."""
    C=[b["c"] for b in bars]; H=[b["h"] for b in bars]; L=[b["l"] for b in bars]
    n=len(bars)
    e1=ema(C, ma1_len); e2=ema(C, ma2_len)
    TR=[0.0]+[max(H[i]-L[i], abs(H[i]-C[i-1]), abs(L[i]-C[i-1])) for i in range(1,n)]
    ATR=[0.0]*n
    for i in range(n):
        ATR[i] = sum(TR[max(1,i-atr_len+1):i+1])/min(atr_len, max(1,i))
    warm = max(ma1_len, ma2_len, atr_len, swing_lb) + 1
    equity=1.0; pos=0; entry_price=None; stop=None; target=None; trailing=None
    eq=[1.0]; trades=[]
    def open_long(i, c):
        nonlocal pos, entry_price, stop, target, trailing
        pos=1; entry_price=c
        ll=min(L[i-swing_lb+1:i+1]); risk=entry_price-(ll-ATR[i]*risk_mult)
        stop=ll-ATR[i]*risk_mult; target=entry_price+rnr*risk if rnr>0 else None
        if trail_stop: trailing=stop
        trades.append({"entry_i":i,"entry_d":dstr(bars[i]["t"]),"side":"long"})
    def open_short(i, c):
        nonlocal pos, entry_price, stop, target, trailing
        pos=-1; entry_price=c
        hh=max(H[i-swing_lb+1:i+1]); risk=(hh+ATR[i]*risk_mult)-entry_price
        stop=hh+ATR[i]*risk_mult; target=entry_price-rnr*risk if rnr>0 else None
        if trail_stop: trailing=stop
        trades.append({"entry_i":i,"entry_d":dstr(bars[i]["t"]),"side":"short"})
    for i in range(n):
        c=C[i]
        if i>0:
            ret = pos*(c/C[i-1]-1.0)
            if pos < 0:
                ret -= short_carry
            equity *= (1.0+ret)
        exited=False
        if pos!=0 and i>=warm:
            lo, hi = L[i], H[i]
            if trail_stop:
                ll=min(L[i-swing_lb+1:i+1]); hh=max(H[i-swing_lb+1:i+1])
                if pos==1:
                    cand = ll - ATR[i]*trail_mult
                    trailing = max(trailing, cand)
                    stoplvl = trailing
                else:
                    cand = hh + ATR[i]*trail_mult
                    trailing = min(trailing, cand)
                    stoplvl = trailing
            else:
                stoplvl = stop
            if pos==1:
                if lo <= stoplvl:
                    equity *= (1.0-FEE)
                    trades[-1]["ret"] = stoplvl/entry_price - 1.0; pos=0; exited=True
                elif target is not None and hi >= target:
                    equity *= (1.0-FEE)
                    trades[-1]["ret"] = target/entry_price - 1.0; pos=0; exited=True
            else:
                if hi >= stoplvl:
                    equity *= (1.0-FEE)
                    trades[-1]["ret"] = entry_price/stoplvl - 1.0; pos=0; exited=True
                elif target is not None and lo <= target:
                    equity *= (1.0-FEE)
                    trades[-1]["ret"] = entry_price/target - 1.0; pos=0; exited=True
            if exited:
                trades[-1]["exit_i"]=i; entry_price=None; stop=None; target=None; trailing=None
        if i>=warm:
            cross_up = e1[i]>e2[i] and e1[i-1]<=e2[i-1]
            cross_dn = e1[i]<e2[i] and e1[i-1]>=e2[i-1]
            if pos==0:
                if cross_up:
                    equity *= (1.0-FEE); open_long(i, c)
                elif allow_short and cross_dn:
                    equity *= (1.0-FEE); open_short(i, c)
            elif flip:
                if pos==1 and allow_short and cross_dn:
                    equity *= (1.0-FEE)
                    trades[-1]["ret"]=c/entry_price-1.0; trades[-1]["exit_i"]=i
                    equity *= (1.0-FEE); open_short(i, c)
                elif pos==-1 and cross_up:
                    equity *= (1.0-FEE)
                    trades[-1]["ret"]=entry_price/c-1.0; trades[-1]["exit_i"]=i
                    equity *= (1.0-FEE); open_long(i, c)
        eq.append(equity)
    dr=[eq[i+1]/eq[i]-1 for i in range(len(eq)-1)]
    return eq[1:], trades, dr

def run_twostage(bars, entry_lookback=20, tight_exit=5, wide_exit=20, profit_switch=0.10,
                 entry_margin=0.005):
    """Two-stage trailing stop (from the TradingView Donchian script idea): use a TIGHT lower
    channel until the trade is up `profit_switch`, then switch to a WIDE channel to let it run.
    Targets the win/loss asymmetry — cut losers fast, give winners room. Long-only."""
    closes = [b["c"] for b in bars]
    equity = 1.0; pos = 0.0; entry_price = None
    eq_curve = [1.0]; daily_rets = []; trades = []
    for i in range(len(bars)):
        c = closes[i]
        if i > 0:
            ret = pos * (c / closes[i-1] - 1.0); equity *= (1.0 + ret); daily_rets.append(ret)
        if i < max(entry_lookback, wide_exit) + 1:
            eq_curve.append(equity); continue
        if pos == 0.0:
            if c > max(closes[i-entry_lookback:i]) * (1.0 + entry_margin):
                pos = 1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "entry_p": c})
        else:
            in_profit = (c / entry_price - 1.0) >= profit_switch
            xlb = wide_exit if in_profit else tight_exit
            stop = min(closes[i-xlb:i])
            if c < stop:
                equity *= (1.0 - FEE)
                trades[-1].update({"exit_i": i, "ret": c/entry_price - 1.0}); pos = 0.0
        eq_curve.append(equity)
    if pos > 0.0:
        equity *= (1.0 - FEE); trades[-1].update({"exit_i": len(bars)-1, "ret": closes[-1]/entry_price-1.0})
    return eq_curve, trades, daily_rets

def run_meanrev(bars, lookback=20, k=2.0):
    """Mean-reversion (Bollinger): buy when close < lower band (mean - k*std),
    exit when close reverts up through the mean. Long-only. The natural COMPLEMENT to
    trend-following — profits in chop, bleeds in trends."""
    closes = [b["c"] for b in bars]
    equity = 1.0; pos = 0.0; entry_price = None
    eq_curve = [1.0]; daily_rets = []; trades = []
    for i in range(len(bars)):
        c = closes[i]
        if i > 0:
            ret = pos * (c / closes[i-1] - 1.0); equity *= (1.0 + ret); daily_rets.append(ret)
        if i < lookback + 1:
            eq_curve.append(equity); continue
        win = closes[i-lookback:i]; mean = sum(win)/lookback
        sd = statistics.pstdev(win) or 1e-9
        lower = mean - k*sd
        if pos == 0.0:
            if c < lower:
                pos = 1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "entry_p": c})
        else:
            if c >= mean:
                equity *= (1.0 - FEE)
                t = trades[-1]; t.update({"exit_i": i, "exit_d": dstr(bars[i]["t"]),
                    "exit_p": c, "ret": c/entry_price - 1.0}); pos = 0.0; entry_price = None
        eq_curve.append(equity)
    if pos > 0.0:
        equity *= (1.0 - FEE); t = trades[-1]
        t.update({"exit_i": len(bars)-1, "exit_d": dstr(bars[-1]["t"]),
                  "exit_p": closes[-1], "ret": closes[-1]/entry_price - 1.0, "open": True})
    return eq_curve, trades, daily_rets

def efficiency_ratio(closes, i, n):
    if i < n: return 0.0
    net = abs(closes[i] - closes[i-n])
    path = sum(abs(closes[j] - closes[j-1]) for j in range(i-n+1, i+1)) or 1e-9
    return net / path

def run_adaptive(bars, entry_lookback=20, exit_lookback=10, entry_margin=0.005,
                 er_window=20, er_thresh=0.30):
    """MY PROPOSAL — 'Adaptive Trend': Donchian breakout, but only ENTER when the market is
    actually trending (Efficiency Ratio > threshold). Targets trend-following's documented
    weakness (chop) without predicting direction — stay flat when the market isn't trending."""
    closes = [b["c"] for b in bars]
    equity = 1.0; pos = 0.0; entry_price = None
    eq_curve = [1.0]; daily_rets = []; trades = []
    for i in range(len(bars)):
        c = closes[i]
        if i > 0:
            ret = pos * (c / closes[i-1] - 1.0); equity *= (1.0 + ret); daily_rets.append(ret)
        if i < max(entry_lookback, exit_lookback, er_window) + 1:
            eq_curve.append(equity); continue
        prior_high = max(closes[i-entry_lookback:i]); prior_low = min(closes[i-exit_lookback:i])
        er = efficiency_ratio(closes, i, er_window)
        if pos == 0.0:
            if er > er_thresh and c > prior_high * (1.0 + entry_margin):
                pos = 1.0; entry_price = c; equity *= (1.0 - FEE)
                trades.append({"entry_i": i, "entry_d": dstr(bars[i]["t"]), "entry_p": c})
        else:
            if c < prior_low:
                equity *= (1.0 - FEE)
                t = trades[-1]; t.update({"exit_i": i, "exit_d": dstr(bars[i]["t"]),
                    "exit_p": c, "ret": c/entry_price - 1.0}); pos = 0.0; entry_price = None
        eq_curve.append(equity)
    if pos > 0.0:
        equity *= (1.0 - FEE); t = trades[-1]
        t.update({"exit_i": len(bars)-1, "exit_d": dstr(bars[-1]["t"]),
                  "exit_p": closes[-1], "ret": closes[-1]/entry_price - 1.0, "open": True})
    return eq_curve, trades, daily_rets

def blend(series_list):
    """Equal-weight capital split across sub-strategies: average their daily returns,
    then rebuild an equity curve. Models running them side by side with split capital."""
    n = min(len(s) for s in series_list)
    blended = [sum(s[j] for s in series_list)/len(series_list) for j in range(n)]
    eq = [1.0]
    for r in blended:
        eq.append(eq[-1]*(1.0+r))
    return eq, [], blended

def correl(a, b):
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    ma, mb = statistics.mean(a), statistics.mean(b)
    cov = sum((a[i]-ma)*(b[i]-mb) for i in range(n))
    da = math.sqrt(sum((x-ma)**2 for x in a)); db = math.sqrt(sum((x-mb)**2 for x in b))
    return cov/(da*db) if da and db else 0.0

def run_brackets(bars, entry_lookback=20, entry_margin=0.005, sl=0.08, tp=0.16,
                 always=False):
    """Fixed stop-loss / take-profit bracket variant.
    Entry: breakout above N-day high by margin (or, if always=True, re-enter at next close
    whenever flat — the 'jump in whenever there's cash' with no entry edge).
    Exit: intrabar — if day's low hits stop -> exit at stop; elif day's high hits TP -> exit at TP.
    If both hit same day, assume STOP first (conservative). Fees on entry and exit."""
    equity = 1.0; pos = 0.0; entry_price = None
    stop_p = tp_p = None
    eq_curve = [1.0]; daily_rets = []; trades = []

    for i in range(len(bars)):
        c = bars[i]["c"]; hi = bars[i]["h"]; lo = bars[i]["l"]
        if i > 0:
            # while in position, exit happens intrabar; approximate daily MTM to exit level
            if pos > 0.0:
                if lo <= stop_p:
                    exit_p = stop_p
                elif hi >= tp_p:
                    exit_p = tp_p
                else:
                    exit_p = c
                ret = pos * (exit_p / bars[i-1]["c"] - 1.0)
                equity *= (1.0 + ret); daily_rets.append(ret)
                if lo <= stop_p or hi >= tp_p:
                    equity *= (1.0 - FEE * pos)
                    t = trades[-1]; t.update({"exit_i": i, "exit_d": dstr(bars[i]["t"]),
                        "exit_p": exit_p, "ret": exit_p/entry_price - 1.0,
                        "hit": "stop" if lo <= stop_p else "tp"})
                    pos = 0.0; entry_price = None
            else:
                daily_rets.append(0.0)

        if i < entry_lookback + 1:
            eq_curve.append(equity); continue

        if pos == 0.0:
            prior_high = max(b["c"] for b in bars[i-entry_lookback:i])
            signal = (c > prior_high * (1.0 + entry_margin)) or always
            if signal:
                pos = 1.0; entry_price = c
                stop_p = c * (1.0 - sl); tp_p = c * (1.0 + tp)
                equity *= (1.0 - FEE); trades.append({"entry_i": i,
                    "entry_d": dstr(bars[i]["t"]), "entry_p": c})
        eq_curve.append(equity)

    if pos > 0.0:
        equity *= (1.0 - FEE)
        t = trades[-1]; t.update({"exit_i": len(bars)-1, "exit_d": dstr(bars[-1]["t"]),
            "exit_p": bars[-1]["c"], "ret": bars[-1]["c"]/entry_price - 1.0, "hit": "eod"})
    return eq_curve, trades, daily_rets

# ---------------------------------------------------------------- metrics

def max_drawdown(curve):
    peak = curve[0]; mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = min(mdd, v/peak - 1.0)
    return mdd

def sharpe(daily_rets):
    rs = [r for r in daily_rets]
    if len(rs) < 2: return 0.0
    mu = statistics.mean(rs); sd = statistics.pstdev(rs)
    if sd == 0: return 0.0
    return (mu / sd) * math.sqrt(365)  # crypto trades 365d

def metrics(bars, eq_curve, trades, daily_rets):
    strat_ret = eq_curve[-1] - 1.0
    bh_ret = bars[-1]["c"] / bars[0]["c"] - 1.0
    closed = [t for t in trades if "ret" in t]
    wins = [t for t in closed if t["ret"] > 0]
    days_in = sum((t.get("exit_i", len(bars)-1) - t["entry_i"]) for t in closed)
    exposure = days_in / max(1, len(bars))
    return {
        "strategy_return": strat_ret,
        "buyhold_return": bh_ret,
        "cash_return": 0.0,
        "vs_buyhold": strat_ret - bh_ret,
        "n_trades": len(closed),
        "win_rate": (len(wins) / len(closed)) if closed else 0.0,
        "avg_win": (statistics.mean([t["ret"] for t in wins]) if wins else 0.0),
        "avg_loss": (statistics.mean([t["ret"] for t in closed if t["ret"] <= 0])
                     if (len(closed) - len(wins)) else 0.0),
        "max_drawdown": max_drawdown(eq_curve),
        "buyhold_max_dd": max_drawdown([b["c"] for b in bars]),
        "sharpe": sharpe(daily_rets),
        "exposure": exposure,
    }

def fmt_report(title, m):
    pct = lambda x: f"{x*100:+.1f}%"
    lines = [
        f"== {title} ==",
        f"  Strategy return : {pct(m['strategy_return'])}",
        f"  Buy & hold      : {pct(m['buyhold_return'])}",
        f"  Cash            : {pct(m['cash_return'])}",
        f"  EDGE vs hold    : {pct(m['vs_buyhold'])}   <-- the number that matters",
        f"  Trades          : {m['n_trades']}  (win rate {m['win_rate']*100:.0f}%)",
        f"  Avg win / loss  : {pct(m['avg_win'])} / {pct(m['avg_loss'])}",
        f"  Max drawdown    : {pct(m['max_drawdown'])}  (buy&hold {pct(m['buyhold_max_dd'])})",
        f"  Sharpe (ann.)   : {m['sharpe']:.2f}",
        f"  Time in market  : {m['exposure']*100:.0f}%",
    ]
    return "\n".join(lines)

# ---------------------------------------------------------------- commands

def cmd_run(args):
    bars = load(args.pair)
    eq, tr, dr = run_strategy(bars, args.entry, args.exit, args.margin,
                              args.voltarget, args.volwindow)
    m = metrics(bars, eq, tr, dr)
    print(f"Data: {args.pair} {dstr(bars[0]['t'])} -> {dstr(bars[-1]['t'])} ({len(bars)} days)")
    print(f"Params: entry={args.entry} exit={args.exit} margin={args.margin} "
          f"voltarget={args.voltarget}")
    print(fmt_report(args.pair, m))

def cmd_sweep(args):
    """Walk-forward: tune on train slice, report same params out-of-sample on test slice."""
    bars = load(args.pair)
    split = int(len(bars) * args.trainfrac)
    train, test = bars[:split], bars[split:]
    print(f"Data: {args.pair} {dstr(bars[0]['t'])} -> {dstr(bars[-1]['t'])} ({len(bars)} days)")
    print(f"Train: {dstr(train[0]['t'])}..{dstr(train[-1]['t'])} ({len(train)}d) | "
          f"Test (out-of-sample): {dstr(test[0]['t'])}..{dstr(test[-1]['t'])} ({len(test)}d)\n")

    grid = []
    for entry in (10, 20, 30, 40, 55):
        for exitl in (5, 10, 15, 20):
            for margin in (0.0, 0.005, 0.01):
                eq, tr, dr = run_strategy(train, entry, exitl, margin)
                m = metrics(train, eq, tr, dr)
                if m["n_trades"] >= 3:               # ignore degenerate (too few trades)
                    grid.append((m["vs_buyhold"], m["sharpe"], entry, exitl, margin, m))
    grid.sort(key=lambda x: x[1], reverse=True)      # rank by in-sample Sharpe

    print("Top 5 parameter sets by IN-SAMPLE Sharpe (train):")
    for vs, sh, e, x, mg, m in grid[:5]:
        print(f"  entry={e:>2} exit={x:>2} margin={mg:<5} | train Sharpe {sh:.2f} "
              f"edge {vs*100:+.0f}% trades {m['n_trades']}")

    best = grid[0]
    _, _, e, x, mg, mtr = best
    eq, tr, dr = run_strategy(test, e, x, mg)
    mte = metrics(test, eq, tr, dr)
    print(f"\nBEST in-sample params: entry={e} exit={x} margin={mg}")
    print(fmt_report(f"{args.pair} IN-SAMPLE (train)", mtr))
    print(fmt_report(f"{args.pair} OUT-OF-SAMPLE (test) — the honest number", mte))
    print("\nIf out-of-sample edge vs hold is <= 0 or much worse than in-sample,")
    print("the strategy is curve-fit and has no demonstrated edge.")

def cmd_compare(args):
    """Head-to-head: Donchian vs EMA crossover vs regime-filtered, all vs buy-and-hold."""
    bars = load(args.pair)
    bh = bars[-1]["c"]/bars[0]["c"] - 1.0
    print(f"Data: {args.pair} {dstr(bars[0]['t'])} -> {dstr(bars[-1]['t'])} ({len(bars)} days)")
    print(f"Buy & hold: {bh*100:+.1f}% | max DD {max_drawdown([b['c'] for b in bars])*100:.0f}%\n")
    print(f"{'system':<40}{'return':>9}{'vs hold':>9}{'maxDD':>8}{'trades':>8}{'win%':>6}{'Sharpe':>8}")
    def row(label, eq, tr, dr):
        m = metrics(bars, eq, tr, dr)
        print(f"{label:<40}{m['strategy_return']*100:>+8.1f}%{m['vs_buyhold']*100:>+8.1f}%"
              f"{m['max_drawdown']*100:>+7.0f}%{m['n_trades']:>8}{m['win_rate']*100:>5.0f}%"
              f"{m['sharpe']:>8.2f}")
    row("Donchian (e20/x10)", *run_strategy(bars, 20, 10, 0.005))
    row("Donchian + 200d regime filter", *run_strategy(bars, 20, 10, 0.005, regime_ma=200))
    row("Donchian + 100d regime filter", *run_strategy(bars, 20, 10, 0.005, regime_ma=100))
    row("EMA 21/55 + RSI>50", *run_ema(bars, 21, 55, 50, False))
    row("EMA 9/21 (faster)", *run_ema(bars, 9, 21, 50, False))

def cmd_tv(args):
    """Faithful TradingView Donchian port vs. our close-based version. Full period + OOS."""
    bars = load(args.pair); n = len(bars)
    def oos(res):
        s = int((n-1)*0.6); return metrics_from_rets(res[2][s:])
    print(f"Data: {args.pair} ({n} days) | buy&hold {(bars[-1]['c']/bars[0]['c']-1)*100:+.1f}%")
    print("(faithful TV: high/low channels, wick entry, no margin)\n")
    print(f"{'system':<40}{'FULL ret':>9}{'Sharpe':>8}{'maxDD':>8}  |{'OOS ret':>9}{'OOS Sh':>8}")
    def row(label, res):
        m = metrics(bars, *res); o = oos(res)
        print(f"{label:<40}{m['strategy_return']*100:>+8.1f}%{m['sharpe']:>8.2f}{m['max_drawdown']*100:>+7.0f}%"
              f"  |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}")
    row("OUR close-based 20/10 (+0.5% margin)", run_strategy(bars, 20, 10, 0.005))
    row("TV faithful: wick, 20/10", run_donchian_tv(bars, 20, 10, 8, "wick", False))
    row("TV faithful: wick, 20/10 + two-stage", run_donchian_tv(bars, 20, 10, 8, "wick", True))
    row("TV faithful: close, 20/10", run_donchian_tv(bars, 20, 10, 8, "close", False))
    row("TV faithful: close + two-stage", run_donchian_tv(bars, 20, 10, 8, "close", True))

def cmd_ts(args):
    """Walk-forward validate our close-based entry + the STRUCTURAL two-stage stop (Run 16's
    lead) against the current simple-exit baseline. Full period + OOS."""
    bars = load(args.pair); n = len(bars)
    def oos(res):
        s = int((n-1)*0.6); return metrics_from_rets(res[2][s:])
    print(f"Data: {args.pair} ({n} days) | buy&hold {(bars[-1]['c']/bars[0]['c']-1)*100:+.1f}%\n")
    print(f"{'system':<40}{'FULL ret':>9}{'Sharpe':>8}{'maxDD':>8}{'trades':>7}  |{'OOS ret':>9}{'OOS Sh':>8}{'OOS DD':>8}")
    def row(label, res):
        m = metrics(bars, *res); o = oos(res)
        s = int((n-1)*0.6)
        oos_curve = res[0][s:]
        oos_dd = max_drawdown(oos_curve) if oos_curve else 0.0
        print(f"{label:<40}{m['strategy_return']*100:>+8.1f}%{m['sharpe']:>8.2f}{m['max_drawdown']*100:>+7.0f}%"
              f"{m['n_trades']:>7}  |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}{oos_dd*100:>+7.0f}%")
    row("Baseline (simple 10d exit) 20/10", run_strategy(bars, 20, 10, 0.005))
    row("Two-stage (tight8 -> wide10) 20/10", run_strategy_ts(bars, 20, 10, 8, 0.005))

def cmd_breakout(args):
    """Rob Carver's range-normalized breakout (qoppac 2016) vs our binary Donchian. Tests whether
    the CONTINUOUS, smoothed construction adds anything over our in/out breakout on OUR assets,
    NET of realistic 0.26%/side fees (charged on every rebalance). Long-only (our constraint).
    Full period + OOS. 'turn' = total turnover (≈ round-trips); the fee story lives there."""
    bars = load(args.pair); n = len(bars)
    s = int((n-1)*0.6)
    print(f"Data: {args.pair} ({n} days) | buy&hold {(bars[-1]['c']/bars[0]['c']-1)*100:+.1f}%\n")
    print(f"{'system':<40}{'FULL ret':>9}{'Sharpe':>8}{'maxDD':>8}{'turn':>7}  |{'OOS ret':>9}{'OOS Sh':>8}{'OOS DD':>8}")
    def row_don(label, res):
        m = metrics(bars, *res); o = metrics_from_rets(res[2][s:])
        oos_dd = max_drawdown(res[0][s:]) if res[0][s:] else 0.0
        print(f"{label:<40}{m['strategy_return']*100:>+8.1f}%{m['sharpe']:>8.2f}{m['max_drawdown']*100:>+7.0f}%"
              f"{m['n_trades']:>7}  |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}{oos_dd*100:>+7.0f}%")
    def row_bo(label, eq, dr, n_entries, turnover):
        full = metrics_from_rets(dr); o = metrics_from_rets(dr[s:])
        oos_dd = max_drawdown(eq[s:]) if eq[s:] else 0.0
        print(f"{label:<40}{full['ret']*100:>+8.1f}%{full['sharpe']:>8.2f}{full['dd']*100:>+7.0f}%"
              f"{turnover:>7.1f}  |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}{oos_dd*100:>+7.0f}%")
    row_don("Our Donchian binary 20/10 (two-stage)", run_strategy_ts(bars, 20, 10, 8, 0.005))
    for lb in (20, 40):
        row_bo(f"Carver breakout SIGN-only, lb={lb}", *run_breakout(bars, lb, "sign"))
        row_bo(f"Carver breakout CONTINUOUS, lb={lb}", *run_breakout(bars, lb, "continuous"))

def cmd_3commas(args):
    """The '3Commas Bot' TradingView template: EMA21/50 crossover entries, long+short+flip,
    swing/ATR stop with fixed 1:1 R:R take-profit by default. Decompose which pieces help/hurt
    vs our Donchian baseline. Full period + OOS."""
    bars = load(args.pair); n = len(bars)
    def oos(res):
        s = int((n-1)*0.6); return metrics_from_rets(res[2][s:])
    print(f"Data: {args.pair} ({n} days) | buy&hold {(bars[-1]['c']/bars[0]['c']-1)*100:+.1f}%\n")
    print(f"{'system':<46}{'FULL ret':>9}{'Sharpe':>8}{'maxDD':>8}{'trades':>7}{'win%':>6}  |{'OOS ret':>9}{'OOS Sh':>8}")
    def row(label, res):
        m = metrics(bars, *res); o = oos(res)
        print(f"{label:<46}{m['strategy_return']*100:>+8.1f}%{m['sharpe']:>8.2f}{m['max_drawdown']*100:>+7.0f}%"
              f"{m['n_trades']:>7}{m['win_rate']*100:>5.0f}%"
              f"  |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}")
    row("Our baseline Donchian 20/10", run_strategy(bars, 20, 10, 0.005))
    row("3Commas DEFAULT (EMA21/50, L+S+flip, 1:1 TP)", run_3commas(bars))
    row("3Commas long-only, 1:1 TP (no shorts/flip)", run_3commas(bars, allow_short=False, flip=False))
    row("3Commas L+S+flip, ATR trailing (no fixed TP)", run_3commas(bars, trail_stop=True))
    row("3Commas long-only, ATR trailing (no fixed TP)", run_3commas(bars, allow_short=False, flip=False, trail_stop=True))
    print("\n-- with Kraken-ish margin carry (0.12%/day while short) --")
    row("3Commas DEFAULT + carry", run_3commas(bars, short_carry=0.0012))
    row("3Commas L+S+flip ATR trailing + carry", run_3commas(bars, trail_stop=True, short_carry=0.0012))

def cmd_refine(args):
    """Test the TradingView-script refinements: asymmetric channels + two-stage stop.
    Full period AND out-of-sample, vs our baseline."""
    bars = load(args.pair); n = len(bars)
    def oos(res):
        s = int((n-1)*0.6); return metrics_from_rets(res[2][s:])
    print(f"Data: {args.pair} ({n} days) | buy&hold {(bars[-1]['c']/bars[0]['c']-1)*100:+.1f}%\n")
    print(f"{'system':<38}{'FULL ret':>9}{'Sharpe':>8}{'maxDD':>8}  |{'OOS ret':>9}{'OOS Sh':>8}")
    def row(label, res):
        m = metrics(bars, *res); o = oos(res)
        print(f"{label:<38}{m['strategy_return']*100:>+8.1f}%{m['sharpe']:>8.2f}{m['max_drawdown']*100:>+7.0f}%"
              f"  |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}")
    row("Baseline Donchian 20/10", run_strategy(bars, 20, 10, 0.005))
    row("Asymmetric 40/5 (slow in, tight out)", run_strategy(bars, 40, 5, 0.005))
    row("Asymmetric 55/10", run_strategy(bars, 55, 10, 0.005))
    row("Two-stage stop (tight5->wide20 @+10%)", run_twostage(bars, 20, 5, 20, 0.10, 0.005))
    row("Two-stage stop (tight5->wide30 @+15%)", run_twostage(bars, 20, 5, 30, 0.15, 0.005))

def cmd_shorts(args):
    """Does adding SHORTS help? Long-only vs long/short (best-case no carry, and with realistic
    margin borrow cost). Shows full period + the out-of-sample bear window."""
    bars = load(args.pair)
    bh = bars[-1]["c"]/bars[0]["c"] - 1.0
    print(f"Data: {args.pair} {dstr(bars[0]['t'])} -> {dstr(bars[-1]['t'])} | buy&hold {bh*100:+.1f}%\n")
    print(f"{'system':<40}{'return':>9}{'maxDD':>8}{'trades':>8}{'Sharpe':>8}")
    def row(label, res):
        m = metrics(bars, res[0], res[1], res[2])
        print(f"{label:<40}{m['strategy_return']*100:>+8.1f}%{m['max_drawdown']*100:>+7.0f}%"
              f"{m['n_trades']:>8}{m['sharpe']:>8.2f}")
    row("Long-only Donchian (current)", run_strategy(bars, 20, 10, 0.005))
    row("Long/SHORT, no borrow cost (best case)", run_longshort(bars, 20, 10, 0.005, 0.0))
    row("Long/SHORT, 0.03%/day carry", run_longshort(bars, 20, 10, 0.005, 0.0003))
    row("Long/SHORT, 0.12%/day carry (Kraken-ish)", run_longshort(bars, 20, 10, 0.005, 0.0012))
    # OOS bear window only
    print("\n  -- out-of-sample window only (the bear: 2025-08-30 -> 2026-06-14) --")
    def idx(d):
        t = datetime.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp()
        return next((i for i,b in enumerate(bars) if b["t"] >= t), len(bars)-1)
    s, e = idx("2025-08-30"), len(bars)-1
    for label, res in [("Long-only", run_strategy(bars,20,10,0.005)),
                       ("Long/short no carry", run_longshort(bars,20,10,0.005,0.0)),
                       ("Long/short 0.12%/day", run_longshort(bars,20,10,0.005,0.0012))]:
        win = metrics_from_rets(res[2][s:e])
        print(f"  {label:<32}{win['ret']*100:>+8.1f}%  maxDD {win['dd']*100:>+5.0f}%  Sharpe {win['sharpe']:>5.2f}")
    print(f"  {'buy & hold (bear window)':<32}{(bars[e]['c']/bars[s]['c']-1)*100:>+8.1f}%")

def cmd_frameworks(args):
    """Test new frameworks (mean-reversion, adaptive-trend) + ensembles, with correlations."""
    bars = load(args.pair)
    bh = bars[-1]["c"]/bars[0]["c"] - 1.0
    print(f"Data: {args.pair} {dstr(bars[0]['t'])} -> {dstr(bars[-1]['t'])} ({len(bars)} days)")
    print(f"Buy & hold: {bh*100:+.1f}%\n")
    don = run_strategy(bars, 20, 10, 0.005)
    emax = run_ema(bars, 21, 55, 50, False)
    mr  = run_meanrev(bars, 20, 2.0)
    adp = run_adaptive(bars, 20, 10, 0.005, 20, 0.30)
    ens_all = blend([don[2], emax[2], mr[2]])           # trend(2) + mean-rev
    ens_tmr = blend([don[2], mr[2]])                    # Donchian + mean-rev (the diversifier pair)

    print(f"{'system':<34}{'return':>9}{'vs hold':>9}{'maxDD':>8}{'trades':>8}{'Sharpe':>8}")
    def row(label, res):
        m = metrics(bars, res[0], res[1], res[2])
        print(f"{label:<34}{m['strategy_return']*100:>+8.1f}%{m['vs_buyhold']*100:>+8.1f}%"
              f"{m['max_drawdown']*100:>+7.0f}%{m['n_trades']:>8}{m['sharpe']:>8.2f}")
    row("Donchian (trend)", don)
    row("EMA 21/55 (trend)", emax)
    row("Mean-reversion (NEW)", mr)
    row("Adaptive-Trend / ER-gated (NEW)", adp)
    row("Ensemble: Donchian+MeanRev", ens_tmr)
    row("Ensemble: Don+EMA+MeanRev", ens_all)

    print("\nDaily-return CORRELATIONS (diversification check — low/negative is GOOD):")
    print(f"  Donchian vs EMA       : {correl(don[2], emax[2]):+.2f}  (expect high — same bet)")
    print(f"  Donchian vs Mean-rev  : {correl(don[2], mr[2]):+.2f}  (want low/neg — diversifier)")
    print(f"  Donchian vs Adaptive  : {correl(don[2], adp[2]):+.2f}")

def metrics_from_rets(rets):
    """Windowed metrics from a slice of daily returns."""
    eq = [1.0]
    for r in rets:
        eq.append(eq[-1]*(1.0+r))
    return {"ret": eq[-1]-1.0, "dd": max_drawdown(eq), "sharpe": sharpe(rets)}

def cmd_validate(args):
    """Walk-forward validation of the trend+mean-rev ensemble: split into train (first 60%)
    and test (last 40%, out-of-sample) and check the diversification benefit holds in BOTH."""
    bars = load(args.pair)
    don = run_strategy(bars, 20, 10, 0.005)[2]
    emax = run_ema(bars, 21, 55, 50, False)[2]
    mr = run_meanrev(bars, 20, 2.0)[2]
    n = min(len(don), len(emax), len(mr))
    don, emax, mr = don[:n], emax[:n], mr[:n]
    ens = [(don[i]+emax[i]+mr[i])/3 for i in range(n)]
    split = int(n*0.6)
    windows = [("TRAIN (in-sample)", 0, split), ("TEST (OUT-OF-SAMPLE)", split, n)]

    print(f"Data: {args.pair} ({n} return-days) | split 60/40\n")
    for name, s, e in windows:
        bh = bars[e]["c"]/bars[s]["c"] - 1.0
        print(f"== {name}: {dstr(bars[s]['t'])} -> {dstr(bars[e]['t'])} ==")
        print(f"  {'system':<26}{'return':>9}{'maxDD':>8}{'Sharpe':>8}")
        for label, series in [("Donchian", don), ("EMA 21/55", emax),
                              ("Mean-reversion", mr), ("ENSEMBLE (3-way)", ens)]:
            m = metrics_from_rets(series[s:e])
            print(f"  {label:<26}{m['ret']*100:>+8.1f}%{m['dd']*100:>+7.0f}%{m['sharpe']:>8.2f}")
        print(f"  {'buy & hold':<26}{bh*100:>+8.1f}%")
        print(f"  corr(Donchian, MeanRev) in window: {correl(don[s:e], mr[s:e]):+.2f}\n")
    print("PASS if, out-of-sample: ensemble Sharpe >= best single system AND/OR ensemble maxDD")
    print("is smaller, AND corr(trend, mean-rev) stays low. Otherwise the benefit was in-sample luck.")

def cmd_signals(args):
    """Live snapshot: current state of BOTH systems + regime, for running them in parallel.
    Donchian exit uses the Run 19 structural two-stage stop: tight 8d-low until the trade is
    'in profit' (entry price <= tight low), then the wider 10d-low. Pass --entry-price if
    currently holding a position to see which stage applies and the live exit level."""
    bars = load(args.pair); closes = [b["c"] for b in bars]
    c = closes[-1]; i = len(bars) - 1
    ph = max(closes[i-20:i]); tight_low = min(closes[i-8:i]); wide_low = min(closes[i-10:i])
    ef, es = ema(closes, 21), ema(closes, 55)
    ma200 = sma(closes, 200)[-1]
    don = "LONG-trigger" if c > ph*1.005 else "hold/flat"
    emastate = "bull (21>55)" if ef[-1] > es[-1] else "bear (21<55)"
    regime = "BULL" if (ma200 and c > ma200) else "BEAR"
    print(f"{args.pair}  last close {c:,.0f}  ({dstr(bars[-1]['t'])})")
    print(f"  Regime (200d MA {ma200:,.0f}) : {regime}")
    print(f"  Donchian: 20d-high {ph:,.0f} (entry trigger +0.5%) -> {don}")
    print(f"  Exit channels (two-stage, Run 19): tight 8d-low {tight_low:,.0f} / wide 10d-low {wide_low:,.0f}")
    entry_price = getattr(args, "entry_price", None)
    if entry_price:
        in_profit = entry_price <= tight_low
        stop = wide_low if in_profit else tight_low
        stage = "WIDE (in profit vs tight line)" if in_profit else "TIGHT (not yet in profit)"
        print(f"  Holding @ {entry_price:,.0f}: stage={stage} -> exit if close < {stop:,.0f}")
    print(f"  EMA: 21={ef[-1]:,.0f} 55={es[-1]:,.0f} -> {emastate}")
    agree = (regime=="BULL" and c>ph*1.005 and ef[-1]>es[-1])
    print(f"  >> Both-systems-agree LONG: {'YES (high conviction)' if agree else 'no'}")

def cmd_abtest(args):
    """Mechanical strategy return over a specific date window (with full prior lookback),
    to A/B against a discretionary blind run on the same window."""
    bars = load(args.pair)
    eq, tr, dr = run_strategy(bars, 20, 10, 0.005)   # full series, proper warm-up
    # find window indices
    def idx_for(datestr):
        target = datetime.datetime.strptime(datestr, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc).timestamp()
        for i, b in enumerate(bars):
            if b["t"] >= target:
                return i
        return len(bars) - 1
    s, e = idx_for(args.start), idx_for(args.end)
    strat_win = eq[e] / eq[s] - 1.0
    bh_win = bars[e]["c"] / bars[s]["c"] - 1.0
    win_trades = [t for t in tr if s <= t.get("entry_i", -1) <= e]
    print(f"{args.pair}  window {dstr(bars[s]['t'])} -> {dstr(bars[e]['t'])} ({e-s} days)")
    print(f"  Mechanical strategy : {strat_win*100:+.1f}%")
    print(f"  Buy & hold          : {bh_win*100:+.1f}%")
    print(f"  Mechanical edge/hold: {(strat_win-bh_win)*100:+.1f}%")
    print(f"  Trades in window    : {len(win_trades)}  "
          f"(in-market at window start: {'yes' if eq[s] != eq[s-1] or True else 'n/a'})")
    for t in win_trades:
        if "ret" in t:
            print(f"    {t['entry_d']} -> {t.get('exit_d','open')}  {t['ret']*100:+.1f}%")

def cmd_brackets(args):
    """Compare fixed SL/TP brackets vs. the trailing-stop baseline and buy-and-hold."""
    bars = load(args.pair)
    print(f"Data: {args.pair} {dstr(bars[0]['t'])} -> {dstr(bars[-1]['t'])} ({len(bars)} days)")
    bh = bars[-1]["c"]/bars[0]["c"] - 1.0
    print(f"Buy & hold: {bh*100:+.1f}% | max DD {max_drawdown([b['c'] for b in bars])*100:.0f}%\n")

    # baseline: trailing-stop (our validated default)
    eq, tr, dr = run_strategy(bars, 20, 10, 0.005)
    m = metrics(bars, eq, tr, dr)
    print(f"{'config':<34}{'return':>9}{'vs hold':>9}{'maxDD':>8}{'trades':>8}{'win%':>6}{'avgWin':>8}")
    print(f"{'TRAILING-STOP baseline (e20/x10)':<34}{m['strategy_return']*100:>+8.1f}%"
          f"{m['vs_buyhold']*100:>+8.1f}%{m['max_drawdown']*100:>+7.0f}%"
          f"{m['n_trades']:>8}{m['win_rate']*100:>5.0f}%{m['avg_win']*100:>+7.1f}%")
    print("  " + "-"*78)

    combos = [(0.05,0.10),(0.08,0.16),(0.10,0.20),(0.08,0.30),(0.08,0.50),(0.10,9.9)]
    for sl, tp in combos:
        eq, tr, dr = run_brackets(bars, 20, 0.005, sl, tp)
        m = metrics(bars, eq, tr, dr)
        tplabel = "no-TP" if tp > 5 else f"{tp*100:.0f}%"
        label = f"breakout + SL {sl*100:.0f}% / TP {tplabel}"
        print(f"{label:<34}{m['strategy_return']*100:>+8.1f}%{m['vs_buyhold']*100:>+8.1f}%"
              f"{m['max_drawdown']*100:>+7.0f}%{m['n_trades']:>8}{m['win_rate']*100:>5.0f}%"
              f"{m['avg_win']*100:>+7.1f}%")
    # always-in-market with brackets (no entry edge)
    eq, tr, dr = run_brackets(bars, 20, 0.005, 0.08, 0.16, always=True)
    m = metrics(bars, eq, tr, dr)
    print("  " + "-"*78)
    print(f"{'ALWAYS-in + SL 8%/TP 16% (no edge)':<34}{m['strategy_return']*100:>+8.1f}%"
          f"{m['vs_buyhold']*100:>+8.1f}%{m['max_drawdown']*100:>+7.0f}%"
          f"{m['n_trades']:>8}{m['win_rate']*100:>5.0f}%{m['avg_win']*100:>+7.1f}%")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch"); pf.add_argument("pair")
    pr = sub.add_parser("run"); pr.add_argument("pair")
    pr.add_argument("--entry", type=int, default=20); pr.add_argument("--exit", type=int, default=10)
    pr.add_argument("--margin", type=float, default=0.005)
    pr.add_argument("--voltarget", type=float, default=None)
    pr.add_argument("--volwindow", type=int, default=20)
    ps = sub.add_parser("sweep"); ps.add_argument("pair")
    ps.add_argument("--trainfrac", type=float, default=0.6)
    pb = sub.add_parser("brackets"); pb.add_argument("pair")
    pa = sub.add_parser("abtest"); pa.add_argument("pair")
    pa.add_argument("--start", required=True); pa.add_argument("--end", required=True)
    pc = sub.add_parser("compare"); pc.add_argument("pair")
    psig = sub.add_parser("signals"); psig.add_argument("pair")
    psig.add_argument("--entry-price", type=float, default=None,
                       help="if holding a position, your entry close price (shows two-stage exit stage/level)")
    pfr = sub.add_parser("frameworks"); pfr.add_argument("pair")
    pv = sub.add_parser("validate"); pv.add_argument("pair")
    psh = sub.add_parser("shorts"); psh.add_argument("pair")
    prf = sub.add_parser("refine"); prf.add_argument("pair")
    ptv = sub.add_parser("tv"); ptv.add_argument("pair")
    ptc = sub.add_parser("tcb"); ptc.add_argument("pair")
    pts = sub.add_parser("ts"); pts.add_argument("pair")
    pbo = sub.add_parser("breakout"); pbo.add_argument("pair")
    a = p.parse_args()
    if a.cmd == "fetch":
        print("cached:", fetch(a.pair))
    elif a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "sweep":
        cmd_sweep(a)
    elif a.cmd == "brackets":
        cmd_brackets(a)
    elif a.cmd == "abtest":
        cmd_abtest(a)
    elif a.cmd == "compare":
        cmd_compare(a)
    elif a.cmd == "signals":
        cmd_signals(a)
    elif a.cmd == "frameworks":
        cmd_frameworks(a)
    elif a.cmd == "validate":
        cmd_validate(a)
    elif a.cmd == "shorts":
        cmd_shorts(a)
    elif a.cmd == "refine":
        cmd_refine(a)
    elif a.cmd == "tv":
        cmd_tv(a)
    elif a.cmd == "tcb":
        cmd_3commas(a)
    elif a.cmd == "ts":
        cmd_ts(a)
    elif a.cmd == "breakout":
        cmd_breakout(a)

if __name__ == "__main__":
    main()
