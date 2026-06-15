#!/usr/bin/env python3
"""Reveal ONE day's OHLC at a time for blind daily walk-forward backtesting.
Usage: reveal_day.py <file_path> <day_number>
Prints only day <day_number> (1-indexed). Nothing about later days.
On day 1 it also prints the prior 10 days (pre-window context) so a starting
range exists, since you can't trade a break without a reference range.
"""
import json, datetime, sys

def load(path):
    d = json.load(open(path))
    k = [x for x in d if x != 'last'][0]
    return d[k]

def fmt(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%d')

def line(c):
    o,h,l,cl = float(c[1]),float(c[2]),float(c[3]),float(c[4])
    pct = (cl-o)/o*100
    return f"{fmt(c[0])}: O={o:.0f} H={h:.0f} L={l:.0f} C={cl:.0f} ({pct:+.2f}%)"

def main():
    path = sys.argv[1]
    spec = sys.argv[2]
    data = load(path)
    if '-' in spec:
        a, b = spec.split('-')
        start, end = int(a), int(b)
    else:
        start = end = int(spec)
    for n in range(start, end+1):
        if n < 1 or n > len(data):
            print(f"day {n} out of range (1..{len(data)})")
            continue
        print(f"Day {n}: {line(data[n-1])}")

if __name__ == '__main__':
    main()
