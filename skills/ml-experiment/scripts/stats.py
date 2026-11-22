#!/usr/bin/env python3
"""Uncertainty for ML comparisons, stdlib only. Use it before claiming one arm beat another.

  stats.py paired --a A.jsonl --b B.jsonl [--id-field id] [--score-field correct] [--cluster-field group]
                  [--min-effect 0.02] [--n-boot 10000] [--seed 0]
      Aligns two arms on shared item ids and reports mean A, mean B, the paired difference (B - A) with
      a 95% bootstrap interval (resampling clusters when --cluster-field is given, e.g. one source
      document with several questions), and for 0/1 scores the exact McNemar test on discordant items.
      Items present in only one arm are counted and reported, never silently dropped. With
      --cluster-field, both arms must carry the same non-empty cluster id for every item; under 5
      clusters the effect is reported but no inference is made, and McNemar (which assumes
      independent items) is not run. --min-effect is the smallest difference worth acting on, from
      the plan: "better" then means the whole interval clears it.
  stats.py mde --n 404 --p 0.71 [--alpha 0.05] [--power 0.8] [--discordant 0.15]
      Smallest effect a test of this size can detect: unpaired two-proportion, and paired (McNemar)
      when you give the expected share of discordant items. Run it BEFORE the experiment.
  stats.py seeds 0.712 0.698 0.731 ...
      Mean, standard deviation and a t-interval across seeds (independent runs).

Files: .jsonl (one object per line) or .json (a list). Scores may be bools, 0/1 or any number.
Exit 0 ok, 2 bad input, 3 the arms do not share the same item set (result printed, but flagged).
"""
import argparse
import json
import math
import random
import statistics
import sys

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
       12: 2.179, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}


def t_crit(df):
    keys = sorted(T95)
    for k in keys:
        if df <= k:
            return T95[k]
    return 1.96


