#!/usr/bin/env python3
"""Cross-sectional momentum across a Kraken crypto universe — the first NEW-dimension edge hunt.

Hypothesis (pre-registered): within a basket of liquid coins, ranking by recent relative strength and
holding the top-K (rebalanced periodically) beats an equal-weight basket of the same universe on
RISK-ADJUSTED return (Sharpe), OUT-OF-SAMPLE (last 40%), net of 0.26%/side fees. Falsification: if
OOS Sharpe of top-K does NOT exceed the basket (and the market-neutral top-minus-bottom spread has
OOS Sharpe <= 0), there is no cross-sectional edge here.

This is genuinely different from all prior runs (single-asset time-series trend): it trades RELATIVE
strength, a different return source than absolute market direction.

Usage: python3 xsmom.py
"""
import sys
from backtester import load, dstr, FEE, metrics_from_rets, max_drawdown

UNIVERSE = ["BTCEUR", "ETHEUR", "SOLEUR", "XRPEUR", "ADAEUR", "DOTEUR", "LINKEUR",
            "LTCEUR", "BCHEUR", "AVAXEUR", "ATOMEUR", "XLMEUR", "TRXEUR", "XMREUR"]


def load_aligned(universe):
    series = {}
    for p in universe:
        bars = load(p)
        series[p] = {b["t"]: b["c"] for b in bars}
    common = sorted(set.intersection(*[set(s) for s in series.values()]))
    closes = {p: [series[p][t] for t in common] for p in universe}
    return common, closes


def basket_rets(closes, dates):
    """Equal-weight, daily-rebalanced basket = the 'crypto market' proxy."""
    pairs = list(closes); T = len(dates)
    return [sum(closes[p][t]/closes[p][t-1] - 1 for p in pairs) / len(pairs) for t in range(1, T)]


def bh_rets(closes, pair, dates):
    return [closes[pair][t]/closes[pair][t-1] - 1 for t in range(1, len(dates))]


def run_xsmom(closes, dates, L, R, K, mode="long", skip=0, fee=FEE):
    """Rank by past-L return (skipping the most recent `skip` days), long top-K equal-weight
    (longshort: also short bottom-K), rebalance every R days. Returns daily portfolio returns,
    net of turnover fees. No look-ahead: decide at close t from data <= t, earn t -> t+1."""
    pairs = list(closes); T = len(dates)
    weights = {p: 0.0 for p in pairs}
    port = []
    for t in range(1, T):
        day_ret = sum(weights[p] * (closes[p][t]/closes[p][t-1] - 1) for p in pairs)
        port.append(day_ret)
        if t >= L + skip and t % R == 0:
            sig = {p: closes[p][t-skip]/closes[p][t-skip-L] - 1 for p in pairs}
            ranked = sorted(pairs, key=lambda p: sig[p], reverse=True)
            new_w = {p: 0.0 for p in pairs}
            for p in ranked[:K]:
                new_w[p] += 1.0 / K
            if mode == "longshort":
                for p in ranked[-K:]:
                    new_w[p] -= 1.0 / K
            turnover = sum(abs(new_w[p] - weights[p]) for p in pairs)
            port[-1] -= fee * turnover
            weights = new_w
    return port


def row(label, rets, split):
    f = metrics_from_rets(rets); o = metrics_from_rets(rets[split:])
    print(f"  {label:<34}{f['ret']*100:>+8.1f}%{f['sharpe']:>8.2f}{f['dd']*100:>+7.0f}%"
          f"   |{o['ret']*100:>+8.1f}%{o['sharpe']:>8.2f}{o['dd']*100:>+7.0f}%")


def main():
    dates, closes = load_aligned(UNIVERSE)
    T = len(dates); split = int((T - 1) * 0.6)
    print(f"Cross-sectional momentum | {len(UNIVERSE)} coins | {T} days "
          f"{dstr(dates[0])} -> {dstr(dates[-1])} | OOS = last 40%\n")
    basket = basket_rets(closes, dates)
    btc = bh_rets(closes, "BTCEUR", dates)

    hdr = f"  {'system':<34}{'FULL ret':>9}{'Sharpe':>8}{'maxDD':>8}   |{'OOS ret':>9}{'OOS Sh':>8}{'OOS DD':>8}"
    print(hdr)
    row("BTC buy & hold", btc, split)
    row("Equal-weight basket (benchmark)", basket, split)
    print()

    # primary config + robustness grid; judge CONSISTENCY, not the max (Run 6/20 lesson)
    configs = [(30, 7, 3), (20, 7, 3), (60, 7, 3), (90, 14, 4), (30, 7, 4)]
    print("  -- long top-K (our tradeable, long-only/spot) --")
    for L, R, K in configs:
        tag = f"L{L} R{R} K{K}" + ("  <-- primary" if (L, R, K) == (30, 7, 3) else "")
        row(tag, run_xsmom(closes, dates, L, R, K, "long"), split)
    print("\n  -- top-minus-bottom (market-neutral DIAGNOSTIC: is there ANY x-sec signal?) --")
    for L, R, K in configs:
        row(f"L{L} R{R} K{K}", run_xsmom(closes, dates, L, R, K, "longshort"), split)

    print("\nPASS only if long top-K OOS Sharpe > basket OOS Sharpe CONSISTENTLY across configs,")
    print("or the market-neutral spread has a consistent positive OOS Sharpe. One lucky cell = noise.")


if __name__ == "__main__":
    main()
