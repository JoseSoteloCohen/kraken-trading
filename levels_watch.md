# Key Levels Watchlist

Daily level-watch monitors these. **Alert only — never auto-trades.** A trigger means "a confirmed
break may be forming; review for an entry," not "trade now."

**Long-only / spot (Run 14):** only an **upside** break is an entry signal. A **downside** break is
NOT a short — when FLAT it just means "stay in cash"; when holding a long it confirms the trend has
turned (the two-stage trailing stop is the actual exit).

**Cadence (the hybrid):** Default WEEKLY decisions. When holding a position (LONG/SHORT) → hold to
the next weekly review. When FLAT → watch daily for a confirmed break to enter mid-week instead of
waiting a full week. **Break-quality filter:** only act if the close clears the level by a
meaningful margin (~≥0.5–1%), not a marginal poke — marginal daily breaks whipsaw (see Run 5 in
backtest_journal.md). When already in a position, don't micro-manage daily.

Account: **€1,000 EUR paper** | Pairs: **BTCEUR / ETHEUR** | Fees 0.26%/side (0.52% round trip).
Last reviewed: 2026-06-16 | BTC ~€56,572 | ETH ~€1,545

## BTC/EUR
- **Downside trigger:** daily close meaningfully below **€51,000** (recent swing-low zone). Long-only/spot (Run 14): if FLAT, **stay in CASH — no short**; if holding a long, the two-stage trailing stop (8d/10d low) is the exit and this confirms the trend has turned.
- **Upside trigger:** daily close meaningfully above **€57,500** (recent resistance / chop ceiling). Confirm → LONG candidate.
- Current state: 2026-06-16 — FLAT. The 06-15 relief pop (US–Iran) faded; price ~€56,600, well below the €57,500 trigger, BEAR regime, EMA bearish. No confirmed break.

## ETH/EUR
- **Downside trigger:** daily close meaningfully below **€1,400** (recent swing low). Long-only/spot (Run 14): if FLAT, **stay in CASH — no short**; if holding a long, the two-stage trailing stop (8d/10d low) is the exit and this confirms the trend has turned.
- **Upside trigger:** daily close meaningfully above **€1,550** (resistance band). Confirm → LONG candidate.
- Current state: 2026-06-16 — FLAT. The 06-15 intraday spike to €1,594 closed back at €1,549 (below €1,550) and is ~€1,545; BEAR regime, EMA bearish. No confirmed break.

## Watch procedure (daily, when FLAT)
1. Pull price: `wsl -d Ubuntu -- bash -lc "kraken ticker BTCEUR -o json"` (and ETHEUR). Use "c"[0] = last trade price.
2. Compare last close vs. trigger levels. Apply the break-quality filter (meaningful margin, not a poke).
3. If a filtered trigger is hit: flag it (alert) + a quick Tier-1 news check (see sources.md). DO NOT place a trade — surface for the entry decision.
4. If nothing triggers: brief "all quiet" with distance to nearest trigger.
5. When holding a position: daily watch is informational only; decisions stay weekly.
6. Re-evaluate levels at each weekly decision and update here.
