#!/usr/bin/env python3
"""Reveal weekly OHLC aggregates one week at a time, for blind walk-forward backtesting.
Usage: reveal_week.py <week_number>
Prints aggregated weekly OHLC for week <week_number> only (1-indexed), plus a running
cumulative summary of weeks 1..week_number. Does not print anything about later weeks.
"""
import json, datetime, sys

WEEK_LEN = 7
data_path = '/tmp/btc_blind.json'

def load_weeks():
    d = json.load(open(data_path))
    k = [x for x in d if x != 'last'][0]
    data = d[k]
    weeks = []
    for i in range(0, len(data), WEEK_LEN):
        chunk = data[i:i+WEEK_LEN]
        if len(chunk) < 2:
            continue
        start = datetime.datetime.fromtimestamp(chunk[0][0], datetime.timezone.utc).strftime('%Y-%m-%d')
        end = datetime.datetime.fromtimestamp(chunk[-1][0], datetime.timezone.utc).strftime('%Y-%m-%d')
        o = float(chunk[0][1])
        h = max(float(c[2]) for c in chunk)
        l = min(float(c[3]) for c in chunk)
        c = float(chunk[-1][4])
        vol = sum(float(c[5]) for c in chunk)
        weeks.append((start, end, o, h, l, c, vol, len(chunk)))
    return weeks

def main():
    n = int(sys.argv[1])
    weeks = load_weeks()
    if n < 1 or n > len(weeks):
        print(f"week {n} out of range (1..{len(weeks)})")
        return
    w = weeks[n-1]
    pct = (w[5]-w[2])/w[2]*100
    print(f"Week {n}: {w[0]} -> {w[1]} ({w[7]}d)")
    print(f"  Open={w[2]:.1f} High={w[3]:.1f} Low={w[4]:.1f} Close={w[5]:.1f} | change={pct:+.2f}%")

if __name__ == '__main__':
    main()
