#!/usr/bin/env python3
"""Test the FALSIFIABLE CORE of the 'ML RSI' indicator: does k-NN on RSI-derived features
predict the next-horizon move direction better than the base rate, OUT-OF-SAMPLE?

Lean faithful port of the engine: 8 RSI features, bank of (features -> forward outcome),
k=8 nearest neighbours by weighted log-distance, distance-weighted vote -> predicted direction.
Equal feature weights (the script's Fisher auto-weighting is a refinement; if the core has no
edge, reweighting won't manufacture one). Measures directional hit-rate vs base rate, full + OOS.
"""
import json, sys, math

PAIR = sys.argv[1] if len(sys.argv) > 1 else "BTCEUR"
d = json.load(open(f"/tmp/bt_{PAIR}.json")); k = [x for x in d if x != "last"][0]
rows = d[k]
C = [float(r[4]) for r in rows]; H = [float(r[2]) for r in rows]; Lo = [float(r[3]) for r in rows]
n = len(C)

def rsi(cl, p):
    out = [50.0]*len(cl)
    if len(cl) <= p: return out
    g = l = 0.0
    for i in range(1, p+1):
        ch = cl[i]-cl[i-1]; g += max(ch,0); l += max(-ch,0)
    ag, al = g/p, l/p
    out[p] = 100 - 100/(1+(ag/al if al else 1e9))
    for i in range(p+1, len(cl)):
        ch = cl[i]-cl[i-1]
        ag = (ag*(p-1)+max(ch,0))/p; al = (al*(p-1)+max(-ch,0))/p
        out[i] = 100 - 100/(1+(ag/al if al else 1e9))
    return out

R, RF, RS = rsi(C,14), rsi(C,7), rsi(C,28)
# ATR14 and rsi stdev / ema
TR = [0.0]+[max(H[i]-Lo[i], abs(H[i]-C[i-1]), abs(Lo[i]-C[i-1])) for i in range(1,n)]
ATR = [sum(TR[max(1,i-13):i+1])/min(14,i) if i else 0 for i in range(n)]
def ema(v,p):
    kk=2/(p+1); o=[v[0]]
    for x in v[1:]: o.append(x*kk+o[-1]*(1-kk))
    return o
REMA = ema(R,20)
STD = [0.0]*n
for i in range(14,n):
    w=R[i-13:i+1]; m=sum(w)/14; STD[i]=(sum((x-m)**2 for x in w)/14)**0.5

WIN=100; STEP=3; HOR=4; AF=0.5
slope=[0.0]*n; accel=[0.0]*n; spread=[0.0]*n; reg=[0.0]*n
for i in range(n):
    if i>=2*STEP:
        slope[i]=R[i]-R[i-STEP]; accel[i]=(R[i]-R[i-STEP])-(R[i-STEP]-R[i-2*STEP])
    spread[i]=RF[i]-RS[i]; reg[i]=REMA[i]-50
def sc(series,i):
    w=series[i-WIN+1:i+1]; lo=min(w); hi=max(w)
    return 0.5 if hi==lo else (series[i]-lo)/(hi-lo)
def pr(series,i):
    w=series[i-WIN+1:i+1]; return sum(1 for x in w if x<=series[i])/len(w)

feat=[None]*n
for i in range(n):
    if i<WIN+2*STEP: continue
    feat[i]=(R[i]/100.0, sc(slope,i), sc(accel,i), abs(R[i]-50)/50.0,
             pr(R,i), sc(STD,i), sc(spread,i), sc(reg,i))

def outcome(i):
    if i+HOR>=n: return None
    mv=C[i+HOR]-C[i]; band=AF*ATR[i]
    return 1 if mv>band else (-1 if mv<-band else 0)

def comp(a,b): return math.log(1+abs(a-b))
def dist(fa,fb): return sum(comp(fa[j],fb[j]) for j in range(8))

# walk forward: predict each bar from a bank of prior, outcome-known bars (memory 500, spacing 4)
MEM=500; SP=4; K=8
preds=[]  # (idx, predicted_dir, actual_sign)
start=WIN+2*STEP+HOR+20
for i in range(start, n-HOR):
    if feat[i] is None: continue
    # bank: bars j with known outcome (j+HOR <= i), spaced, most recent MEM
    cand=[]
    j=i-HOR
    while j>=start-20 and len(cand)<MEM*SP:
        if feat[j] is not None and j%SP==0:
            o=outcome(j)
            if o is not None and o!=0:
                cand.append((dist(feat[i],feat[j]), 1 if o>0 else -1))
        j-=1
    if len(cand)<K: continue
    cand.sort(key=lambda x:x[0])
    nn=cand[:K]
    tot=bull=bear=0.0
    for g,cls in nn:
        w=1/(1+g)
        if cls>0: bull+=w
        else: bear+=w
        tot+=w
    score=(bull-bear)/tot if tot else 0
    pdir = 1 if score>0.15 else (-1 if score<-0.15 else 0)
    if pdir==0: continue
    actual = 1 if C[i+HOR]>C[i] else -1
    preds.append((i, pdir, actual))

def report(name, subset):
    if not subset:
        print(f"  {name}: no predictions"); return
    hits=sum(1 for _,p,a in subset if p==a)
    base_up=sum(1 for _,_,a in subset if a==1)/len(subset)
    base=max(base_up,1-base_up)  # always-guess-majority baseline
    acc=hits/len(subset)
    print(f"  {name}: {len(subset)} preds | hit-rate {acc*100:.1f}% | "
          f"base(majority) {base*100:.1f}% | edge {(acc-base)*100:+.1f} pts")

split=int(n*0.6)
print(f"=== ML-RSI core kNN directional test: {PAIR} ({n} bars, horizon {HOR}) ===")
report("FULL period", preds)
report("IN-SAMPLE (first 60%)", [p for p in preds if p[0]<split])
report("OUT-OF-SAMPLE (last 40%)", [p for p in preds if p[0]>=split])
print("  (edge > 0 means the kNN beats blindly guessing the majority direction)")
