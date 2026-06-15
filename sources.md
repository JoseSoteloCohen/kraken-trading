# Vetted News & Data Sources

Curated, credibility-tiered source list for trading-context research. **Only consume Tier 1/2 for
decisions; never the blocklist.** Enforce via WebSearch `allowed_domains` / `blocked_domains`.

Rationale: backtests (see [backtest_journal.md](backtest_journal.md)) showed the market-moving
signal is **macro facts** (Fed, inflation, ETF flows, filings), not crypto-blog opinion. Weight
neutral newswires above exchange-owned commentary (exchanges have a structural interest in you
trading).

## 🟢 Tier 1 — Primary (weight highest, macro + market-moving facts)
- **TradingView News** — https://www.tradingview.com/news/ — aggregates Reuters/Dow Jones/GlobeNewswire; single entry point for macro + cross-asset + crypto. Confirmed readable via WebFetch.
- Reuters — reuters.com
- Bloomberg — bloomberg.com (often paywalled; WebFetch may get only headlines)
- Wall Street Journal — wsj.com (paywalled)
- Financial Times — ft.com (paywalled)
- Associated Press — apnews.com
- CNBC — cnbc.com
- Fortune — fortune.com

## 🟢 Tier 1 — Primary / official (raw facts, no spin)
- Federal Reserve — federalreserve.gov
- SEC (filings/EDGAR) — sec.gov
- Bureau of Labor Statistics (inflation/CPI) — bls.gov

## 🟡 Tier 2 — Secondary (crypto-specific events; more headline-driven)
- CoinDesk — coindesk.com
- The Block — theblock.co
- Blockworks — blockworks.co
- DL News — dlnews.com
- Cointelegraph — cointelegraph.com (use with care, more promotional)

## 🟡 Tier 2 — Sentiment only (exchange house view — NOT neutral fact)
- **Bitvavo Industry** — https://bitvavo.com/en/news (Industry section) — weekly cadence, matches weekly trading rhythm. Listing shows headlines only; fetch individual articles for analysis.

## 🔵 Data utility (price/trend cross-check, NOT a news source)
- **Kraken market summary** — https://www.kraken.com/convert/btc/usd (swap pair in URL) — live price + 7d/30d/1y % changes. Same data as the CLI, pre-summarized. Convenience cross-check only.

## 🔴 Blocklist — prediction/affiliate SEO mills (NEVER consume)
intellectia.ai, coindcx.com, changelly.com, coinpedia.org, cryptopolitan.com, moneymagpie.com,
bitcoinfoundation.org, buyucoin.com, mexc.com, litefinance.org

## Usage notes
- For macro/decision research: WebSearch with `allowed_domains` set to Tier 1 (+ Tier 2 if crypto-specific), `blocked_domains` set to the blocklist.
- Treat exchange sources (Bitvavo, Kraken) as sentiment/convenience, weight neutral newswires higher.
- News is a **risk-flag/tiebreaker**, not the primary driver — price-action discipline leads (see backtest takeaways).
