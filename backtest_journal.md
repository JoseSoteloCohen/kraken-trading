# Backtest Journal (Walk-Forward, Hypothetical)

This is a separate, analytical exercise using historical OHLC data — NOT connected to the live
paper trading account (which fills at real-time live prices). Purpose: build a track record of
Claude's directional calls vs. actual outcomes, to surface biases/patterns over time.

## Methodology

- Pull daily OHLC for a pair via `kraken ohlc <PAIR> --interval 1440 --since <ts>`
- Walk through chronologically in weekly chunks
- At each decision point, make a call (LONG/SHORT/FLAT) based only on data up to that point,
  with reasoning written before considering what happens next
- Reveal next week's actual close, grade hypothetical P&L on $10,000 notional, 0.26% fee each way (0.52% round trip)

**Caveat**: Because all historical data is fetched in one request, Claude has the full series in
context when making "earlier" calls. Discipline (reasoning only from trailing data, written before
revealing outcomes) approximates blindness but isn't perfect. For stricter rigor, fetch data
incrementally across separate steps so future candles aren't in context yet.

## Run 1: BTC/USD, daily, 2026-05-04 to 2026-06-14

| # | Decision date | Close at decision | Call | Reasoning | Next week close | Change | P&L ($10k, incl. fees) |
|---|---|---|---|---|---|---|---|
| 1 | 2026-05-10 | 82,171.8 | LONG | Grinding to new highs, breakout momentum | 77,410.0 | -5.80% | -$631.50 |
| 2 | 2026-05-17 | 77,410.0 | SHORT | Sharp reversal, downtrend confirmed | 76,984.9 | -0.55% | +$2.90 |
| 3 | 2026-05-24 | 76,984.9 | FLAT | Choppy consolidation, mixed signals | 73,570.0 | -4.43% | $0 (missed ~+$428 short) |
| 4 | 2026-05-31 | 73,570.0 | SHORT | Range broke down, downtrend accelerating | 63,307.6 | -13.95% | +$1,343.00 |
| 5 | 2026-06-07 | 63,307.6 | LONG | Oversold bounce after capitulation | 63,790.6 | +0.76% | +$24.30 |

**Net: +$738.70 (+7.39%) over 5 weeks**

