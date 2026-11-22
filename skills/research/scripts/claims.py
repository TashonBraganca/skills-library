#!/usr/bin/env python3
"""Check that every number in a report comes from the result it claims to describe.

In agent-written research, most unsupported numbers are real values taken from the wrong
experiment, arm, split, metric or run (arXiv 2610.38691: about four in five in its labeled sample).
A citation to the right paper or file does not catch that. This checker matches each claimed number
to its evidence row by the full tuple, and flags a value that matches some other row instead.

  claims.py check --claims claims.jsonl --evidence evidence.jsonl
  claims.py untagged report.md                      # numbers in prose with no [c:ID] tag

evidence.jsonl, one row per measured value you opened (a table cell, a log line, a JSON field):
  {"evidence_id": "e1", "source": "https://arxiv.org/abs/2504.07086v2", "locator": "Table 3",
   "experiment": "aime24", "arm": "grpo", "split": "test", "metric": "pass@1", "unit": "%", "value": 43.3}
claims.jsonl, one row per number your report states:
  {"claim_id": "c1", "value": 43.3, "experiment": "aime24", "arm": "grpo", "split": "test",
   "metric": "pass@1", "unit": "%"}
All five tuple fields are required (use "n/a" when a field truly does not apply). Any extra field on
the claim (run, seed, version, locator) must equal the same field on the evidence row. "unit" is the
evidence unit; "display_unit" (optional) is how the report shows it, and the conversion is derived
(ratio -> %, s -> ms ...), never chosen. "evidence_id" (optional) must name a row whose tuple matches.
Rounding follows the decimals the claim displays.

Verdicts: VERIFIED, MISMATCH (right row, wrong value), MISATTRIBUTED (value belongs to a different
row), AMBIGUOUS (several matching rows disagree), UNSUPPORTED (no row matches the tuple).
Exit: 0 all verified, 1 any mismatch or misattribution, 2 bad input, 3 unsupported, ambiguous or untagged.
A claim this checker cannot verify is not proven false. Check it by hand.
"""
import argparse
import json
import re
import sys

KEYS = ("experiment", "arm", "split", "metric", "unit")


def load(path, id_field):
    rows = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError as e:
                sys.exit(print(f"INPUT ERROR: {path}:{n}: not JSON ({e})", file=sys.stderr) or 2)
            if id_field not in r or "value" not in r:
                sys.exit(print(f"INPUT ERROR: {path}:{n}: needs {id_field} and value", file=sys.stderr) or 2)
            try:
                r["value"] = float(r["value"])
            except (TypeError, ValueError):
                sys.exit(print(f"INPUT ERROR: {path}:{n}: value is not a number", file=sys.stderr) or 2)
            rows.append(r)
    ids = [r[id_field] for r in rows]
    if len(set(ids)) != len(ids):
        sys.exit(print(f"INPUT ERROR: {path}: duplicate {id_field}", file=sys.stderr) or 2)
    return rows


def decimals_of(v, raw):
    s = str(raw)
    return len(s.split(".")[1]) if "." in s and "e" not in s.lower() else 0


def same(claim, ev_value, scale, dec):
    return round(ev_value * scale, dec) == round(claim, dec)


CONVERT = {("ratio", "%"): 100.0, ("fraction", "%"): 100.0, ("%", "ratio"): 0.01, ("%", "fraction"): 0.01,
           ("s", "ms"): 1000.0, ("ms", "s"): 0.001, ("count", "k"): 0.001, ("k", "count"): 1000.0}
META = {"claim_id", "value", "text", "evidence_id", "note", "display_unit"}


