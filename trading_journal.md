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

### 2026-06-19 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,369. Regime BEAR (200d MA €65,909). EMA 21/55 bear (57,077/60,336). Donchian 20d-high €63,275. Two-stage exit tight8 €54,889/wide10 €53,294. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-19 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,491. Regime BEAR (200d MA €2,034). EMA 21/55 bear (1,541/1,681). Donchian 20d-high €1,732. Two-stage exit tight8 €1,440/wide10 €1,405. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-20 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,020. Regime BEAR (200d MA €65,796). EMA 21/55 bear (56,981/60,182). Donchian 20d-high €63,167. Two-stage exit tight8 €54,889/wide10 €53,294. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-20 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,517. Regime BEAR (200d MA €2,029). EMA 21/55 bear (1,539/1,675). Donchian 20d-high €1,722. Two-stage exit tight8 €1,440/wide10 €1,405. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-21 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,170. Regime BEAR (200d MA €65,672). EMA 21/55 bear (56,816/60,003). Donchian 20d-high €61,319. Two-stage exit tight8 €54,889/wide10 €54,889. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-21 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,488. Regime BEAR (200d MA €2,023). EMA 21/55 bear (1,534/1,668). Donchian 20d-high €1,722. Two-stage exit tight8 €1,453/wide10 €1,440. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-22 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,979. Regime BEAR (200d MA €65,556). EMA 21/55 bear (56,740/59,859). Donchian 20d-high €57,385. Two-stage exit tight8 €54,889/wide10 €54,889. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-22 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,511. Regime BEAR (200d MA €2,017). EMA 21/55 bear (1,532/1,663). Donchian 20d-high €1,599. Two-stage exit tight8 €1,487/wide10 €1,440. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-23 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,061. Regime BEAR (200d MA €65,447). EMA 21/55 bear (56,587/59,688). Donchian 20d-high €57,189. Two-stage exit tight8 €54,889/wide10 €54,889. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-23 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,463. Regime BEAR (200d MA €2,011). EMA 21/55 bear (1,526/1,656). Donchian 20d-high €1,560. Two-stage exit tight8 €1,488/wide10 €1,453. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-24 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€53,720. Regime BEAR (200d MA €65,332). EMA 21/55 bear (56,327/59,475). Donchian 20d-high €57,189. Two-stage exit tight8 €54,889/wide10 €54,889. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-24 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,426. Regime BEAR (200d MA €2,005). EMA 21/55 bear (1,517/1,647). Donchian 20d-high €1,549. Two-stage exit tight8 €1,463/wide10 €1,463. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-25 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€52,554. Regime BEAR (200d MA €65,206). EMA 21/55 bear (55,984/59,228). Donchian 20d-high €57,189. Two-stage exit tight8 €53,720/wide10 €53,720. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-25 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,377. Regime BEAR (200d MA €1,999). EMA 21/55 bear (1,504/1,638). Donchian 20d-high €1,549. Two-stage exit tight8 €1,426/wide10 €1,426. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: SHORT candidate — confirmed downside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-26 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€52,726. Regime BEAR (200d MA €65,080). EMA 21/55 bear (55,688/58,996). Donchian 20d-high €57,189. Two-stage exit tight8 €52,554/wide10 €52,554. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-26 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,385. Regime BEAR (200d MA €1,993). EMA 21/55 bear (1,493/1,629). Donchian 20d-high €1,549. Two-stage exit tight8 €1,377/wide10 €1,377. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: SHORT candidate — confirmed downside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-27 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€52,658. Regime BEAR (200d MA €64,945). EMA 21/55 bear (55,412/58,769). Donchian 20d-high €57,189. Two-stage exit tight8 €52,554/wide10 €52,554. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-27 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,381. Regime BEAR (200d MA €1,985). EMA 21/55 bear (1,483/1,620). Donchian 20d-high €1,549. Two-stage exit tight8 €1,377/wide10 €1,377. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: SHORT candidate — confirmed downside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-28 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€52,248. Regime BEAR (200d MA €64,813). EMA 21/55 bear (55,124/58,536). Donchian 20d-high €57,189. Two-stage exit tight8 €52,554/wide10 €52,554. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-28 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,379. Regime BEAR (200d MA €1,978). EMA 21/55 bear (1,474/1,611). Donchian 20d-high €1,549. Two-stage exit tight8 €1,377/wide10 €1,377. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: SHORT candidate — confirmed downside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-29 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€52,694. Regime BEAR (200d MA €64,683). EMA 21/55 bear (54,903/58,328). Donchian 20d-high €57,189. Two-stage exit tight8 €52,248/wide10 €52,248. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-29 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,410. Regime BEAR (200d MA €1,971). EMA 21/55 bear (1,468/1,604). Donchian 20d-high €1,549. Two-stage exit tight8 €1,377/wide10 €1,377. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-30 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€51,298. Regime BEAR (200d MA €64,554). EMA 21/55 bear (54,576/58,077). Donchian 20d-high €57,189. Two-stage exit tight8 €52,248/wide10 €52,248. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-06-30 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,376. Regime BEAR (200d MA €1,965). EMA 21/55 bear (1,459/1,596). Donchian 20d-high €1,549. Two-stage exit tight8 €1,377/wide10 €1,377. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: SHORT candidate — confirmed downside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-01 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€52,702. Regime BEAR (200d MA €64,433). EMA 21/55 bear (54,405/57,885). Donchian 20d-high €57,189. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-01 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,413. Regime BEAR (200d MA €1,959). EMA 21/55 bear (1,455/1,589). Donchian 20d-high €1,549. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-02 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€53,832. Regime BEAR (200d MA €64,327). EMA 21/55 bear (54,353/57,740). Donchian 20d-high €57,189. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-02 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,487. Regime BEAR (200d MA €1,953). EMA 21/55 bear (1,458/1,586). Donchian 20d-high €1,549. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-03 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€54,713. Regime BEAR (200d MA €64,232). EMA 21/55 bear (54,386/57,632). Donchian 20d-high €57,189. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-03 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,537. Regime BEAR (200d MA €1,948). EMA 21/55 bear (1,465/1,584). Donchian 20d-high €1,549. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-04 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,206. Regime BEAR (200d MA €64,135). EMA 21/55 bear (54,460/57,545). Donchian 20d-high €57,189. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-04 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,557. Regime BEAR (200d MA €1,943). EMA 21/55 bear (1,474/1,583). Donchian 20d-high €1,549. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-05 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,603. Regime BEAR (200d MA €64,046). EMA 21/55 bear (54,564/57,476). Donchian 20d-high €57,189. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-05 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,560. Regime BEAR (200d MA €1,939). EMA 21/55 bear (1,482/1,582). Donchian 20d-high €1,557. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-06 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,946. Regime BEAR (200d MA €63,961). EMA 21/55 bear (54,690/57,421). Donchian 20d-high €56,527. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-06 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,571. Regime BEAR (200d MA €1,935). EMA 21/55 bear (1,490/1,582). Donchian 20d-high €1,560. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-07 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,519. Regime BEAR (200d MA €63,862). EMA 21/55 bear (54,765/57,353). Donchian 20d-high €56,020. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-07 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,552. Regime BEAR (200d MA €1,930). EMA 21/55 bear (1,495/1,581). Donchian 20d-high €1,571. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-08 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€54,524. Regime BEAR (200d MA €63,758). EMA 21/55 bear (54,743/57,252). Donchian 20d-high €56,020. Two-stage exit tight8 €51,298/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-08 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,526. Regime BEAR (200d MA €1,925). EMA 21/55 bear (1,498/1,579). Donchian 20d-high €1,571. Two-stage exit tight8 €1,376/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-09 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,295. Regime BEAR (200d MA €63,656). EMA 21/55 bear (54,794/57,182). Donchian 20d-high €56,020. Two-stage exit tight8 €52,702/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-09 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,526. Regime BEAR (200d MA €1,920). EMA 21/55 bear (1,501/1,577). Donchian 20d-high €1,571. Two-stage exit tight8 €1,413/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-10 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,198. Regime BEAR (200d MA €63,560). EMA 21/55 bear (54,921/57,147). Donchian 20d-high €56,020. Two-stage exit tight8 €53,832/wide10 €51,298. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-10 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,574. Regime BEAR (200d MA €1,915). EMA 21/55 bear (1,507/1,577). Donchian 20d-high €1,571. Two-stage exit tight8 €1,487/wide10 €1,376. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-11 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,900. Regime BEAR (200d MA €63,469). EMA 21/55 bear (55,010/57,103). Donchian 20d-high €56,198. Two-stage exit tight8 €54,524/wide10 €52,702. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-11 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,566. Regime BEAR (200d MA €1,910). EMA 21/55 bear (1,513/1,576). Donchian 20d-high €1,574. Two-stage exit tight8 €1,526/wide10 €1,413. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-12 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,902. Regime BEAR (200d MA €63,377). EMA 21/55 bear (55,091/57,060). Donchian 20d-high €56,198. Two-stage exit tight8 €54,524/wide10 €53,832. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-12 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,584. Regime BEAR (200d MA €1,905). EMA 21/55 bear (1,519/1,577). Donchian 20d-high €1,574. Two-stage exit tight8 €1,526/wide10 €1,487. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-13 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€54,708. Regime BEAR (200d MA €63,280). EMA 21/55 bear (55,056/56,976). Donchian 20d-high €56,198. Two-stage exit tight8 €54,524/wide10 €54,524. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-13 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,559. Regime BEAR (200d MA €1,901). EMA 21/55 bear (1,523/1,576). Donchian 20d-high €1,584. Two-stage exit tight8 €1,526/wide10 €1,526. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-14 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,885. Regime BEAR (200d MA €63,194). EMA 21/55 bear (55,223/56,972). Donchian 20d-high €56,198. Two-stage exit tight8 €54,524/wide10 €54,524. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-14 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,655. Regime BEAR (200d MA €1,897). EMA 21/55 bear (1,535/1,579). Donchian 20d-high €1,584. Two-stage exit tight8 €1,526/wide10 €1,526. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-15 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,438. Regime BEAR (200d MA €63,103). EMA 21/55 bear (55,333/56,953). Donchian 20d-high €56,885. Two-stage exit tight8 €54,524/wide10 €54,524. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-15 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,672. Regime BEAR (200d MA €1,893). EMA 21/55 bear (1,547/1,582). Donchian 20d-high €1,655. Two-stage exit tight8 €1,526/wide10 €1,526. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-16 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,748. Regime BEAR (200d MA €63,009). EMA 21/55 bear (55,371/56,910). Donchian 20d-high €56,885. Two-stage exit tight8 €54,524/wide10 €54,524. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-16 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,628. Regime BEAR (200d MA €1,888). EMA 21/55 bear (1,555/1,584). Donchian 20d-high €1,672. Two-stage exit tight8 €1,526/wide10 €1,526. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-17 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€55,881. Regime BEAR (200d MA €62,919). EMA 21/55 bear (55,417/56,874). Donchian 20d-high €56,885. Two-stage exit tight8 €54,708/wide10 €54,524. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-17 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,610. Regime BEAR (200d MA €1,884). EMA 21/55 bear (1,560/1,585). Donchian 20d-high €1,672. Two-stage exit tight8 €1,526/wide10 €1,526. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-18 — BTCEUR
- Market snapshot: automated daily watch (confirmed close). price ~€56,671. Regime BEAR (200d MA €62,826). EMA 21/55 bear (55,531/56,866). Donchian 20d-high €56,885. Two-stage exit tight8 €54,708/wide10 €54,524. Triggers: down €51,000, up €57,500.
- Recommendation/reasoning: FLAT — no confirmed break. Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.

### 2026-07-18 — ETHEUR
- Market snapshot: automated daily watch (confirmed close). price ~€1,628. Regime BEAR (200d MA €1,879). EMA 21/55 bear (1,566/1,586). Donchian 20d-high €1,672. Two-stage exit tight8 €1,559/wide10 €1,526. Triggers: down €1,400, up €1,550.
- Recommendation/reasoning: LONG candidate — confirmed upside break (review, never auto-trade). Mechanical daily watch (GitHub Actions); the human/Claude layer makes the actual call on a confirmed break.
- Action taken: no action (mechanical watch — never trades).
- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.
- Review (filled in later): _pending_.
