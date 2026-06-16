#!/usr/bin/env python3
"""
Cloud-friendly mechanical watcher for the Kraken disciplined-trading workflow.

This is what a Claude Code Routine (or a plain cron job) runs once a day. It:
  1. Pulls fresh daily candles + the live price for BTCEUR & ETHEUR from Kraken's public API
     (stdlib only — no API key, no `kraken` CLI, no WSL; runs anywhere, incl. a fresh cloud clone).
  2. Reads the current trigger levels out of levels_watch.md.
  3. Prints the parallel-systems snapshot: 200d regime, Donchian two-stage exit channels, EMA 21/55.
  4. Applies the BREAK-QUALITY FILTER (the daily close must clear a level by >= MARGIN, default
     0.5%) and reports, per asset, whether a CONFIRMED break has fired.

It NEVER places a trade. It surfaces "all quiet" vs "a confirmed break may be forming — review for
an entry." The decision stays with the user (and Claude, per the skill rules).

Exit code: 0 = all quiet, 10 = at least one confirmed break (handy for `python3 watch.py || notify`
on a POSIX shell). The printed `RESULT:` line is the canonical signal — the GitHub Actions workflow
keys off that, not the exit code, so it's robust even where a shell wrapper swallows the code.

Pass `--confirmed` (scheduled/cloud runs) to judge the last COMPLETED daily candle instead of
today's in-progress one — so a break must be a real daily CLOSE, not an intraday poke.
"""
import re, sys, os, argparse, datetime
import backtester as bt

PAIRS = ["BTCEUR", "ETHEUR"]
MARGIN = float(os.environ.get("BREAK_MARGIN", "0.005"))          # 0.5% break-quality filter
ACCOUNT_EUR = 1000.0   # flat-balance assumption used only to size the break-alert proposal
HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS_FILE = os.path.join(HERE, "levels_watch.md")
JOURNAL_FILE = os.path.join(HERE, "trading_journal.md")
SECTION = {"BTCEUR": "BTC/EUR", "ETHEUR": "ETH/EUR"}

def parse_levels(path):
    """Extract {pair: {'down': float|None, 'up': float|None}} from levels_watch.md.
    Tolerant: looks for the first €-number on the Downside/Upside trigger line in each pair block."""
    levels = {p: {"down": None, "up": None} for p in PAIRS}
    if not os.path.exists(path):
        return levels
    text = open(path, encoding="utf-8").read()
    for pair in PAIRS:
        m = re.search(rf"##\s*{re.escape(SECTION[pair])}(.*?)(?:\n##\s|\Z)", text, re.S)
        if not m:
            continue
        block = m.group(1)
        for key, word in (("down", "Downside"), ("up", "Upside")):
            lm = re.search(rf"{word} trigger.*?€\s*([\d,]+(?:\.\d+)?)", block, re.S)
            if lm:
                levels[pair][key] = float(lm.group(1).replace(",", ""))
    return levels

def journal_entries(results, confirmed):
    """Append a dashboard-compatible entry per pair to trading_journal.md, skipping any pair
    whose date already has an entry (idempotent). Returns the number of entries written."""
    existing = open(JOURNAL_FILE, encoding="utf-8").read() if os.path.exists(JOURNAL_FILE) else ""
    blocks = []
    for r in results:
        if re.search(rf"^### {re.escape(r['date'])}(?: \d{{2}}:\d{{2}})? — {re.escape(r['pair'])}\b",
                     existing, re.M):
            continue                                      # already logged this date+pair
        if r["fired"]:
            side = r["fired"][0][0]
            verdict = (f"{side} candidate — confirmed {'upside' if side == 'LONG' else 'downside'} "
                       f"break (review, never auto-trade)")
        else:
            verdict = "FLAT — no confirmed break"
        ema = "bull" if r["ef"] > r["es"] else "bear"
        trig = [t for t in ((f"down €{r['down']:,.0f}" if r["down"] else ""),
                            (f"up €{r['up']:,.0f}" if r["up"] else "")) if t]
        snap = (f"automated daily watch ({'confirmed close' if confirmed else 'intraday'}). "
                f"price ~€{r['close']:,.0f}. Regime {r['regime']} (200d MA €{r['ma200']:,.0f}). "
                f"EMA 21/55 {ema} ({r['ef']:,.0f}/{r['es']:,.0f}). Donchian 20d-high €{r['ph']:,.0f}. "
                f"Two-stage exit tight8 €{r['tight']:,.0f}/wide10 €{r['wide']:,.0f}. "
                f"Triggers: {', '.join(trig) if trig else 'none set'}.")
        blocks.append(
            f"### {r['date']} — {r['pair']}\n"
            f"- Market snapshot: {snap}\n"
            f"- Recommendation/reasoning: {verdict}. Mechanical daily watch (GitHub Actions); the "
            f"human/Claude layer makes the actual call on a confirmed break.\n"
            f"- Action taken: no action (mechanical watch — never trades).\n"
            f"- Prediction: re-checked daily; a confirmed break = daily close beyond a trigger by >=0.5%.\n"
            f"- Review (filled in later): _pending_.")
    if blocks:
        with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "\n\n".join(blocks) + "\n")
    return len(blocks)