### Observations / biases to watch
- Got faked out by a breakout near a local high (#1) — be more skeptical of "new highs = momentum continues" near extended moves.
- Too cautious during consolidation after a strong move (#3) — missed a continuation trade.
- Best result came from following a *confirmed* trend break (#4), not from anticipating reversals.
- Mean-reversion/bounce call after capitulation (#5) was directionally right but barely cleared fees — size/conviction should reflect that these are low-edge trades.

## Run 2: BTC/USD, weekly, 2026-01-01 to 2026-06-14 (YTD, 23 decisions)

| # | Week of | Call | Reasoning | Next week actual | P&L ($10k, incl. fees) |
|---|---|---|---|---|---|
| 1 | 01/01-07 | LONG | Fresh momentum, new-year up week | +6.20% | +$568 |
| 2 | 01/08-14 | LONG | 2 strong up weeks, momentum | -7.80% | -$832 |
| 3 | 01/15-21 | SHORT | Sharp reversal after extended run | -0.24% | -$28 |
| 4 | 01/22-28 | SHORT | Downtrend confirmed (2 down wks) | -18.11% | +$1,759 |
| 5 | 01/29-02/04 | LONG | 3 down weeks, deeply oversold, bounce bet | -8.16% | -$868 |
| 6 | 02/05-11 | SHORT | Bounce failed, trend still down | -0.92% | +$40 |
| 7 | 02/12-18 | LONG | Downtrend decelerating, bottoming | +2.34% | +$182 |
| 8 | 02/19-25 | LONG | First up week, trend change confirmed | +6.92% | +$640 |
| 9 | 02/26-03/04 | LONG | 2 up weeks, momentum | -3.42% | -$394 |
| 10 | 03/05-11 | LONG | Pullback in uptrend, buy dip | +1.52% | +$100 |
| 11 | 03/12-18 | LONG | Uptrend resumed | +0.05% | -$47 |
| 12 | 03/19-25 | FLAT | Momentum stalling, unclear | -4.49% | $0 (missed +$397) |
| 13 | 03/26-04/01 | SHORT | Sharp down week, reversal signal | +4.42% | -$494 |
| 14 | 04/02-08 | LONG | V-reversal, momentum resumed | +5.23% | +$471 |
| 15 | 04/09-15 | LONG | 2 strong up weeks, continuation | +4.54% | +$402 |
| 16 | 04/16-22 | FLAT | 3 up weeks (+14.9%), overextended | -3.14% | $0 (missed +$262) |
| 17 | 04/23-29 | LONG | Pullback in uptrend, buy dip | +7.51% | +$699 |
| 18 | 04/30-05/06 | FLAT | +7.5% week, very extended | -2.64% | $0 (avoided -$316) |
| 19 | 05/07-13 | SHORT | Pullback after extended run, topping | -2.29% | +$177 |
| 20 | 05/14-20 | SHORT | 2 down weeks, downtrend forming | -4.05% | +$353 |
| 21 | 05/21-27 | SHORT | 3 down weeks, accelerating | -13.86% | +$1,334 |
| 22 | 05/28-06/03 | SHORT | Huge drop, don't call bottom early | -4.02% | +$350 |
| 23 | 06/04-10 | LONG | Decelerating downtrend, bottoming | +3.82% (partial wk) | +$330 |

**Net: +$4,742 on $10k per trade (≈+47%), 14W / 6L / 3 flat (70% hit rate on directional calls)**

### Critical caveat — likely hindsight-contaminated
The entire 6-month series was in context for this run. Several calls (#6, #18, #22, #23) explicitly
referenced "lessons" from elsewhere in the *same already-visible* dataset — that's a red flag for
hindsight bias, not genuine forward reasoning. A 70% hit rate / +47% over 6 months is an outlier
result that should NOT be trusted as representative. Treat this run as a demonstration of what
"pattern-following with flat-at-extremes" looks like when reverse-engineered against known data,
not as evidence of real predictive skill.

## Run 3: BTC/USD, weekly, 2025-09-15 to 2025-11-23 — STRICTLY BLIND (9 decisions)

Methodology: full 273-day dataset fetched once into `/tmp/btc_blind.json` (in WSL) without viewing
prices. A helper script (`reveal_week.py`) revealed one week's aggregated OHLC at a time via
separate tool calls — each call/decision was recorded *before* the next week was revealed, so
future candles were genuinely not in context.

| # | Week | Call | Reasoning | Actual change | P&L ($10k, incl. fees) |
|---|---|---|---|---|---|
| 1 | 09/15-21 | FLAT | Flat/choppy week (-0.08%), no signal | -2.75% | $0 (missed +$223) |
| 2 | 09/22-28 | SHORT | Broke down below week 1's range low | +10.18% | -$1,070 |
| 3 | 09/29-10/05 | LONG | V-reversal, broke to new highs | -6.81% | -$733 |
| 4 | 10/06-12 | LONG | Bounced ~15% off 100k support intraweek | -5.61% | -$613 |
| 5 | 10/13-19 | SHORT | Bounce failed, broader downtrend reasserting | +5.37% | -$589 |
| 6 | 10/20-26 | FLAT | 5 weeks of whipsaw, no tradeable trend | -3.42% | $0 (missed +$290) |
| 7 | 10/27-11/02 | FLAT | Still no trend after 7 weeks | -5.30% | $0 (missed +$478) |
| 8 | 11/03-09 | SHORT | Broke below 100k for first time, breakdown | -10.06% | +$954 |
| 9 | 11/10-16 | SHORT | Breakdown confirmed, downtrend accelerating | -7.87% | +$735 |

**Net: -$1,316 (-13.2%), 2W / 4L / 3 flat (33% hit rate on directional calls)**

### Comparison to Run 2 (hindsight-contaminated, same methodology otherwise)
Run 2: +47%, 70% hit rate. Run 3 (blind): -13.2%, 33% hit rate. The gap is enormous — confirms
Run 2 was not representative. Run 3 is the more trustworthy baseline for what "trend/momentum +
flat-on-uncertainty" reasoning actually achieves without hindsight help.

### Observations
- **Calling reversals/bounces is a clear weak spot**: decisions 2-5 were all attempts to call a
  turn (breakdown reversal, V-reversal, bounce-off-support, bounce-failure) and ALL FOUR were
  wrong, in a market that was genuinely whipsawing. This matches the pattern flagged in Run 1 (#1)
  and Run 2 (#5, #13).
- **Confirmed breakdowns/breakouts of key levels are the strongest signal**: decisions 8-9 (short
  after the 100k level broke) were the only wins, and the biggest wins by magnitude.
- **FLAT during genuine chop was the right call** (decisions 1, 6, 7) — zero loss vs. likely losses
  if forced into a direction. The cost was missed gains, not realized losses.
- **Takeaway for live trading**: prefer waiting for a confirmed break of a meaningful level/range
  over trying to call tops/bottoms or bounces. When the market is choppy with no clear structure,
  FLAT is a legitimate (and apparently correct) choice, not just indecision.

## Run 4: BTC/USD + ETH/USD, weekly, 2025-02-15 to 2025-05-09 — STRICTLY BLIND (11 decisions each)

Methodology: same as Run 3 (one week revealed at a time via `reveal_week2.py`, call recorded
before next week revealed). This run explicitly applied the **Run 3 lens**: trade confirmed
breaks of levels/ranges, avoid calling reversals/bounces, go FLAT during chop.

### BTC/USD
| # | Week of | Call | Reasoning | Actual | P&L |
|---|---|---|---|---|---|
| 1 | 02/22-28 | FLAT | Mild down week inside range | -12.27% | $0 (missed short) |
| 2 | 03/01-07 | SHORT | Confirmed breakdown below range low | +2.91% | -$343 |
| 3 | 03/08-14 | FLAT | Bounce, higher low, chop | -3.19% | $0 |
| 4 | 03/15-21 | SHORT | New lower low, downtrend re-confirmed | +0.04% | -$56 |
| 5 | 03/22-28 | FLAT | Dead flat, basing | +0.40% | $0 |
| 6 | 03/29-04/04 | FLAT | Range-bound | -0.63% | $0 |
| 7 | 04/05-11 | FLAT | 4th week of chop | -0.50% | $0 |
| 8 | 04/12-18 | FLAT | Intraweek spike down, closed back in range | +1.26% | $0 |
| 9 | 04/19-25 | FLAT | 6 weeks chop, no break | +12.13% | $0 (missed breakout) |
| 10 | 04/26-05/02 | LONG | Confirmed breakout above range | +2.33% | +$181 |
| 11 | 05/03-09 | LONG | Continuation, new highs | +6.25% | +$573 |

**BTC net: +$355 | 2W / 2L / 7 flat**

### ETH/USD
| # | Week of | Call | Reasoning | Actual | P&L |
|---|---|---|---|---|---|
| 1 | 02/22-28 | FLAT | Mild down week, no break | -15.93% | $0 (missed short) |
| 2 | 03/01-07 | SHORT | Confirmed breakdown below range low | -4.33% | +$381 |
| 3 | 03/08-14 | SHORT | New low, downtrend intact | -10.73% | +$1,021 |
| 4 | 03/15-21 | SHORT | (held short) | +2.84% | -$336 |
| 5 | 03/22-28 | FLAT | Higher low, possible reversal | -3.50% | $0 |
| 6 | 03/29-04/04 | FLAT | Held prior low, no new low | -4.26% | $0 |
| 7 | 04/05-11 | FLAT | Testing 1750 support, not broken | -13.75% | $0 (missed short) |
| 8 | 04/12-18 | SHORT | Confirmed break below 1750 | +1.42% | -$194 |
| 9 | 04/19-25 | FLAT | Bounce, higher low, possible reversal | +12.48% | $0 (missed breakout) |
| 10 | 04/26-05/02 | LONG | Confirmed breakout above consolidation | +3.16% | +$264 |
| 11 | 05/03-09 | LONG | Continuation | +27.28% | +$2,676 |

**ETH net: +$3,812 | 4W / 2L / 5 flat**

### Combined result
**Net: +$4,167 across both | 10 directional calls, 6W / 4L (60% hit rate) | 12 flats**

### Observations — important nuance vs. Run 3
- This blind run came out **positive**, unlike Run 3 (-13%). The difference is regime: this period
  (Feb-May 2025) had two clean trends — a sharp crash then a strong breakout — with well-defined
  confirmed breaks. The lens is built for exactly this. Run 3's period was choppier and the lens lost.
  **Conclusion: the "confirmed-break" strategy is regime-dependent — it wins in trending markets and
  bleeds/breaks even in choppy ones.**
- **P&L is highly concentrated**: ETH's single +27.28% week (#11) = +$2,676, and ETH #3 = +$1,021.
  Those two weeks are ~89% of total profit. Strip the one lucky +27% week and combined net drops to
  ~$1,491. A couple of trend weeks dominate everything — small sample, high variance.
- **The "wait for confirmation" rule reliably misses the first leg of every move** — it sat out the
  -12%/-16% crash week (#1) and the +12% breakout week (#9) on both assets. It captures the
  *continuation*, never the initial break. That's the inherent cost of waiting for confirmation.
- **Reversal-calling weakness reconfirmed**: every SHORT that tried to extend into a turn (BTC #2,
  #4; ETH #4, #8) lost. The winning shorts (ETH #2, #3) were fresh confirmed breakdowns, not
  reversal bets.
- **FLAT discipline held up**: 12 flats, zero realized losses from them; cost was opportunity only.

### Overall takeaways across all 4 runs (for live trading)
1. Hindsight inflates results massively (Run 2 +47% vs blind runs) — only trust blind/forward calls.
2. Edge, if any, is in trading **confirmed breaks of ranges/levels**, not reversals or bounces.
3. Strategy is **regime-dependent**: profitable in trending periods, negative in choppy ones. No
   reliable way known yet to tell which regime you're in *ahead* of time.
4. Results are **high-variance and concentrated** — a couple of weeks make the year. Position sizing
   and risk control matter more than hit rate.
5. Net honest expectation: this is **not a proven edge** — 2 blind runs, one +, one −, small samples.
   Treat live paper trading as continued data collection, not as a validated money-making system.

## Run 5: BTC/EUR, DAILY blind — testing the "weekly default, daily-watch when FLAT" hybrid

Account now **€1,000 EUR** (user's real starting capital). Period 2025-06-01 to 2025-07-13 (~6
weeks), revealed ONE DAY at a time via `reveal_day.py` (blind). Tested the user's hybrid: default
weekly, but when FLAT, watch daily for a confirmed break to enter mid-week rather than waiting.
Rule: FLAT → LONG on daily close above prior-10-day high / SHORT below prior-10-day low; exit on
close back inside the broken level. Fees 0.52% round trip.

**Days 1-10:** warm-up (range 87,784–96,725). **Days 11-20:** chop, FLAT.
**Trade 1 — SHORT** (day 21 @ 88,704): marginal break (€47 below the 10-day low). Whipsawed —
day 23 closed back inside (+3.53%), break invalidated. Exit @ 90,921 = **−€30.20**.
**Days 24-38:** more chop, FLAT (~15 days).
**Trade 2 — LONG** (day 39 @ 94,855): clean break above 10-day high (93,900). Strong continuation
to >€100k. Exit @ 101,590 = **+€65.80**.

**Net: +€35.60 (+3.56%) over 6 weeks | 2 trades, ~31 FLAT days, 1W / 1L**

### Does the hybrid actually add value? (the key question)
**Yes, conditionally.** The breakout (Trade 2) started **mid-week** (Wed July 9). A pure-weekly
trader re-deciding only on the weekly boundary would likely have been FLAT at the prior weekend
(July 6, price ~92,720, still in chop) and not re-entered until the NEXT weekend (July 13 @
101,590) — **missing almost the entire +7% move or buying the top.** The daily-watch-when-flat
caught it 4 days early at 94,855. That is exactly the "don't waste the flat week" benefit the user
wanted, and it was real here.

**But it has a cost:** the daily watching also produced the whipsaw SHORT (−€30) that a pure-weekly
trader would NOT have taken (the marginal June 21 daily poke wouldn't register on a weekly close).
So the hybrid traded €30 of whipsaw losses to capture a breakout entry worth €66. Net positive
*this time*, but the whipsaw is the recurring tax.

### The fix (important)
The losing trade came from a **marginal €47 break** — exactly the noise a daily timeframe adds.
A **break-quality filter** would have skipped it while keeping the good breakout:
- Require the close to clear the level by a meaningful margin (e.g. ≥0.5–1%, not €47), AND/OR
- Require the expected follow-through to comfortably exceed the 0.52% fee, AND/OR
- Only act on daily breaks in the *direction* that doesn't fight a higher-timeframe range.

### Verdict for live trading
**Adopt the hybrid** (weekly default; when FLAT, watch daily for an entry) — it demonstrably
rescued an otherwise-missed breakout. **But enforce a break-quality filter** so marginal daily
pokes don't generate whipsaw trades. When already in a position, stay weekly (don't micro-manage).
On €1,000 with 0.52% round-trip fees, every avoided whipsaw matters proportionally as much as on
any size — discipline on entry quality is the whole game.

## Run 6: MECHANICAL backtest — Donchian breakout vs. buy-and-hold (the rigorous test)

Built `backtester.py`: mechanized the "trade confirmed breaks" rule into a Donchian-channel
trend-following system (enter on close above N-day high by a margin; exit on close below M-day low —
a trailing stop that lets winners run / cuts losers). Long-only, no leverage. Benchmarked against
buy-and-hold and cash. ~2 years daily data (2024-06-24 → 2026-06-14, 721 candles each).

### Full-period results, default params (entry=20, exit=10, margin=0.5%)
| Asset | Strategy | Buy & hold | Edge vs hold | Max DD (strat / hold) | Win rate | Sharpe |
|---|---|---|---|---|---|---|
| BTC | **+30.0%** | +0.0% | **+30%** | −28% / −50% | 38% | 0.80 |
| ETH | **−25.7%** | −52.6% | **+27%** | −56% / −67% | 31% | −0.11 |

Win/loss profile (both): avg win ~+16%, avg loss ~−5 to −8% → textbook trend-following (lose small
often, win big rarely). Time in market only ~30–37% (in cash the rest, avoiding chop).

### Walk-forward (tune on first 60%, report SAME params on untouched last 40%) — THE HONEST TEST
| Asset | In-sample edge vs hold | OUT-OF-SAMPLE edge vs hold | OOS abs return | OOS Sharpe |
|---|---|---|---|---|
| BTC | −9% (best-Sharpe params) | **+19.8%** | −20.0% | −1.84 |
| ETH | +92% | **+24.9%** | −35.6% | −1.45 |

Vol-targeting (size to ~2% daily vol) gave a small risk improvement: BTC Sharpe 0.80→0.87, ETH DD
−56%→−40%. Marginal, mostly risk not return.

### THE HONEST CONCLUSION (most important finding of the whole project)
1. **There is no demonstrated alpha.** Out-of-sample, the strategy LOST money in absolute terms on
   both assets (negative Sharpe). It does not reliably make money. Do not expect it to.
2. **What IS robust and real: drawdown reduction.** Across every cut — full-period, in-sample,
   out-of-sample, both assets — the trend-following exit consistently **beat buy-and-hold by ~+20 to
   +31%** by getting out of crashes. It roughly **halved max drawdown** (e.g. BTC −28% vs −50%). This
   is the genuine, repeatable property of trend-following: it is a *risk-reduction* tool, not an
   alpha engine.
3. **Parameter optimization OVERFIT and did not help.** The best in-sample-Sharpe params for BTC
   actually had a *negative* edge in-sample and worse out-of-sample. Lesson: use robust defaults
   (entry=20/exit=10), do NOT tune parameters on this little data — it fools you.
4. **The reframe for "better results":** the achievable goal is NOT "predict direction for profit"
   (not demonstrated, probably not attainable at this scale). It is **"participate in crypto with far
   smaller drawdowns"** via systematic trend-following + risk control. Honest alternatives that may do
   as well with less effort: systematic DCA, or hold-with-a-trailing-stop. The discretionary
   weekly/news layer's real job is **risk management, not alpha**.

### Validated defaults (use these; don't re-optimize)
entry_lookback=20, exit_lookback=10, entry_margin=0.5%, optional vol-target ~2% daily, no leverage.

## Run 7: Stop-loss / take-profit brackets vs. trailing stop (`backtester.py brackets`)

Tested the idea of attaching a fixed stop-loss + take-profit to every trade, with cash availability
as the cue to evaluate a new entry (NOT to trade indiscriminately — entry still requires a confirmed
breakout). 2 years daily, both assets.

### Results (return / edge-vs-hold)
| Config | BTC | ETH |
|---|---|---|
| **Trailing-stop baseline (e20/x10)** | **+30.0% / +30%** | −25.7% / **+27%** |
| breakout + SL 8% / TP 16% | −15.6% / −16% | −16.7% / +36% |
| breakout + SL 8% / TP 30% | −2.5% / −3% | −11.6% / +41% |
| breakout + SL 5% / TP 10% | −23.9% / −24% | +3.1% / +56% |
| ALWAYS-in + brackets (no entry signal) | −30.1% / −30% | **−78.7% / −26%** |

### Findings
1. **Fixed take-profit caps the winners and breaks the strategy on BTC** — every TP setting turned
   the +30% trailing result negative. The rare big trend is the edge; truncating it is fatal. Confirms
   the prior concern with data.
2. **"Always in" (redeploy with no entry signal) is catastrophic** (−30% BTC, −79% ETH). Brackets
   manage exits; they do NOT create an entry edge. An entry signal is non-negotiable.
3. **The one good bracket result (ETH 5%/10%) is noise** — inconsistent across SL/TP levels and
   doesn't transfer to BTC. No single bracket setting was robust across both assets. The trailing stop
   beat buy-and-hold on BOTH — that's a real property, not a fluke.

### Validated rules (adopted)
- **Exit = trailing Donchian stop. This IS the stop-loss** — a dynamic one that ratchets up to protect
  gains without ever capping upside. Do not add a separate fixed stop.
- **No fixed take-profit.** Ever. It mathematically kills trend-following by truncating winners.
- **Cash freeing up = the cue to EVALUATE a new entry, not to trade.** Only enter on a confirmed
  breakout (with the break-quality margin). Never "always in."

## Run 8: A/B — discretionary human+news vs. mechanical rule (`backtester.py abtest`)

Compared the blind discretionary runs (3,4,5) against what the mechanical Donchian rule returned over
the exact same windows (same data, same dates).

| Window | Discretionary (blind) | Mechanical | Buy & hold | Winner |
|---|---|---|---|---|
| Run 3 BTC Sep–Nov'25 | −13.2% | −9.0% | −23.0% | Mechanical |
| Run 4 BTC Feb–May'25 | +3.6% | +11.4% | −1.7% | Mechanical |
| Run 4 ETH Feb–May'25 | +38.1% | +22.3% | −18.9% | Discretionary* |
| Run 5 BTC Jun–Jul'25 | +3.6% | +6.9% | +9.1% | Mechanical |

\*The one discretionary win was driven almost entirely by a single lucky +27% ETH week (flagged as
high-variance at the time). Strip it and the mechanical rule sweeps.

### Conclusion: the human+news layer does NOT add measurable value
Mechanical matched/beat discretionary in 3 of 4 windows — despite the comparison being *stacked for
discretionary*: (a) discretionary could go SHORT to profit in down moves while the mechanical rule is
long-only, and still lost; (b) the "blind" discretionary runs had the full data file in context, so
they're if anything flattered by residual hindsight. Beating that handicap-favored opponent makes the
mechanical result stronger. Net: discretionary judgment + news slightly *underperformed* a simple
systematic rule, with more effort and more failure modes.

**Caveat:** 4 windows is a small sample — strong directional evidence, not proof.

### Adopted implications
- **Mechanical system drives entries/exits** (that's where the measured drawdown-reduction edge is).
- **Human+news layer demoted to RISK OVERSIGHT only** — a veto for abnormal events (depeg, exchange
  failure, known macro catalyst) and position sizing, NOT a source of entry signals.
- Bonus: a mostly self-running system fits the full-time-job constraint better than discretionary
  chart-watching.

## Run 9: EMA crossover system — tested vs Donchian, adopted as a PARALLEL system

Tested the proposed EMA(21/55)+RSI>50 crossover system (`backtester.py compare`). 2yr daily.
| System | BTC return/Sharpe | ETH return/Sharpe | Trades |
|---|---|---|---|
| Donchian (ours) | +30.0% / 0.80 | −25.7% / −0.11 | 13–16 |
| EMA 21/55 +RSI>50 | +37.6% / 0.79 | +19.7% / 0.47 | 5–6 |

Findings: (1) EMA cross is a **legit peer** — comparable on BTC, better on ETH this sample. (2) The
**RSI>50 filter is inert** — identical results with/without it (RSI is ~always >50 at an up-cross;
redundant). (3) The proposed **"exit on close below 55 EMA" actively hurt** (+37.6%→−10.9% BTC). (4)
Only **5–6 trades** = too few to claim superiority; can't walk-forward validate. (5) Deeper point:
EMA-cross and Donchian are the **same bet** (trend-following) — both only reduce drawdown, neither
generates alpha; choosing between them is marginal.
**Adopted:** run BOTH in parallel (`backtester.py signals <PAIR>`). When Donchian + EMA + regime all
agree, that's a higher-conviction signal. Do NOT adopt the RSI filter or the close-below-55 exit.

## Run 10: Market cycles + `is_bear_market` regime filter

**Cycle analysis (12.7yr weekly BTC, 2013–2026):** major tops 2013-11 → 2017-12 → 2021-Q4 are ~4yr
apart; major bottoms 2015-01 → 2019-01 → 2022-11 also ~4yr apart — the halving rhythm is visibly
real. BUT: only **3 clean cycles** (can't confirm a law), big **intermediate swings** don't fit the
grid (2019 rally, 2020 COVID crash, 2024–25), amplitude **shrinking** each cycle. **Conclusion:
calendar/date-based cycle timing is NOT tradeable** (n=3, fragile, being off by months is fatal). Do
not encode "it's year X so expect Y." Use **price-based regime** instead — it captures "are we in a
bear" adaptively without predicting dates.

**Regime filter test (200d-MA: only long when price > 200d MA):**
| | No filter | +200d | +100d |
|---|---|---|---|
| BTC | +30.0% | −16.2% | +25.4% |
| ETH | −25.7% | −1.8% | −12.6% |
Mixed: **helped ETH** (sustained bear — stayed out) but **hurt BTC** (chopped around the MA →
whipsaw + missed trades). Highly sensitive to MA length (asset/param-fragile).
**Adopted:** use the regime as **CONTEXT** (bull/bear awareness for caution & sizing), NOT as a hard
mechanical entry gate. Current reading (2026-06-14): BTC and ETH both **BEAR** (price < 200d MA) —
all systems flat. Notably the price-regime independently reached the "we're past the ~2025 peak"
conclusion the 4yr-cycle narrative was reaching for, but adaptively.

## Run 11: New frameworks — mean-reversion, Adaptive-Trend (ER-gated), and ENSEMBLES

Tested two genuinely-different frameworks (not more trend variants) + ensembles (`backtester.py
frameworks`). 2yr daily. Goal: improve RISK-ADJUSTED return via diversification, not raw return.

| System | BTC ret/Sharpe/DD | ETH ret/Sharpe/DD |
|---|---|---|
| Donchian (trend) | +30% / 0.80 / −28% | −26% / −0.11 / −56% |
| EMA 21/55 (trend) | +38% / 0.79 / −31% | +20% / 0.47 / −36% |
| Mean-reversion (NEW) | −9% / 0.11 / −44% | −35% / −0.14 / −54% |
| Adaptive-Trend ER-gated (NEW) | +18% / 0.61 / −28% | −20% / −0.11 / −48% |
| **Ensemble Don+EMA+MeanRev** | **+29% / 0.78 / −24%** | **−3% / 0.09 / −43%** |

**Correlations (the key metric):** Donchian–EMA +0.70/+0.56 (same bet); **Donchian–MeanRev −0.00/−0.00
(perfectly uncorrelated!)**; Donchian–Adaptive +0.89/+0.85 (just a timid Donchian).

### Findings
1. **Adaptive-Trend (the ER-gate idea) FAILED** — underperformed plain Donchian on return and is
   0.85+ correlated with it (not a diversifier, just more conservative). Clever idea lost to the
   simple baseline — the session's recurring lesson, applied to a self-proposed idea. Not adopted.
2. **Mean-reversion alone is bad BUT zero-correlated with trend** — the holy grail of diversification.
   It pays off when trend-following bleeds.
3. **The ENSEMBLE (trend + mean-reversion) genuinely improves risk-adjusted return / cuts drawdown** —
   ETH −26%→−3% (DD −56%→−43%); BTC comparable return at the lowest DD of any system (−24%). Textbook
   portfolio theory: blending uncorrelated streams raises Sharpe even when one stream is mediocre.

### Candidate "our own system" (MOST PROMISING LEAD — not yet adopted)
Equal-weight ensemble of a trend system (Donchian/EMA) + a mean-reversion system. Grounded in real
diversification theory, validated in-sample. **MUST be walk-forward / out-of-sample validated before
adoption** (zero-correlation and the ETH gain could be sample artifacts — that test has killed every
prior "improvement"). Also consider sizing mean-rev below equal weight since it bleeds alone.

## Run 12: Walk-forward VALIDATION of the ensemble (`backtester.py validate`) — QUALIFIED FAIL

Split 60/40 (train / out-of-sample test), measured each system + the 3-way ensemble in both windows.

| | In-sample best Sharpe | OUT-OF-SAMPLE result |
|---|---|---|
| BTC | Ensemble 1.91 (best) | Best single = Donchian −0.40; **Ensemble −1.45 (middle of pack)** |
| ETH | EMA 1.27, Ensemble 1.24 | Best single = EMA −1.31; **Ensemble −2.11 (middle of pack)** |

### Verdict
- ✅ **Zero correlation HELD out-of-sample** (corr trend/mean-rev = −0.00/−0.01 every window) — the
  diversification mechanism is real and stable.
- ❌ **Ensemble did NOT beat the best single system OOS** (worse Sharpe AND drawdown than the best
  single, both assets). The in-sample "ensemble is best risk-adjusted" was IN-SAMPLE LUCK. The
  flagship-candidate did not earn adoption.
- 🔴 **OOS reconfirms NO ALPHA**: every system lost money on both assets in the test window (a bear
  market). Long-biased systems don't profit in bears — they only lose less than holding.
- ✅ **What the ensemble robustly DID buy:** it avoided the worst single-system outcome (you don't
  have to guess which system wins — the winner flipped from EMA in-sample to Donchian OOS on BTC),
  and it beat buy-and-hold materially OOS (BTC −17% vs −40%; ETH −35% vs −60%).

### Conclusion (adopted)
Diversification delivers **robustness + drawdown reduction, NOT superior returns or alpha.** Do NOT
treat the ensemble as a flagship that beats everything. Use it (if at all) as the **robust default
when you don't want to bet on a single system**, with honest expectations. The validation worked: it
stopped us trading an in-sample illusion — the same fate as every other "improvement" this session.

### The meta-lesson, now overwhelming
Across Runs 6–12, EVERY attempt to beat the simple baseline (param tuning, TP brackets, RSI filter,
EMA superiority, calendar cycles, regime gating, the Adaptive-Trend idea, the ensemble) was inert,
harmful, or merely in-sample luck that failed OOS. The robust, repeatable truths are only: (1) trend
systems reduce drawdown vs buy-and-hold; (2) there is no demonstrated alpha; (3) simplicity wins.
This is strong evidence the honest play is risk-managed participation, not a search for a winning edge.

## Run 13: Forex (EUR/USD) — is it better to trade than crypto?

Pulled via `kraken ohlc EURUSD --interval 1440 --asset-class forex` (key "EUR/USD", 721 days). Ran
with a realistic forex fee (`KRAKEN_BT_FEE=0.0002`, ~a pip/side) since crypto's 0.26% would rig it.
EUR/USD annualized vol ≈ **8%** vs crypto's 50–70%.

| System | Return 2yr | vs hold | maxDD | Sharpe | OOS |
|---|---|---|---|---|---|
| Donchian (trend) | +3.9% | −4.2% | −3% | 0.54 | −2.0% |
| EMA 21/55 (trend) | +6.4% | −1.7% | −7% | 0.59 | −4.8% |
| Mean-reversion | +4.1% | −3.9% | −5% | 0.63 | **+1.5% (only OOS positive)** |
| Ensemble 3-way | +5.3% | −2.8% | −3% | 0.79 | −1.8% |
| Buy & hold | +8.1% | — | — | — | −0.7% |

### Verdict: forex is NOT better — it's a different game
1. **Tiny vol → tiny unleveraged returns** (+5%/2yr). Forex needs 10–50x **leverage** to be meaningful,
   which adds large risk — crypto gives big moves without leverage. Forex's calmness is also its problem.
2. **Trend systems UNDERPERFORMED buy-and-hold on forex** (opposite of crypto). EUR/USD ranges, doesn't
   crash — so trend-following's drawdown-dodging edge has nothing to dodge; it just lags and bleeds.
3. **Theory-consistent insight: mean-reversion suits forex** (range-bound majors) — best risk-adjusted
   here, only system positive OOS. Lesson: match asset to strategy — crypto↔trend, forex↔mean-reversion.
4. **Long-only handicaps forex badly**: EUR/USD has no upward drift, so long-only misses every USD-up
   period. Forex needs long+short — a different engine, not the same system on a new symbol.
- Held across asset classes: zero corr (trend vs mean-rev −0.00) and no OOS alpha.
**For the user's goals (no leverage, low maintenance, €1k): crypto + trend-following remains the better
fit** — not because it profits reliably (it doesn't), but because it doesn't require leverage to matter.

## Run 14: Does adding SHORTS help? (`backtester.py shorts`)

Why long-only originally: spot paper is inherently long-only; shorting needs margin (leverage) +
borrow cost + liquidation risk — a big risk step-up for a real €1k account. Tested a symmetric
long/short Donchian with varying borrow carry.

| | Long-only | L/S no carry | L/S 0.12%/day (Kraken-ish) |
|---|---|---|---|
| BTC full 2yr | **+30.0%** | +16.2% | −14.9% |
| ETH full 2yr | −25.7% | −10.1% | −34.0% |
| BTC OOS bear | −7.7% | **+9.5%** | −6.3% |
| ETH OOS bear | −39.8% | **−14.4%** | −25.5% |

### Findings
1. **Shorts help in sustained bears** (OOS): BTC −7.7%→+9.5%, ETH −39.8%→−14.4% (no carry). Intuition
   correct for that regime.
2. **But shorts HURT over the full cycle** — long-only +30% vs L/S +16% on BTC. Shorting fights
   crypto's upward drift; shorts get run over in recoveries, and trade count ~2x (more fees/whipsaw).
   Only worth it if you KNOW you're in a bear — and regime isn't reliably predictable (Run 10).
3. **Borrow carry is decisive.** At Kraken-ish 0.12%/day margin rollover, the bear benefit is eaten
   (BTC bear +9.5%→−6.3%). Multi-week margin shorts are expensive; plus leverage + liquidation risk.
4. **Long-only already captures most of the bear benefit by going to CASH**: in the OOS bear, long-only
   −7.7%/−39.8% vs buy-hold −39.7%/−60.5%. Cash dodges the crash without leverage/carry/liquidation.

### Verdict (adopted): stay LONG-ONLY
Going to cash in downtrends is the low-risk version of "profit from the bear" — ~80% of the benefit
(avoid the loss), none of the added risk. Shorts chase the last 20% but require nailing the regime AND
dodging carry, and add leverage/liquidation risk inappropriate for a real unleveraged €1k account.

## Run 15: TradingView "Donchian Breakout Strategy" — review + refinement test (`backtester.py refine`)

A popular open-source TV script. Architecture is ESSENTIALLY OURS: upside Donchian breakout entry +
lower-channel trailing-stop exit + optional MA/slope/ADR filters, long-only. (Honest source: no perf
claims, hedged notes — unlike the EMA-crossover pitch.) Two ideas in it we hadn't tested:
(a) asymmetric channels (slow entry / tight exit), (b) two-stage stop (tight until +profit, then wide).

| System | BTC full/OOS | ETH full/OOS |
|---|---|---|
| Baseline Donchian 20/10 | +30% / −7.7% | −26% / −39.8% |
| Asymmetric 40/5 | +0.9% / −11.4% | +3.9% / −13.1% |
| Two-stage (tight5→wide30 @+15%) | +1.5% / −15.4% | +42.6% / −29.4% |

### Findings
1. **CONVERGENT VALIDATION (key learning):** an independent, respected strategy lands on our exact
   architecture → our design is the established, sensible shape, not naive. Its optional filters (MA,
   slope, ADR) = ones we already tested as marginal (Runs 10–11).
2. **The refinements are NOT robust:** baseline beat them on BTC (full + OOS); they beat baseline on
   ETH — **none won on BOTH assets OOS.** Each trades BTC perf for ETH perf. The two-stage's +42.6%
   ETH is an in-sample mirage (OOS still −29.4%).
3. **Why:** tight/fast stops help a relentless grind-down (ETH bear) but get whipsawed in chop (BTC).
   Optimal stop-tightness is regime-dependent → no universal setting; baseline 20/10 is best compromise.
**Verdict: keep the robust baseline; don't adopt the refinements.** Same overfitting lesson as the
whole session — simple/robust beats clever/tuned.

## Run 16: FAITHFUL TradingView port (read the actual Pine source) — corrects Run 15

Got the real Pine Script. My Run-15 model was wrong in ways that mattered: real script uses HIGH/LOW
channels (not close), default WICK entry (resting stop at channel, fills intrabar), no entry margin,
and the two-stage "in profit" trigger is STRUCTURAL (`entry <= tight 8-period low line`), not a fixed
%. Built a faithful port (`backtester.py tv`).

| System | BTC full/OOS | ETH full/OOS |
|---|---|---|
| Our close-based 20/10 +margin | +30% / −7.7% | −26% / −39.8% |
| TV wick 20/10 | +18% / −9.6% | +18% / −30.6% |
| TV wick + two-stage | +22% / −9.1% | +41% / −24.2% |
| TV close + two-stage | +28% / −7.6% | −1% / −42.8% |

### Findings (incl. a CORRECTION to Run 15)
1. **CORRECTION: the structural two-stage stop IS a real, broad improvement.** Run 15 dismissed it,
   but that used a mismodeled fixed-% trigger. The faithful structural version improved EVERY config
   (both entry modes, both assets, full-period, mostly OOS): BTC wick +18→+22, BTC close +13→+28, ETH
   wick +18→+41, ETH close −6→−1. **First refinement all session to help across the board, not one
   asset.** Only caught because we read the actual source — lesson: model the real thing.
2. **Wick-vs-close entry is asset-dependent & vindicates the close-based choice on BTC:** wick helped
   ETH trends (+18% vs our −26%) but HURT BTC (+18% vs our +30%) — in BTC chop, wick entries caught the
   false breakouts that closes filter ("wicks fool you" is real on BTC). Neither mode wins both.
3. **Still NO alpha:** best config (ETH wick+two-stage) was −24% OOS — loses less, still loses.

### Action: the structural two-stage stop is the one promising refinement found all session.
Worth grafting onto our system (close-based entry + structural two-stage exit) and validating further.
It improves the SHAPE of returns (cut losers faster, let winners breathe) — risk tool, not alpha.

## Run 17: TradingView "Machine Learning RSI | AI Classification & Ranking" (Zeiierman) — falsifiable-core test

Second TV script reviewed. Critical structural fact: it's an `indicator()`, not a `strategy()` — no
backtest/P&L exists for it anywhere, despite 15+ tunable parameters (classic overfitting setup). Core
mechanism: k=8 nearest-neighbor classifier over 8 RSI-derived features (value, slope, acceleration,
midpoint distance, percentile, volatility, fast/slow spread, regime), voting on a 4-bar-ahead
direction vs an ATR-scaled threshold. Construction is honest (no repaint, proper lag).

Wrote `mlrsi_test.py`: a lean, equal-weight-feature port of just the kNN engine (the Fisher
auto-weighting is a refinement — if the unweighted core has no edge, reweighting can't manufacture
one), measuring directional hit-rate vs a majority-class baseline.

| Pair | Full hit-rate vs base | In-sample edge | OOS edge |
|---|---|---|---|
| BTCEUR | 47.2% vs 52.3% | −1.7 pts | −14.0 pts |
| ETHEUR | 46.9% vs 50.8% | −6.6 pts | −8.5 pts |

### Findings
1. **The kNN core has NEGATIVE edge everywhere** — not just OOS, but even IN-SAMPLE (where overfitting
   normally makes things look artificially good). It underperforms simply always guessing the
   majority direction, on both assets, on every split.
2. **The 8 features are too collinear to carry information.** All 8 are transforms of the same
   underlying RSI(14)/price series (value, slope, accel, %rank, spread of RSI(7) vs RSI(28), etc.) —
   effectively ~1-2 independent dimensions dressed as 8. Lorentzian distance over redundant axes
   doesn't find meaningfully "similar" history.
3. **4-bar-ahead direction vs 0.5×ATR is close to coin-flip territory** on daily crypto — consistent
   with the negative in-sample result; there's barely a learnable signal at this horizon even with
   foresight.
4. **The visible "signals" on the chart are very likely driven by the ML-adaptive Supertrend
   (trailing-stop trend-follower), not the kNN.** We already extensively tested trend-following
   trailing stops this session (Donchian, EMA, the TV Donchian port) — this would just be another
   variant of the same family, not a new edge.

**Verdict: no demonstrated edge, do not pursue.** The headline "AI classification" core fails its most
basic test (beat a coin-flip-ish majority baseline) even in-sample. Combined with 15+ untested tunable
parameters and an `indicator()`-only implementation (its author has apparently never backtested it
either), this is a pattern-matching visual tool, not a strategy. Consistent with this session's
meta-lesson: complexity ≠ edge; the validated baseline (Donchian + structural two-stage stop, Run 16)
remains the best lead.

## Run 18: TradingView "3Commas Bot" template — EMA21/50 cross + swing/ATR stop + long/short/flip

A real `strategy()` (unlike the last two): EMA(21)x EMA(50) crossover entries, **long AND short by
default with reversal flips**, stop = swing-high/low(5) +/- ATR(14), fixed 1:1 R:R take-profit by
default (optional ATR trailing stop instead). Ported faithfully (`backtester.py tcb`).

| System | BTC full/OOS | ETH full/OOS | trades (full/OOS-eligible) |
|---|---|---|---|
| Our baseline Donchian 20/10 | +30.0% / −7.7% | −25.7% / −39.8% | 13 / 16 |
| 3Commas DEFAULT (L+S+flip, 1:1 TP) + 0.12%/day carry | +6.0% / −7.7% | +53.8% / +17.2% | 12 / 10 |
| 3Commas L+S+flip, ATR trailing + carry | +4.9% / +0.4% | +13.1% / +23.4% | 12 / 10 |
| 3Commas **long-only** (no shorts/flip), 1:1 TP | −3.0% / −10.4% | +12.7% / −21.2% | 6 / 5 |
| 3Commas **long-only**, ATR trailing | −6.9% / −5.4% | −15.4% / −15.3% | 6 / 5 |

### Findings
1. **First system all session with positive OOS Sharpe on BOTH assets** (ATR-trailing+carry: BTC
   0.14, ETH 1.09) — looked like a milestone, but the trade dump kills the excitement: ETH had only
   **5 OOS trades**, and the pattern is "every short won (+23.7%, +22.1%, +13.6%), every long lost
   (−11.0%, −7.7%)." That's not an edge — it's "ETH was in one clean sustained downtrend during the
   OOS window, and a system allowed to short rode that single trend." Same regime-dependency
   documented all session (Run 10), just expressed via 5 trades instead of 16.
2. **DECISIVE: under our actual long-only/spot constraint, this bot is WORSE than our baseline on
   BOTH assets** (BTC −3.0%/−10.4% and −6.9%/−5.4% vs our +30%/−7.7%; ETH +12.7%/−21.2% and
   −15.4%/−15.3% vs our −25.7%/−39.8%, still negative). Strip out shorting and the EMA-cross +
   fixed-1:1-TP + ATR-stop combo underperforms — consistent with Run 7 (fixed TP hurts trend-
   following) and Run 9 (EMA cross alone, no edge).
3. **Refines (doesn't reverse) Run 14 on carry cost:** Run 14 found 0.12%/day carry ATE almost the
   entire short benefit for Donchian long/short (+9.5%→−6.3%). Here carry barely dents it (ETH ATR-
   trailing OOS +29.9%→+23.4%) — because EMA-cross signals are rarer and the ATR/swing stop exits
   faster, so far less carry accumulates per trade. If shorts are ever revisited: trade frequency/
   duration matters more for carry cost than the entry/exit shape itself. Not actionable now.

**Verdict: no change to the long-only conclusion (Run 14).** The standout OOS numbers come entirely
from shorting through one clean ETH downtrend (5 trades, not statistically meaningful), and the
long-only version of this same bot loses to our baseline on both assets. Logged as a data point on
the shorts question, nothing adopted.

## Run 19: Our close-based entry + structural two-stage stop — walk-forward validated (ADOPTED)

Built `run_strategy_ts` (`backtester.py ts <PAIR>`): identical entry/fees to our baseline
(`run_strategy`, 20/10/0.5%), but the exit is Run 16's structural two-stage channel — a TIGHT
close-based 8-day-low stop until the trade moves "in profit" relative to it (entry price <= tight
8d-low), then it switches permanently to the WIDE 10-day-low for the rest of the trade.

| System | BTC full | BTC OOS | ETH full | ETH OOS |
|---|---|---|---|---|
| Baseline (simple 10d-low exit) | +30.0% / Sh 0.80 / DD −28% | −7.7% / Sh −0.40 / DD −20% | −25.7% / Sh −0.11 / DD −56% | −39.8% / Sh −2.15 / DD −44% |
| **Two-stage (tight8→wide10)** | **+35.4% / Sh 0.89 / DD −26%** | **−6.5% / Sh −0.32 / DD −20%** | **−16.2% / Sh +0.05 / DD −54%** | **−37.7% / Sh −2.01 / DD −42%** |

Trade count unchanged (13 BTC / 16 ETH) — same entries, only exits shift.

### Findings
1. **Improved on every axis, both assets, both splits.** Return, Sharpe, AND max-drawdown all moved in
   the favorable direction for BTC and ETH, in the full period AND out-of-sample. This is the first
   refinement all session to be unambiguously better everywhere with no tradeoff.
2. **Per-trade dump confirms it's a real mechanism, not 1-2 lucky trades:** 3/13 BTC trades and 4/16
   ETH trades changed — every changed trade was a LOSER that got cut earlier/smaller (e.g. BTC
   −7.6%→−5.0%, −4.6%→−3.3%; ETH −9.2%→−4.4%, −7.1%→−3.8%, −11.7%→−8.6%). All winning trades are
   byte-identical to baseline. The tight 8d-low simply exits a losing trade sooner when it never
   reached "in profit" status — pure better risk control, no change to how winners are ridden.
3. **Still NO OOS alpha** (both OOS returns remain negative, Sharpe still negative). Consistent with
   the session-wide finding: this is a risk-shape improvement (smaller losses), not a new source of
   edge.

**Verdict: ADOPTED.** Clean, mechanistic, no-downside refinement to the validated Run 7 exit rule.
Wired into the live system: `backtester.py signals <PAIR> [--entry-price X]` now shows both exit
channels (tight 8d-low / wide 10d-low) and, if holding, which stage applies and the live exit price.
SKILL.md's exit-rule section updated accordingly. `run_strategy` (the historical-comparison baseline
referenced by Runs 6-18) is left unchanged so those numbers remain meaningful as written;
`run_strategy_ts` / `backtester.py ts <PAIR>` is the new two-stage version for re-validation.

## Run 20: Rob Carver's range-normalized breakout (qoppac 2016) — tested, nothing adopted

Highest-quality source assessed all session: Rob Carver (ex-AHL/Man Group systematic trader, author
of *Systematic Trading* etc.) — rigorous, anti-hype, cost-aware, the same philosophy this project
runs on. His "simple breakout rule" is a CONTINUOUS, range-normalized trend forecast:
`(price − rangemid)/(rangehigh − rangelow)` over a lookback, EWMA-smoothed (span ≈ lb/4), giving a
graded −0.5…+0.5 conviction you size into — unlike our binary in/out Donchian. Carver notes in the
post it's ~the same thing as a moving-average crossover (same trend family we run, Run 9).

Ported faithfully (`backtester.py breakout`): traded long-only (our constraint), net of 0.26%/side
fees charged on every rebalance. `turn` = total turnover (≈ position-change units; our binary ≈ 13).

| BTC system | FULL Sh | turn | OOS Sh || ETH system | FULL Sh | OOS Sh |
|---|---|---|---|---|---|---|---|
| Our Donchian two-stage | **0.89** | 13 | **−0.32** || Our Donchian two-stage | 0.05 | −2.01 |
| Carver sign lb20 | 0.74 | 36 | −0.21 || Carver sign lb20 | 0.33 | −1.46 |
| Carver continuous lb20 | 0.41 | 37 | −0.93 || Carver continuous lb20 | 0.53 | −1.47 |
| Carver sign lb40 | 0.58 | 20 | −0.94 || Carver sign lb40 | 0.58 | −1.65 |
| Carver continuous lb40 | 0.70 | 17 | −1.31 || Carver continuous lb40 | 0.22 | −2.44 |

### Findings
1. **No robust winner — the signature of noise, not edge.** The "best" Carver config flips by asset
   (sign-lb20 on BTC; sign-lb40 / cont-lb20 on ETH) and the full-period winner is never the OOS
   winner. Picking one would be curve-fitting on tiny data (the Run 6 trap). Our binary Donchian has
   the best BTC Sharpe (0.89) outright; on ETH some Carver configs post higher *raw* return but only
   because the looser always-near-in signal caught more bounces in a −52% bear — still −1.5…−2.4 OOS.
2. **Turnover kills it on our account.** Carver configs turn 17–38 vs our 13; the continuous version
   rebalances near-daily. On 0.52% round-trip that drag is in the net numbers and it *hurts* (BTC
   continuous Sharpe 0.41 vs our 0.89). Carver's framework assumes cheap futures execution + a no-trade
   buffer (my port omits the buffer — but even buffered it out-trades our binary and stays −OOS).
3. **Every config negative OOS on both assets** — no exception to the session-long no-alpha finding.
4. **The valuable parts of Carver's framework don't fit our constraints.** Continuous conviction-
   sizing, vol-normalized risk targeting, multi-speed combination, many-instrument diversification —
   all real, but unlocked by leverage + a large portfolio + cheap execution. We have €1k, unleveraged,
   spot, 2 correlated assets, high fees. The continuous sizing is actively *penalized* by our costs.

**Verdict: nothing adopted; strong endorsement of the source.** Carver's actual lesson for us is the
meta-one we already hold — trend-following is a risk tool, normalize/diversify/size-by-risk *if you
have the scale*. We don't, so our stripped-down binary breakout + two-stage exit is the honest fit.
`backtester.py breakout <PAIR>` + `run_breakout()` / `carver_breakout()` retain the comparison.

## Run 21: Kraken Prop evaluation simulator — can our system pass a funded-account challenge?

User wants to attempt Kraken Prop (https://www.kraken.com/prop) with ~$20K and leverage. Pulled the
real rules (2026-06-15): single-step, no time limit; **3% max daily loss** (all plans); **static**
max total drawdown from starting balance (Starter 6% / Intermediate 5% / Advanced 3%); up to **5x**
leverage; **60+ crypto pairs** (so our BTCEUR/ETHEUR data + validated systems apply directly). Eval
fee $20–$1,090; 80–90% profit split; "most applicants do not pass on their first attempt."

Built `prop_sim.py`: Monte-Carlo block-bootstrap (block=10d, preserves vol-clustering) of a strategy's
real daily returns through the actual rules, 10,000 simulated attempts/cell, exposure E = notional/
equity (E=5 is max leverage). Profit target parameterized (default 8%). Tested the two-stage system.

| Plan (max DD) | zero-edge ruin refn | P(pass) 1x | P(pass) 5x | dominant failure |
|---|---|---|---|---|
| Starter (6%) | 43% | BTC 39.5% / ETH 28.4% | ~40% / 39% | daily-loss bust 56–70% |
| Intermediate (5%) | 38% | 38.7% / 28.3% | ~41% / 39% | daily-loss bust |
| Advanced (3%) | 27% | 34.7% / 27.6% | ~41% / 39% | daily-loss bust + DD |

### Findings
1. **P(pass) only tracks (or trails) the ZERO-SKILL gambler's-ruin rate** [floor/(target+floor)]. The
   strategy adds no skill to passing — consistent with the session-long no-OOS-alpha finding. You'd
   pay the eval fee to play a roughly fair-to-unfavorable lottery.
2. **The 3% DAILY-loss limit is the dominant killer (56–70% of failures)**, not the total-drawdown
   limit. Our trend system manages trade risk, not daily risk — it sits through big red days while in
   position, which is exactly what the daily limit punishes. Adapting would require hard intraday
   daily-loss stops — which CONTRADICTS validated Run 7 (no fixed stops) with no evidence the result
   has edge.
3. **Leverage does NOT improve P(pass) — it's strictly worse.** Pass-rate is ~flat 1x→5x; leverage
   only shifts the bust mode from drawdown to daily-loss. The "leverage to amplify returns" premise
   fails: a system with 20–42% natural OOS drawdowns vs a 6% static floor must trade SMALLER than
   unleveraged, not bigger.
4. **The simulation is OPTIMISTIC.** It uses close-to-close daily returns; Kraken's daily-loss limit
   triggers INTRADAY, where excursions exceed the close. Real P(pass) is below these numbers, and the
   gap widens with leverage. ~35% is a ceiling, not an estimate.
5. **Even passing is negative-EV long-run:** the funded account keeps the same absorbing barriers with
   no edge, so it eventually busts; you pay eval fees repeatedly to reach an account that bleeds out.

**Verdict: not a viable profit path.** Same root cause as everything since Run 6 — no demonstrated
edge — but prop rules + leverage convert "harmless (risk tool)" into "fatal (negative EV)." If the
user proceeds anyway, the least-bad configuration is: lowest tier/target, **minimum** leverage (not
max), and a hard intraday daily-loss stop well inside 3% — accepting it's a lottery, not an edge.
`prop_sim.py` is the go/no-go gate for any candidate strategy.

## Future runs
- Re-run `backtester.py validate` periodically as the OOS window grows / new regimes appear.
- If ever pursuing the ensemble, size mean-rev below equal weight and re-validate.
- Re-run `sweep` / `brackets` / `abtest` / `compare` / `frameworks` as data accrues.
- Test the engine on more assets / a basket to see if the drawdown-reduction edge is universal.
- Once live decisions accumulate in trading_journal.md, A/B those real-time calls vs. the mechanical
  baseline too (the cleanest test — truly no hindsight).
- Cross-reference with [trading_journal.md](trading_journal.md) for live paper trading decisions.