def z(p):
    """Inverse standard normal CDF (Acklam's approximation, error < 1e-8 in the range used here)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - 0.02425:
        return -z(1 - p)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def load(path, idf, sf, cf):
    try:
        text = open(path).read()
        rows = json.loads(text) if path.endswith(".json") else [json.loads(l) for l in text.splitlines() if l.strip()]
    except (OSError, ValueError) as e:
        sys.exit(print(f"cannot read {path}: {e}", file=sys.stderr) or 2)
    out = {}
    for n, r in enumerate(rows, 1):
        if idf not in r or sf not in r:
            sys.exit(print(f"{path} row {n}: missing {idf!r} or {sf!r}", file=sys.stderr) or 2)
        v = r[sf]
        if isinstance(v, bool):
            v = int(v)
        if not isinstance(v, (int, float)) or not math.isfinite(v):
            sys.exit(print(f"{path} row {n}: score {v!r} is not a finite number", file=sys.stderr) or 2)
        if r[idf] in out:
            sys.exit(print(f"{path}: duplicate id {r[idf]!r}", file=sys.stderr) or 2)
        if cf:
            cl = r.get(cf)
            if cl is None or str(cl).strip() == "":
                sys.exit(print(f"{path} row {n}: cluster field {cf!r} missing or empty", file=sys.stderr) or 2)
        out[r[idf]] = (float(v), r.get(cf) if cf else r[idf])
    return out


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def cmd_paired(a):
    A = load(a.a, a.id_field, a.score_field, a.cluster_field)
    B = load(a.b, a.id_field, a.score_field, a.cluster_field)
    shared = sorted(set(A) & set(B), key=str)
    only_a, only_b = len(set(A) - set(B)), len(set(B) - set(A))
    if not shared:
        print("no shared item ids between the arms", file=sys.stderr)
        return 2
    if a.n_boot < 1000:
        print("--n-boot must be at least 1000", file=sys.stderr)
        return 2
    if a.cluster_field:
        clash = [i for i in shared if str(A[i][1]) != str(B[i][1])]
        if clash:
            print(f"cluster ids differ between arms for {len(clash)} item(s), e.g. {clash[0]!r}", file=sys.stderr)
            return 2
    diffs = {i: B[i][0] - A[i][0] for i in shared}
    clusters = {}
    for i in shared:
        clusters.setdefault(A[i][1], []).append(i)
    keys = list(clusters)
    rng = random.Random(a.seed)
    boots = []
    for _ in range(a.n_boot):
        pick = [keys[rng.randrange(len(keys))] for _ in keys]
        items = [i for k in pick for i in clusters[k]]
        boots.append(sum(diffs[i] for i in items) / len(items))
    boots.sort()
    lo, hi = boots[int(0.025 * a.n_boot)], boots[min(a.n_boot - 1, int(0.975 * a.n_boot))]
    ma = statistics.fmean(A[i][0] for i in shared)
    mb = statistics.fmean(B[i][0] for i in shared)
    print(f"items shared {len(shared)}; only in A {only_a}; only in B {only_b}; clusters {len(keys)}")
    print(f"mean A {ma:.4f}   mean B {mb:.4f}   paired diff (B - A) {mb - ma:+.4f}   95% bootstrap CI [{lo:+.4f}, {hi:+.4f}]")
    binary = all(A[i][0] in (0.0, 1.0) and B[i][0] in (0.0, 1.0) for i in shared)
    if a.cluster_field and len(keys) < 5:
        print(f"reading: inconclusive. Only {len(keys)} independent cluster(s): no interval or test supports inference.")
        return 3 if (only_a or only_b) else 0
    if a.cluster_field and len(keys) < 20:
        print(f"WARN: {len(keys)} clusters; the cluster bootstrap interval is unstable below about 20.")
    if binary and not a.cluster_field:
        b_ = sum(1 for i in shared if A[i][0] == 1 and B[i][0] == 0)
        c_ = sum(1 for i in shared if A[i][0] == 0 and B[i][0] == 1)
        print(f"McNemar exact: A right/B wrong {b_}, A wrong/B right {c_}, two-sided p = {mcnemar_exact(b_, c_):.4g}")
    m = a.min_effect
    if lo > m:
        verdict = "B better" + (f" by at least the meaningful effect {m}" if m else "")
    elif hi < -m:
        verdict = "A better" + (f" by at least the meaningful effect {m}" if m else "")
    elif lo > 0 or hi < 0:
        verdict = f"a nonzero difference that may be smaller than the meaningful effect {m}" if m else "nonzero"
    else:
        verdict = "inconclusive (the interval includes 0)"
    print(f"reading: {verdict}. The interval covers item sampling only, not seed or prompt variance.")
    if only_a or only_b:
        print("FLAG: the arms were scored on different item sets; fix that before comparing.")
        return 3
    return 0


def cmd_mde(a):
    if a.n <= 0 or not (0 < a.alpha < 1) or not (0 < a.power < 1):
        print("need --n > 0, 0 < alpha < 1, 0 < power < 1", file=sys.stderr)
        return 2
    if not (0 < a.p < 1):
        print("baseline p at 0 or 1: the normal approximation is unavailable; plan from pilot variance instead", file=sys.stderr)
        return 2
    if a.discordant is not None and not (0 < a.discordant <= 1):
        print("--discordant must be in (0, 1]", file=sys.stderr)
        return 2
    za, zb = z(1 - a.alpha / 2), z(a.power)
    p = a.p
    unpaired = (za + zb) * math.sqrt(2 * p * (1 - p) / a.n)
    print(f"n {a.n}, baseline {p:.3f}, alpha {a.alpha}, power {a.power}")
    print(f"unpaired two-proportion MDE ~ {unpaired:.4f} ({unpaired * 100:.1f} points)")
    if a.discordant:
        paired = (za + zb) * math.sqrt(a.discordant / a.n)
        print(f"paired (McNemar, {a.discordant:.0%} discordant) MDE ~ {paired:.4f} ({paired * 100:.1f} points)")
    print("Independent binary outcomes only. For continuous or clustered outcomes, estimate power at the")
    print("independent unit from pilot variance. A smaller true effect will usually read as inconclusive.")
    return 0


def cmd_seeds(a):
    v = a.values
    if not all(math.isfinite(x) for x in v):
        print("seed values must be finite numbers", file=sys.stderr)
        return 2
    if len(v) < 2:
        print("need 2+ seed values", file=sys.stderr)
        return 2
    m, s = statistics.fmean(v), statistics.stdev(v)
    h = t_crit(len(v) - 1) * s / math.sqrt(len(v))
    print(f"seeds {len(v)}: mean {m:.4f}, sd {s:.4f}, 95% t-interval [{m - h:.4f}, {m + h:.4f}], range {min(v):.4f} to {max(v):.4f}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("paired")
    s.add_argument("--a", required=True); s.add_argument("--b", required=True)
    s.add_argument("--id-field", default="id"); s.add_argument("--score-field", default="correct")
    s.add_argument("--cluster-field"); s.add_argument("--min-effect", type=float, default=0.0)
    s.add_argument("--n-boot", type=int, default=10000); s.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("mde")
    s.add_argument("--n", type=int, required=True); s.add_argument("--p", type=float, required=True)
    s.add_argument("--alpha", type=float, default=0.05); s.add_argument("--power", type=float, default=0.8)
    s.add_argument("--discordant", type=float)
    s = sub.add_parser("seeds")
    s.add_argument("values", type=float, nargs="+")
    a = ap.parse_args()
    return {"paired": cmd_paired, "mde": cmd_mde, "seeds": cmd_seeds}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
