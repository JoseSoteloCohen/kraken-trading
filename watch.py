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
HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS_FILE = os.path.join(HERE, "levels_watch.md")
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

def main():
    ap = argparse.ArgumentParser(description="Kraken mechanical daily watcher")
    ap.add_argument("--confirmed", action="store_true",
                    help="evaluate the last COMPLETED daily candle (drop today's in-progress "
                         "candle), so a break must be a real daily CLOSE, not an intraday poke. "
                         "Use this for scheduled daily runs.")
    args = ap.parse_args()
    today_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    levels = parse_levels(LEVELS_FILE)
    any_break = False
    mode = "CONFIRMED daily close" if args.confirmed else "intraday (in-progress candle)"
    print(f"=== Kraken mechanical watch [{mode}] | break-quality margin {MARGIN*100:.2f}% ===\n")
    for pair in PAIRS:
        bars = bt.load(pair, refresh=True)
        if args.confirmed:                       # drop today's still-forming candle
            bars = [b for b in bars if bt.dstr(b["t"]) < today_utc]
        closes = [b["c"] for b in bars]
        live = bt.fetch_ticker(pair)
        last_close = closes[-1]; i = len(closes) - 1
        ph = max(closes[i-20:i]); tight = min(closes[i-8:i]); wide = min(closes[i-10:i])
        ef, es = bt.ema(closes, 21), bt.ema(closes, 55)
        ma200 = bt.sma(closes, 200)[-1]
        regime = "BULL" if (ma200 and last_close > ma200) else "BEAR"
        lv = levels[pair]; up, down = lv["up"], lv["down"]
        print(f"-- {pair} -- live {live:,.0f} | last daily close {last_close:,.0f} ({bt.dstr(bars[-1]['t'])})")
        print(f"   Regime(200d {ma200:,.0f}): {regime} | EMA21 {ef[-1]:,.0f} {'>' if ef[-1]>es[-1] else '<'} EMA55 {es[-1]:,.0f}")
        print(f"   Donchian 20d-high {ph:,.0f} | two-stage exit: tight8 {tight:,.0f} / wide10 {wide:,.0f}")
        # Break-quality filter on the canonical DAILY CLOSE (the skill defines breaks on closes).
        fired = []
        if up and last_close >= up * (1 + MARGIN):
            fired.append(f"UPSIDE break: close {last_close:,.0f} cleared €{up:,.0f} by {(last_close/up-1)*100:.1f}% -> LONG candidate")
        if down and last_close <= down * (1 - MARGIN):
            fired.append(f"DOWNSIDE break: close {last_close:,.0f} cleared €{down:,.0f} by {(1-last_close/down)*100:.1f}% -> SHORT candidate")
        if fired:
            any_break = True
            for f in fired:
                print(f"   ** CONFIRMED {f}")
        else:
            dists = []
            if up:   dists.append(f"upside €{up:,.0f} ({(up/last_close-1)*100:+.1f}%)")
            if down: dists.append(f"downside €{down:,.0f} ({(down/last_close-1)*100:+.1f}%)")
            print(f"   all quiet — nearest: {', '.join(dists) if dists else 'no levels set'}")
        print()
    if any_break:
        print("RESULT: CONFIRMED BREAK — review for an entry decision (do NOT auto-trade).")
        sys.exit(10)
    print("RESULT: ALL QUIET — no confirmed break. FLAT stays FLAT.")
    sys.exit(0)

if __name__ == "__main__":
    main()
