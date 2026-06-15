# kraken-trading

A disciplined, mechanical crypto paper-trading workflow for **BTCEUR / ETHEUR** on a small
(€1,000) unleveraged spot account. The whole point of this system is to resist the impulses that
lose retail traders money: it trades only *confirmed breaks*, sits in cash when there's no signal,
and treats trend-following as a **risk-reduction tool, not a money-printer** (there is no
demonstrated out-of-sample alpha — see `backtest_journal.md`).

> **Paper / analysis only. Nothing here places, amends, or cancels a real order.** The tooling
> *proposes*; a human executes. Keep it that way.

## What's here

| File | Purpose |
|---|---|
| `backtester.py` | The mechanical engine: Donchian breakout + two-stage exit, EMA, regime, walk-forward validation. Pulls data from Kraken's **public REST API** (stdlib only, no key, no CLI). |
| `watch.py` | The daily watcher. Fresh data → regime / Donchian / EMA snapshot + break-quality filter → "all quiet" or "CONFIRMED break". Never trades. |
| `levels_watch.md` | Current per-asset trigger levels (the watcher reads these). |
| `trading_journal.md` | The live decision log / track record being graded. |
| `backtest_journal.md` | Every backtest run + the lessons that justify each rule. |
| `sources.md` | Vetted, credibility-tiered news sources (+ blocklist). |
| `.claude/loop.md` | Instructions the cloud Routine follows each run. |

## Run it by hand

No dependencies beyond Python 3:

```bash
python3 watch.py                      # daily watch for BTCEUR + ETHEUR
python3 backtester.py run BTCEUR      # single backtest (auto-fetches data)
python3 backtester.py signals BTCEUR  # live parallel-systems snapshot
python3 backtester.py ts BTCEUR       # two-stage exit walk-forward (Run 19)
python3 backtester.py breakout BTCEUR # Carver breakout comparison (Run 20)
```

`watch.py` exits `10` when a confirmed break has fired and `0` when all quiet, so a plain cron
job can branch on it: `python3 watch.py || notify-me`.

## Run it in the cloud (computer off) — Claude Code Routines

A [Routine](https://code.claude.com/docs/en/routines) runs a Claude Code session on Anthropic's
cloud on a schedule, from a **fresh clone of this repo** — no local machine required. Because it's a
fresh clone, the engine deliberately has **no local dependencies** (public API, stdlib only).

To create the daily routine, from a Claude Code session use `/schedule`, e.g.:

```
/schedule every day at 1am, clone this repo and follow .claude/loop.md
```

The routine will run `watch.py`, interpret the result against the rules in `.claude/loop.md`, append
to `trading_journal.md`, commit/push, and produce a summary (which is your notification — loud if a
break fired, one line if quiet). Minimum routine interval is 1 hour; **daily** is the right cadence
for a daily-candle system — hourly just adds noise.

### Persistence & notifications

- The routine commits the journal update back to this repo so the record survives. If the cloud
  environment can't push, the run summary still tells you the verdict.
- For a phone/email push, add a webhook call (Telegram/Pushover/email) to the end of `.claude/loop.md`
  — not wired up yet.

## Rules baked in (see `backtest_journal.md` for the evidence)

- Trade **confirmed breaks**, never reversals/bounces. Marginal pokes don't count (≥0.5–1% margin).
- Exit = **two-stage trailing Donchian stop** (Run 19); **never a fixed take-profit** (Run 7).
- **Long-only / spot** — shorts tested worse net of carry + risk (Run 14).
- **FLAT is legitimate** and usually correct when there's no break.
- Don't re-optimize parameters — they overfit on this little data (Run 6).
