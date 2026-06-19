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
- Review: BTC 06-15 closed €57,189 — stayed below the €57,500 upside trigger; no break. FLAT correct. 06-16 drifted back toward ~€56,600.

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
- Review: ETH 06-15 closed €1,549 — just under the €1,550 trigger and well below the €1,558 confirm level; the intraday relief-rally spike (high €1,594) faded by the close. FLAT correct.

### 2026-06-15 21:36 — ETHEUR
- Market snapshot: intraday re-check (US–Iran peace-deal relief rally lifted both pairs). ETH price ~€1,567, today's in-progress daily candle high €1,594, poking ~1.2% ABOVE the €1,550 upside trigger — but this is the IN-PROGRESS candle, NOT a confirmed daily close. Regime BEAR (200d MA €2,055), EMA bear (21=€1,557 < 55=€1,708), still far below the Donchian 20d-high €1,780. BTC similar lift to ~€57,300, still ~0.3% BELOW its €57,500 trigger.
- Recommendation/reasoning: FLAT — do not chase. The break is unconfirmed (intraday poke, not a daily close; Run 5 showed these whipsaw), the catalyst is macro relief not ETH-specific, and the structure is still bearish. No both-systems agreement.
- Action taken: no action.
- Prediction: decision is the 00:00 UTC daily close. Confirm = a daily CLOSE ≥ ~€1,558 (ETH) or ~€57,790 (BTC) → CAUTIOUS reduced-size LONG candidate to review (never auto-trade). A fade back under = stay FLAT. The GitHub Actions watcher (watch.py --confirmed) catches the confirmed close at 00:10 UTC.
- Review: Confirmed NO break — ETH 06-15 closed €1,549, below the €1,558 confirm level. The intraday poke faded exactly as flagged; waiting for the daily close avoided a whipsaw (validates the Run 5 break-quality discipline).

### 2026-06-16 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,527. Regime BEAR (200d MA €66,231). EMA 21/55 bear (57,630/60,903). Donchian 20d-high €63,991. Two-stage exit tight8 €53,294/wide10 €52,923. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-16 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,543. Regime BEAR (200d MA €2,050). EMA 21/55 bear (1,555/1,702). Donchian 20d-high €1,741. Two-stage exit tight8 €1,405/wide10 €1,364. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-17 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,014. Regime BEAR (200d MA €66,119). EMA 21/55 bear (57,483/60,729). Donchian 20d-high €63,275. Two-stage exit tight8 €53,294/wide10 €53,294. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-17 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,520. Regime BEAR (200d MA €2,044). EMA 21/55 bear (1,552/1,695). Donchian 20d-high €1,732. Two-stage exit tight8 €1,405/wide10 €1,405. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-18 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€54,889. Regime BEAR (200d MA €66,004). EMA 21/55 bear (57,247/60,520). Donchian 20d-high €63,275. Two-stage exit tight8 €53,294/wide10 €53,294. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-18 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,492. Regime BEAR (200d MA €2,039). EMA 21/55 bear (1,546/1,688). Donchian 20d-high €1,732. Two-stage exit tight8 €1,405/wide10 €1,405. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.
