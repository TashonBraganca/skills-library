#!/usr/bin/env python3
"""Hard gates for the gtm skill: no plan without evidence, no experiment without a receipt.

  gtm_check.py inputs --brief gtm/company/brief.md --report gtm/research/<report>.md
                      --report-brief gtm/research/brief.md --scores gtm/buyers/scores.json [--max-age-days 30]
      Passes only when: the intake brief answers all six fields (an unknown answer is written
      "unavailable"); the research report passes research/scripts/report_check.py against its brief;
      and scores.json (venue_score.py --json) has 1+ venue scored within the age limit.
  gtm_check.py plan --plan gtm/strategy/plan.md --scores gtm/buyers/scores.json
      Every row of the experiments table, whose header must hold these columns:
        | venue | exact action | success event | sample size | stop rule | buyer links |
      passes only when its venue is scored "channel test", its 3+ buyer links are the evidence URLs of
      3+ distinct qualifying buyers (rung 3+) in that venue's scores, and the sample size and stop rule
      hold numbers. The plan also needs a "Why this could fail" section with 2+ items. This is a
      STRUCTURE PASS: for each row it prints the venue's allowed action and rule excerpt next to the
      planned action, and a person must confirm the rule allows that exact action.

Exit 0 pass, 1 a gate failed (fix it or run the missing skill), 2 bad input.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

BRIEF_FIELDS = ["Sells", "Buyer", "Problems", "Usable results", "Track", "Never mention"]
REPORT_CHECK = os.path.expanduser("~/.skills-library/skills/research/scripts/report_check.py")
URL_RE = re.compile(r"https?://[^\s)|>\]]+")


def cmd_inputs(a):
    fails = []
    try:
        brief = open(a.brief, encoding="utf-8").read()
        for f in BRIEF_FIELDS:
            m = re.search(r"^\s*[-*]?\s*\**" + re.escape(f) + r"\**\s*:\s*(.+)$", brief, re.I | re.M)
            if not m or len(m.group(1).strip()) < 3:
                fails.append(f"brief: field '{f}:' missing or empty (write 'unavailable' if unknown)")
    except OSError:
        fails.append(f"{a.brief}: missing. Run gtm step 1 (intake).")
    p = subprocess.run([sys.executable, REPORT_CHECK, a.report, "--brief", a.report_brief], capture_output=True, text=True)
    if p.returncode not in (0, 3):
        fails.append(f"research report fails report_check.py (exit {p.returncode}): " + " | ".join(
            l for l in p.stdout.splitlines() if l.startswith("FAIL"))[:400])
    try:
        rows = json.load(open(a.scores))
        dates = {str(r.get("scored", ""))[:10] for r in rows}
        if not rows:
            fails.append(f"{a.scores}: no venues scored. Run find-buyers (gtm step 3).")
        for d in dates:
            try:
                age = (dt.date.today() - dt.date.fromisoformat(d)).days
            except ValueError:
                fails.append(f"{a.scores}: no valid 'scored' date; re-run venue_score.py --json")
                break
            if age > a.max_age_days:
                fails.append(f"{a.scores}: scored {age} days ago (limit {a.max_age_days}). Re-run find-buyers.")
        if rows and not fails:
            print(f"scores: {len(rows)} venues, {sum(r.get('decision') == 'channel test' for r in rows)} eligible for a channel test")
    except (OSError, json.JSONDecodeError, TypeError, AttributeError):
        fails.append(f"{a.scores}: missing or unreadable. Run find-buyers and venue_score.py --json (gtm step 3).")
    for f in fails:
        print("FAIL " + f)
    if not fails:
        print("PASS inputs: brief, research report, venue scores")
    return 1 if fails else 0


def table_rows(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if "venue" in cells and any("stop" in c for c in cells) and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            idx = {name: next((k for k, c in enumerate(cells) if name in c), None)
                   for name in ("venue", "action", "success", "sample", "stop", "link")}
            out = []
            for row in lines[i + 2:]:
                if not row.strip().startswith("|"):
                    break
                out.append([c.strip() for c in row.strip().strip("|").split("|")])
            return idx, out
    return None, []


def cmd_plan(a):
    try:
        text = open(a.plan, encoding="utf-8").read()
        scores = {r["venue"].lower(): r for r in json.load(open(a.scores))}
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"bad input: {e}", file=sys.stderr)
        return 2
    fails = []
    idx, rows = table_rows(text)
    if idx is None:
        fails.append("no experiments table with 'venue' and 'stop rule' columns")
        rows = []
    missing_cols = [k for k, v in (idx or {}).items() if v is None]
    if missing_cols:
        fails.append(f"experiments table lacks columns: {missing_cols}")
    canon = lambda u: u.split("?")[0].split("#")[0].rstrip("/").lower()
    for row in rows if not missing_cols else []:
        get = lambda k: row[idx[k]] if idx[k] is not None and idx[k] < len(row) else ""
        venue = get("venue").strip("` ").lower()
        sc = scores.get(venue)
        tag = f"row '{get('venue')}'"
        if not sc:
            fails.append(f"{tag}: venue not in the find-buyers scores")
            continue
        if sc.get("decision") != "channel test":
            fails.append(f"{tag}: venue decision is '{sc.get('decision')}', not 'channel test' (a reply-only venue is not a channel)")
        qualifying = {canon(e["url"]): e["buyer"] for e in sc.get("evidence", []) if e.get("rung", 0) >= 3}
        cited = {canon(u) for u in URL_RE.findall(get("link"))}
        matched = {qualifying[u] for u in cited if u in qualifying}
        stray = [u for u in cited if u not in qualifying]
        if len(matched) < 3:
            fails.append(f"{tag}: {len(matched)} buyer link(s) match distinct qualifying buyers in the scores (need 3)")
        if stray:
            fails.append(f"{tag}: {len(stray)} link(s) are not qualifying buyer evidence for this venue")
        if not get("success") or get("success") in ("-", "?"):
            fails.append(f"{tag}: 'success event' is empty")
        for k in ("sample", "stop"):
            if not re.search(r"\d", get(k)):
                fails.append(f"{tag}: '{k}' has no number")
        print(f"CONFIRM {get('venue')}: planned '{get('action')}' | venue allows '{sc.get('allowed_action', '')}' | "
              f"rule: \"{(sc.get('rules_excerpt') or '')[:140]}\"")
    m = re.search(r"^#+\s*why this could fail\s*$(.*?)(?=^#+\s|\Z)", text, re.I | re.M | re.S)
    items = re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", m.group(1), re.M) if m else []
    if len(items) < 2:
        fails.append("no 'Why this could fail' section with 2+ items")
    for f in fails:
        print("FAIL " + f)
    if not fails:
        print(f"STRUCTURE PASS: {len(rows)} experiment(s). Now confirm each CONFIRM line against the rule text.")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("inputs")
    s.add_argument("--brief", required=True); s.add_argument("--report", required=True)
    s.add_argument("--report-brief", required=True); s.add_argument("--scores", required=True)
    s.add_argument("--max-age-days", type=int, default=30)
    s = sub.add_parser("plan")
    s.add_argument("--plan", required=True)
    s.add_argument("--scores", required=True)
    a = ap.parse_args()
    return cmd_inputs(a) if a.cmd == "inputs" else cmd_plan(a)


if __name__ == "__main__":
    sys.exit(main())