def cmd_check(a):
    ev = load(a.evidence, "evidence_id")
    cl = load(a.claims, "claim_id")
    raw_claims = {json.loads(l)["claim_id"]: json.loads(l)["value"] for l in open(a.claims) if l.strip()}
    by_id = {e["evidence_id"]: e for e in ev}
    bad = unsure = 0
    for c in cl:
        missing = [k for k in KEYS if c.get(k) in (None, "")]
        tag = f"{c['claim_id']} = {raw_claims[c['claim_id']]}"
        if missing:
            print(f"UNSUPPORTED {tag}: incomplete tuple, missing {', '.join(missing)} (use \"n/a\" if a field does not apply)")
            unsure += 1
            continue
        if "scale" in c:
            print(f"INPUT ERROR: {c['claim_id']}: 'scale' is not allowed; give display_unit and the conversion is derived", file=sys.stderr)
            return 2
        disp = c.get("display_unit") or c["unit"]
        if disp == c["unit"]:
            scale = 1.0
        elif (c["unit"], disp) in CONVERT:
            scale = CONVERT[(c["unit"], disp)]
        else:
            print(f"INPUT ERROR: {c['claim_id']}: no defined conversion from {c['unit']} to {disp}", file=sys.stderr)
            return 2
        dec = decimals_of(c["value"], raw_claims[c["claim_id"]])
        ident = [k for k in c if k not in META]
        tag = f"{c['claim_id']} ({', '.join(f'{k}={c[k]}' for k in ident)}) = {raw_claims[c['claim_id']]}"
        match = [e for e in ev if all(str(e.get(k)) == str(c[k]) for k in ident)]
        if c.get("evidence_id"):
            named = by_id.get(c["evidence_id"])
            if named is None or named not in match:
                why = "does not exist" if named is None else "has a different tuple or identity"
                print(f"MISMATCH {tag}: named evidence {c['evidence_id']} {why}")
                bad += 1
                continue
            match = [named]
        hits = [e for e in match if same(c["value"], e["value"], scale, dec)]
        if hits and len({round(e['value'] * scale, dec) for e in match}) == 1:
            e = hits[0]
            print(f"VERIFIED {tag} <- {e['evidence_id']} {e.get('source', '')} {e.get('locator', '')}".rstrip())
            continue
        if hits:
            print(f"AMBIGUOUS {tag}: {len(match)} rows match with different values "
                  f"({', '.join(e['evidence_id'] for e in match)}); add the missing identity field (seed, run, version)")
            unsure += 1
            continue
        elsewhere = [e for e in ev if e not in match and same(c["value"], e["value"], scale, dec)]
        if match:
            vals = ", ".join(f"{e['evidence_id']}={e['value'] * scale:g}" for e in match)
            extra = f"; the stated value matches {', '.join(e['evidence_id'] for e in elsewhere)} instead" if elsewhere else ""
            print(f"MISMATCH {tag}: evidence says {vals}{extra}")
            bad += 1
        elif elsewhere:
            where = "; ".join(f"{e['evidence_id']} ({', '.join(f'{k}={e.get(k)}' for k in KEYS if e.get(k))})" for e in elsewhere)
            print(f"MISATTRIBUTED {tag}: no row has this identity; the value belongs to {where}")
            bad += 1
        else:
            print(f"UNSUPPORTED {tag}: no evidence row has this identity or value")
            unsure += 1
    print(f"\n{len(cl)} claims: {len(cl) - bad - unsure} verified, {bad} wrong, {unsure} not verifiable here")
    return 1 if bad else (3 if unsure else 0)


NUM = re.compile(r"(?<![\w.\[:/#-])(\d+(?:\.\d+)?)\s?(%|x|pp|points?|ms|s|k|M|B)?(?![\w.])")


def cmd_untagged(a):
    """List lines with empirical-looking numbers (decimals, or numbers with %, x, pp, ms, s, k, M, B)
    that carry no [c:ID] tag. Bare integer counts ("64 subjects") are not caught: check them by eye."""
    n_bad = 0
    in_code = False
    known, shown = None, {}
    if a.claims:
        rows_ = [json.loads(l) for l in open(a.claims) if l.strip()]
        known = {r["claim_id"] for r in rows_}
        shown = {r["claim_id"]: (float(r["value"]), decimals_of(r["value"], r["value"])) for r in rows_}
    for n, line in enumerate(open(a.report), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.lstrip().startswith(("#", "|---", "http")):
            continue
        # mask years, dates, versions, links and list markers without moving positions
        masked = re.sub(r"https?://\S+|\b(19|20)\d{2}(-\d{2}(-\d{2})?)?\b|\bv\d+(\.\d+)*\b|^\s*\d+\.\s|\[c:[\w.-]+\]",
                        lambda m: " " * len(m.group(0)), line)
        loose = []
        for m in NUM.finditer(masked):
            if "." not in m.group(1) and not m.group(2):
                continue
            nxt = NUM.search(masked, m.end())
            window = line[m.end(): min(m.end() + 40, nxt.start() if nxt else len(line))]
            if "[c:" not in window:
                loose.append(m.group(0))
        unknown = [t for t in re.findall(r"\[c:([\w.-]+)\]", line) if known is not None and t not in known]
        if known is not None:
            for m in re.finditer(r"(\d+(?:\.\d+)?)\s?(%|x|pp|ms|s|k|M|B)?[^\d\[]{0,40}\[c:([\w.-]+)\]", line):
                cid = m.group(3)
                if cid in known and cid in shown:
                    val, d = shown[cid]
                    if round(float(m.group(1)), d) != round(val, d):
                        unknown.append(f"{cid} says {m.group(1)} but the claim row says {val:g}")
        if loose or unknown:
            n_bad += 1
            msg = ", ".join(loose[:6]) + (f" tag problems: {'; '.join(unknown)}" if unknown else "")
            print(f"{a.report}:{n}: {msg} | {line.strip()[:140]}")
    print(f"\n{n_bad} line(s) state numbers with no claim tag" if n_bad else "every empirical-looking number is tagged")
    return 3 if n_bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="match claims to evidence rows by full tuple")
    c.add_argument("--claims", required=True)
    c.add_argument("--evidence", required=True)
    c.set_defaults(fn=cmd_check)
    u = sub.add_parser("untagged", help="numbers in a Markdown report with no [c:ID] tag")
    u.add_argument("report")
    u.add_argument("--claims", help="claims.jsonl: also flag tags that name no claim")
    u.set_defaults(fn=cmd_untagged)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
