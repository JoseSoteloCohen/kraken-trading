#!/usr/bin/env python3
"""Kraken Prop evaluation simulator.

Monte-Carlo (block-bootstrap) a strategy's real daily returns through Kraken Prop's actual rules to
estimate P(pass), P(daily-loss bust), P(max-DD bust). The honest answer to: can this strategy pass
the challenge, and at what exposure?

Kraken Prop rules (from https://www.kraken.com/prop, fetched 2026-06-15):
  - Single-step challenge, NO time limit, NO min trading days.
  - Max DAILY loss: 3% (static, all plans) -- measured here from each day's OPENING equity.
  - Max TOTAL drawdown (STATIC from starting balance): Starter 6% / Intermediate 5% / Advanced 3%.
  - Leverage up to 5x. 60+ crypto pairs -> our BTCEUR/ETHEUR data + validated systems apply.
  - Profit target varies by tier; passed as a parameter (default 8%).

"Exposure" E = effective notional / account equity. E=1 is fully-invested unleveraged; E=5 is the
max 5x leverage. Account daily return = E * (strategy's underlying daily return). The strategy's
daily_rets already encode position (0 when flat), so flat days contribute 0 regardless of E.

Usage: python3 prop_sim.py [PAIR=BTCEUR] [strat=twostage] [target=0.08]
       strat in: twostage | donchian | meanrev | breakout
"""
import sys, random
from backtester import load, run_strategy, run_strategy_ts, run_meanrev, run_breakout

PAIR   = sys.argv[1] if len(sys.argv) > 1 else "BTCEUR"
STRAT  = sys.argv[2] if len(sys.argv) > 2 else "twostage"
TARGET = float(sys.argv[3]) if len(sys.argv) > 3 else 0.08

DAILY_LIMIT = 0.03           # 3% max daily loss (all plans)
PLANS = [("Starter", 0.06), ("Intermediate", 0.05), ("Advanced", 0.03)]
HORIZON = 252                # ~1 trading year cap (no time limit, but barriers are absorbing)
N = 10000
BLOCK = 10                   # block bootstrap preserves vol-clustering / short trends


def strat_rets(pair, strat):
    bars = load(pair)
    if strat == "twostage": return run_strategy_ts(bars, 20, 10, 8, 0.005)[2]
    if strat == "donchian": return run_strategy(bars, 20, 10, 0.005)[2]
    if strat == "meanrev":  return run_meanrev(bars, 20, 2.0)[2]
    if strat == "breakout": return run_breakout(bars, 20, "sign")[1]
    raise SystemExit(f"unknown strat '{strat}'")


def block_bootstrap(rets, length, block, rng):
    out = []
    while len(out) < length:
        s = rng.randrange(0, len(rets))
        out.extend(rets[s:s + block])
    return out[:length]


def simulate(rets, exposure, target, maxdd, daily_lim=DAILY_LIMIT,
             horizon=HORIZON, n=N, block=BLOCK, seed=0):
    rng = random.Random(seed)
    passes = daily = dd = timeout = 0
    floor = 1.0 - maxdd                       # static floor from starting balance
    for _ in range(n):
        path = block_bootstrap(rets, horizon, block, rng)
        eq = 1.0; outcome = None
        for r in path:
            day_open = eq
            eq *= (1.0 + exposure * r)
            if eq <= day_open * (1.0 - daily_lim): outcome = "daily"; break
            if eq <= floor:                        outcome = "dd";    break
            if eq >= 1.0 + target:                 outcome = "pass";  break
        if   outcome == "pass":  passes += 1
        elif outcome == "daily": daily  += 1
        elif outcome == "dd":    dd     += 1
        else:                    timeout += 1
    return passes / n, daily / n, dd / n, timeout / n


def main():
    rets = strat_rets(PAIR, STRAT)
    # zero-edge gambler's-ruin benchmark (ignores daily limit & drift): floor/(target+floor)
    print(f"Kraken Prop simulator | {PAIR} | strategy={STRAT} | profit target {TARGET*100:.0f}% | "
          f"daily-loss limit {DAILY_LIMIT*100:.0f}%")
    print(f"  ({len(rets)} daily returns | {N:,} bootstrapped paths/cell | horizon {HORIZON}d | block {BLOCK}d)\n")
    for plan, maxdd in PLANS:
        gr = maxdd / (TARGET + maxdd)          # zero-edge, no-daily-limit reference
        print(f"== {plan} plan: max total drawdown {maxdd*100:.0f}% (static) | "
              f"zero-edge gambler's-ruin P(pass) refn {gr*100:.0f}% ==")
        print(f"  {'exposure':>9}{'P(pass)':>10}{'P(daily-bust)':>15}{'P(DD-bust)':>12}{'P(timeout)':>12}")
        for E in (1, 2, 3, 5):
            p, d, x, t = simulate(rets, E, TARGET, maxdd)
            print(f"  {str(E)+'x':>9}{p*100:>9.1f}%{d*100:>14.1f}%{x*100:>11.1f}%{t*100:>11.1f}%")
        print()


if __name__ == "__main__":
    main()
