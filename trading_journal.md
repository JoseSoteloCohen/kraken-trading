# Paper Trading Journal

Tracks Claude's market recommendations/decisions vs. actual outcomes, to assess accuracy over time.

Setup:
- Kraken CLI v0.3.2, installed via WSL Ubuntu (`wsl -d Ubuntu -- kraken ...`)
- Spot paper account initialized: $10,000 USD, 0.26% taker fee, 0% slippage
- Reset anytime with `kraken paper reset`

## How entries work

Each entry below is added when Claude makes a recommendation/trade. Later, the "Outcome" section is filled in by re-checking `kraken ticker` and `kraken paper status`.

Entry template:

```
### YYYY-MM-DD HH:MM — PAIR
- Market snapshot: price, relevant context/indicators discussed
- Recommendation/reasoning: what Claude suggested and why
- Action taken: paper order placed (order_id, side, volume, price, fee) or "no action"
- Prediction: expected direction/target and timeframe to review by
- Review (filled in later): actual price at review time, outcome vs. prediction, was the reasoning correct?
```

---

## Entries

### 2026-06-15 — BTCEUR
- Market snapshot: price ~€56,412 (last close €56,166 on 2026-06-14). Regime BEAR (200d MA €66,446).
  Donchian: 20d-high €66,417 (entry trigger +0.5% = ~€66,750) -> hold/flat, far below. EMA bear
  (21=€57,751 < 55=€61,191). Two-stage exit channels (Run 19): tight 8d-low €52,923 / wide 10d-low
  €52,923 (n/a, no open position). levels_watch.md triggers: downside €51,000 / upside €57,500 —
  neither broken (price is between them, chopping).
- Recommendation/reasoning: FLAT. No confirmed break of either watch level, no Donchian entry
  trigger, EMA and regime both bearish, no both-systems-agree LONG signal. Per the skill, no
  confirmed break = no trade.
- Action taken: no action.
- Prediction: stay FLAT; watch daily for a confirmed close beyond €51,000 (down) or €57,500 (up)
  with >=0.5-1% margin. Re-check at next weekly review (~2026-06-22) or sooner on a confirmed break.
- Review (filled in later): _pending_.

### 2026-06-15 — ETHEUR
- Market snapshot: price ~€1,478.72 (last close €1,481 on 2026-06-14). Regime BEAR (200d MA €2,060).
  Donchian: 20d-high €1,815 (entry trigger +0.5% = ~€1,824) -> hold/flat, far below. EMA bear
  (21=€1,556 < 55=€1,713). Two-stage exit channels (Run 19): tight 8d-low €1,364 / wide 10d-low
  €1,364 (n/a, no open position). levels_watch.md triggers: downside €1,400 / upside €1,550 —
  neither broken (price consolidating near support).
- Recommendation/reasoning: FLAT. No confirmed break of either watch level, no Donchian entry
  trigger, EMA and regime both bearish, no both-systems-agree LONG signal. Per the skill, no
  confirmed break = no trade.
- Action taken: no action.
- Prediction: stay FLAT; watch daily for a confirmed close beyond €1,400 (down) or €1,550 (up)
  with >=0.5-1% margin. Re-check at next weekly review (~2026-06-22) or sooner on a confirmed break.
- Review (filled in later): _pending_.