def _plan(pair, fired, close, tight, wide, regime):
    """Decision-ready proposal printed when a break fires, so the alert arrives review-ready.
    Long-only/spot: only an UPSIDE break is an entry; a downside break means stay in cash."""
    sides = {s for s, _ in fired}
    out = ["   --- decision-ready plan (PROPOSAL — review regime + news, then approve; never auto-traded) ---"]
    if "LONG" in sides:
        dist = (close - tight) / close if close else 0.0
        units = ACCOUNT_EUR / close if close else 0.0
        risk = ACCOUNT_EUR * dist
        trim = "  [BEAR regime -> consider HALF size (Run 10)]" if regime == "BEAR" else ""
        out += [
            f"   LONG {pair}: entry ref €{close:,.0f} (the confirmed close)",
            f"     initial stop = tight 8d-low €{tight:,.0f} ({dist*100:.1f}% below entry); "
            f"widens to 10d-low €{wide:,.0f} once in profit (Run 19 two-stage)",
            f"     size: full = flat cash ~€{ACCOUNT_EUR:,.0f} -> {units:.4f} units; "
            f"max risk if stopped at the tight low ~€{risk:,.0f} ({dist*100:.1f}%){trim}",
            "     NO fixed take-profit (Run 7) — the trailing two-stage stop decides the exit.",
        ]
    if "SHORT" in sides:
        out += [
            f"   DOWNSIDE break {pair}: long-only/spot (Run 14) — NO short.",
            "     if FLAT: stay in cash. If holding a long: the two-stage trailing stop is your exit.",
        ]
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser(description="Kraken mechanical daily watcher")
    ap.add_argument("--confirmed", action="store_true",
                    help="evaluate the last COMPLETED daily candle (drop today's in-progress "
                         "candle), so a break must be a real daily CLOSE, not an intraday poke. "
                         "Use this for scheduled daily runs.")
    ap.add_argument("--journal", action="store_true",
                    help="append a dashboard-compatible entry per pair to trading_journal.md "
                         "(idempotent per date+pair). Use on scheduled runs to keep a record.")
    args = ap.parse_args()
    today_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    levels = parse_levels(LEVELS_FILE)
    any_break = False
    mode = "CONFIRMED daily close" if args.confirmed else "intraday (in-progress candle)"
    print(f"=== Kraken mechanical watch [{mode}] | break-quality margin {MARGIN*100:.2f}% ===\n")
    results = []
    for pair in PAIRS:
        bars = bt.load(pair, refresh=True)
        if args.confirmed:                       # drop today's still-forming candle
            bars = [b for b in bars if bt.dstr(b["t"]) < today_utc]
        closes = [b["c"] for b in bars]
        live = bt.fetch_ticker(pair)
        last_close = closes[-1]; i = len(closes) - 1
        cdate = bt.dstr(bars[-1]["t"])
        ph = max(closes[i-20:i]); tight = min(closes[i-8:i]); wide = min(closes[i-10:i])
        ef, es = bt.ema(closes, 21), bt.ema(closes, 55)
        ma200 = bt.sma(closes, 200)[-1]
        regime = "BULL" if (ma200 and last_close > ma200) else "BEAR"
        lv = levels[pair]; up, down = lv["up"], lv["down"]
        print(f"-- {pair} -- live {live:,.0f} | last daily close {last_close:,.0f} ({cdate})")
        print(f"   Regime(200d {ma200:,.0f}): {regime} | EMA21 {ef[-1]:,.0f} {'>' if ef[-1]>es[-1] else '<'} EMA55 {es[-1]:,.0f}")
        print(f"   Donchian 20d-high {ph:,.0f} | two-stage exit: tight8 {tight:,.0f} / wide10 {wide:,.0f}")
        # Break-quality filter on the canonical DAILY CLOSE (the skill defines breaks on closes).
        fired = []
        if up and last_close >= up * (1 + MARGIN):
            fired.append(("LONG", f"UPSIDE break: close {last_close:,.0f} cleared €{up:,.0f} by {(last_close/up-1)*100:.1f}% -> LONG candidate"))
        if down and last_close <= down * (1 - MARGIN):
            fired.append(("SHORT", f"DOWNSIDE break: close {last_close:,.0f} cleared €{down:,.0f} by {(1-last_close/down)*100:.1f}% -> SHORT candidate"))
        if fired:
            any_break = True
            for _, msg in fired:
                print(f"   ** CONFIRMED {msg}")
            print(_plan(pair, fired, last_close, tight, wide, regime))
        else:
            dists = []
            if up:   dists.append(f"upside €{up:,.0f} ({(up/last_close-1)*100:+.1f}%)")
            if down: dists.append(f"downside €{down:,.0f} ({(down/last_close-1)*100:+.1f}%)")
            print(f"   all quiet — nearest: {', '.join(dists) if dists else 'no levels set'}")
        print()
        results.append(dict(pair=pair, date=cdate, close=last_close, regime=regime, ma200=ma200,
                            ef=ef[-1], es=es[-1], ph=ph, tight=tight, wide=wide, up=up, down=down,
                            fired=fired))
    if args.journal:
        n = journal_entries(results, args.confirmed)
        print(f"[journal] appended {n} entr{'y' if n == 1 else 'ies'} to {os.path.basename(JOURNAL_FILE)}\n")
    if any_break:
        print("RESULT: CONFIRMED BREAK — review for an entry decision (do NOT auto-trade).")
        sys.exit(10)
    print("RESULT: ALL QUIET — no confirmed break. FLAT stays FLAT.")
    sys.exit(0)

if __name__ == "__main__":
    main()
