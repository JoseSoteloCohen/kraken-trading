# Key Levels Watchlist

Daily level-watch monitors these. **Alert only — never auto-trades.** A trigger means "a confirmed
break may be forming; review for an entry," not "trade now."

**Cadence (the hybrid):** Default WEEKLY decisions. When holding a position (LONG/SHORT) → hold to
the next weekly review. When FLAT → watch daily for a confirmed break to enter mid-week instead of
waiting a full week. **Break-quality filter:** only act if the close clears the level by a
meaningful margin (~≥0.5–1%), not a marginal poke — marginal daily breaks whipsaw (see Run 5 in
backtest_journal.md). When already in a position, don't micro-manage daily.

Account: **€1,000 EUR paper** | Pairs: **BTCEUR / ETHEUR** | Fees 0.26%/side (0.52% round trip).
Last reviewed: 2026-06-15 (21:36 UTC, intraday) | BTC ~€57,324 | ETH ~€1,568

## BTC/EUR
- **Downside trigger:** daily close meaningfully below **€51,000** (recent swing-low zone). Confirm → SHORT candidate.
- **Upside trigger:** daily close meaningfully above **€57,500** (recent resistance / chop ceiling). Confirm → LONG candidate.
- Current state (2026-06-15 intraday): bouncing toward €57,500 on a macro relief rally (US–Iran peace deal), ~0.3% below trigger. NOT a confirmed break. Bias FLAT pending the daily close (confirm = close ≥ ~€57,790).

## ETH/EUR
- **Downside trigger:** daily close meaningfully below **€1,400** (recent swing low). Confirm → SHORT candidate.
- **Upside trigger:** daily close meaningfully above **€1,550** (resistance band). Confirm → LONG candidate.
- Current state (2026-06-15 intraday): poking ~1.2% ABOVE €1,550 (live €1,568, high €1,594) on the same macro relief rally — NOT yet a confirmed daily close, and against a BEAR regime + EMA bear cross. Bias FLAT pending the close (confirm = close ≥ ~€1,558 → CAUTIOUS reduced-size LONG candidate, present for decision).

## Watch procedure (daily, when FLAT)
1. Pull price: `wsl -d Ubuntu -- bash -lc "kraken ticker BTCEUR -o json"` (and ETHEUR). Use "c"[0] = last trade price.
2. Compare last close vs. trigger levels. Apply the break-quality filter (meaningful margin, not a poke).
3. If a filtered trigger is hit: flag it (alert) + a quick Tier-1 news check (see sources.md). DO NOT place a trade — surface for the entry decision.
4. If nothing triggers: brief "all quiet" with distance to nearest trigger.
5. When holding a position: daily watch is informational only; decisions stay weekly.
6. Re-evaluate levels at each weekly decision and update here.
