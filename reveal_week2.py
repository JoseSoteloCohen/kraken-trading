#!/usr/bin/env python3
"""Reveal one week's aggregated OHLC at a time for blind walk-forward backtesting.
Usage: reveal_week2.py <file_path> <week_number>
Prints ONLY the requested week's aggregated OHLC. Nothing about later weeks.
"""
import json, datetime, sys

WEEK_LEN = 7

def load_weeks(path):
    d = json.load(open(path))
    k = [x for x in d if x != 'last'][0]
    data = d[k]
    weeks = []
    for i in range(0, len(data), WEEK_LEN):
        chunk = data[i:i+WEEK_LEN]
        if len(chunk) < 2:
            continue
        fmt = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%d')
        o = float(chunk[0][1])
        h = max(float(c[2]) for c in chunk)
        l = min(float(c[3]) for c in chunk)
        c = float(chunk[-1][4])
        weeks.append((fmt(chunk[0][0]), fmt(chunk[-1][0]), o, h, l, c, len(chunk)))
    return weeks

def main():
    path = sys.argv[1]
    n = int(sys.argv[2])
    weeks = load_weeks(path)
    if n < 1 or n > len(weeks):
        print(f"week {n} out of range (1..{len(weeks)})")
        return
    w = weeks[n-1]
    pct = (w[5]-w[2])/w[2]*100
    print(f"Week {n}: {w[0]} -> {w[1]} ({w[6]}d)")
    print(f"  Open={w[2]:.2f} High={w[3]:.2f} Low={w[4]:.2f} Close={w[5]:.2f} | change={pct:+.2f}%")

if __name__ == '__main__':
    main()
