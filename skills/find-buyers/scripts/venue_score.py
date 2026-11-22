#!/usr/bin/env python3
"""Score buyer venues from an evidence ledger, so rankings come from counted posts, not impressions.

  venue_score.py --ledger buyers.jsonl --venues venues.jsonl [--today 2026-11-19] [--window-days 365] [--json scores.json]

buyers.jsonl: one row per opened post that shows a buyer episode
  {"venue": "r/bookkeeping", "buyer": "u/some_user" or "org:acme", "rung": 3, "date": "2026-10-02",
   "url": "<permalink>", "firsthand": true, "role_fit": 2, "quote": "<their words>"}
  rung: 0 seller or advice, 1 first-hand pain, 2 costly workaround, 3 active search or switching,
        4 budget, trial or demo, 5 documented purchase or migration
  role_fit: 0 wrong role, 1 adjacent, 2 likely buyer, 3 exact buyer role (judged from the post)
venues.jsonl: one row per venue
  {"venue": "r/bookkeeping", "rules_url": "...", "rules_checked": "2026-11-19", "rules_source": "live",
   "permission": "allowed" | "prohibited" | "unknown", "rules_excerpt": "<the rule text that permits it>",
   "allowed_action": "answer questions with disclosure; weekly promo thread", "opened": 40}

Score (0 to 10) = fit (0-3) + intent (0-3) + recency (0-2) + reach (0-2), per references/query-bank.md:
  fit      median role_fit of distinct first-hand buyers (0 when none)
  intent   3 if >= 3 distinct buyers at rung >= 3; 2 if >= 1 at rung >= 3 or >= 3 at rung 2; 1 if any rung >= 1; else 0
  recency  2 if any rung >= 2 within 90 days; 1 if within the window; else 0
  reach    0 unless rules were checked live (rules_source "live" and a date); then 2 if an allowed action is
           named, 1 if the rules allow only passive reading or the action is unclear
A reviewer must still confirm that the cited rule allows the exact action planned.
A venue is ELIGIBLE for an experiment only with a live rule receipt (rules_url, rules_checked date,
rules_excerpt), permission "allowed", a named allowed action (reach 2) and intent >= 2. One qualifying
buyer justifies one permitted reply at most; a channel test needs intent 3 (three distinct buyers at rung 3+).
Exit 0 ok, 2 bad input. Rows are keyed by canonical permalink: identical repeats merge, but one
permalink coded with two buyers or two codings is an input error (one post is one buyer). One buyer
counts once per venue. allowed_action is the one permitted active action ("" for read-only venues).
Rows may carry "segment"; a ledger mixing segments needs --segment (one scoring run per segment).
"""
import argparse
import datetime as dt
import json
import statistics
import sys


def load(path, need):
    rows = []
    for n, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError as e:
            sys.exit(print(f"INPUT ERROR {path}:{n}: {e}", file=sys.stderr) or 2)
        miss = [k for k in need if k not in r]
        if miss:
            sys.exit(print(f"INPUT ERROR {path}:{n}: missing {miss}", file=sys.stderr) or 2)
        rows.append(r)
    return rows


def validate_buyer(r, n):
    errs = []
    if not isinstance(r["rung"], int) or isinstance(r["rung"], bool) or not 0 <= r["rung"] <= 5:
        errs.append("rung must be an integer 0-5")
    if not isinstance(r["role_fit"], int) or isinstance(r["role_fit"], bool) or not 0 <= r["role_fit"] <= 3:
        errs.append("role_fit must be an integer 0-3")
    if not isinstance(r["firsthand"], bool):
        errs.append("firsthand must be true or false (JSON boolean)")
    if not str(r["url"]).startswith("http"):
        errs.append("url must be the post's permalink")
    if not str(r.get("quote", "")).strip():
        errs.append("quote (the buyer's own words) is required")
    try:
        dt.date.fromisoformat(str(r["date"])[:10])
    except ValueError:
        errs.append("date must be YYYY-MM-DD")
    if errs:
        sys.exit(print(f"INPUT ERROR ledger row {n}: " + "; ".join(errs), file=sys.stderr) or 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--venues", required=True)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--window-days", type=int, default=365)
    ap.add_argument("--json", help="also write the rows as JSON (gtm_check.py reads this)")
    ap.add_argument("--segment", help="score only ledger rows with this segment")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today)
    ledger = load(a.ledger, ["venue", "buyer", "rung", "date", "url", "firsthand", "role_fit"])
    for n, r in enumerate(ledger, 1):
        validate_buyer(r, n)
    segs = {r.get("segment") for r in ledger}
    if a.segment:
        ledger = [r for r in ledger if r.get("segment") == a.segment]
    elif len(segs) > 1:
        sys.exit(print(f"INPUT ERROR: the ledger mixes segments {sorted(map(str, segs))}; run once per --segment", file=sys.stderr) or 2)
    venues = {v["venue"]: v for v in load(a.venues, ["venue"])}
    for name, v in venues.items():
        act = v.get("allowed_action", "")
        if act is not None and not isinstance(act, str):
            sys.exit(print(f"INPUT ERROR venue {name}: allowed_action must be a string", file=sys.stderr) or 2)
    canon = lambda u: str(u).split("?")[0].split("#")[0].rstrip("/").lower()
    by_url, by_venue = {}, {}
    for r in ledger:
        key = canon(r["url"])
        coding = (r["venue"], r["buyer"], int(r["rung"]), int(r["role_fit"]), bool(r["firsthand"]), str(r["date"])[:10])
        if key in by_url:
            if by_url[key] != coding:
                sys.exit(print(f"INPUT ERROR: {r['url']} is coded twice differently {by_url[key]} vs {coding}; one post is one buyer", file=sys.stderr) or 2)
            continue
        by_url[key] = coding
        if not r["firsthand"] or int(r["rung"]) < 1 or int(r["role_fit"]) < 2:
            continue  # only first-hand posts from a likely or exact buyer role count
        age = (today - dt.date.fromisoformat(r["date"][:10])).days
        if age > a.window_days or age < 0:
            continue
        b = by_venue.setdefault(r["venue"], {}).setdefault(r["buyer"], {"rung": 0, "fit": 0, "age": 10**6, "urls": []})
        if int(r["rung"]) > b["rung"] or not b.get("best_url"):
            b["best_url"] = r["url"]  # the link that proves this buyer's highest rung, kept with it
        b["rung"] = max(b["rung"], int(r["rung"]))
        b["fit"] = max(b["fit"], int(r["role_fit"]))
        if int(r["rung"]) >= 2:
            b["age"] = min(b["age"], age)
        b["urls"].append(r["url"])
    rows = []
    for name in sorted(set(venues) | set(by_venue)):
        buyers = by_venue.get(name, {})
        v = venues.get(name, {})
        rungs = [b["rung"] for b in buyers.values()]
        fit = int(statistics.median([b["fit"] for b in buyers.values()])) if buyers else 0
        n3 = sum(r >= 3 for r in rungs)
        n2 = sum(r == 2 for r in rungs)
        intent = 3 if n3 >= 3 else 2 if (n3 >= 1 or n2 >= 3) else 1 if rungs else 0
        ages = [b["age"] for b in buyers.values() if b["age"] < 10**6]
        recency = 2 if ages and min(ages) <= 90 else 1 if ages else 0
        try:
            checked = dt.date.fromisoformat(str(v.get("rules_checked", ""))[:10])
        except ValueError:
            checked = None
        perm = v.get("permission", "unknown")
        if perm not in ("allowed", "prohibited", "unknown"):
            sys.exit(print(f"INPUT ERROR venue {name}: permission must be allowed, prohibited or unknown", file=sys.stderr) or 2)
        if checked is not None and (checked > today or (today - checked).days > 30):
            checked = None  # a future date or a check older than 30 days is not a live receipt
        live = (v.get("rules_source") == "live" and checked is not None and str(v.get("rules_url", "")).startswith("http")
                and bool(str(v.get("rules_excerpt", "")).strip()))
        action = (v.get("allowed_action") or "").strip()
        reach = 0 if not live or perm != "allowed" else (2 if action else 1)
        reply_ok = live and reach >= 2 and n3 >= 1      # one qualifying buyer: one permitted reply
        eligible = live and reach >= 2 and intent >= 3  # channel test: three distinct qualifying buyers
        ladder = {k: sum(r == k for r in rungs) for k in range(1, 6)}
        receipt = f"{perm}, checked {checked} at {v.get('rules_url', '?')}" if live else f"{perm} (no live rule receipt)"
        per_buyer = [f"{b['best_url']} (rung {b['rung']})" for _, b in sorted(buyers.items(), key=lambda kv: -kv[1]["rung"])]
        evidence = [{"buyer": k, "url": b["best_url"], "rung": b["rung"]} for k, b in buyers.items()]
        rows.append((fit + intent + recency + reach, name, fit, intent, recency, reach, len(buyers), ladder,
                     v.get("opened"), ("channel test" if eligible else "reply only" if reply_ok else "no"), receipt, action, per_buyer[:3], evidence))
    rows.sort(key=lambda x: (-x[0], x[1]))
    print("| venue | score | fit | intent | recency | reach | qualifying buyers | rungs 1-5 | opened | decision | rule receipt | allowed action | one link per buyer |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s, name, fit, intent, rec, reach, nb, ladder, opened, el, rules, action, urls, _ev in rows:
        print(f"| {name} | {s} | {fit} | {intent} | {rec} | {reach} | {nb} | {'/'.join(str(ladder[k]) for k in range(1, 6))} | "
              f"{opened if opened is not None else '?'} | {el} | {rules} | {action or '-'} | {' '.join(urls)} |")
    if a.json:
        out = [{"venue": name, "score": s, "fit": fit, "intent": intent, "recency": rec, "reach": reach,
                "qualifying_buyers": nb, "rungs": ladder, "opened": opened, "decision": el, "rule_receipt": rules,
                "allowed_action": action, "rules_excerpt": venues.get(name, {}).get("rules_excerpt", ""),
                "links": urls, "evidence": ev, "segment": a.segment or next(iter(segs), None), "scored": a.today}
               for s, name, fit, intent, rec, reach, nb, ladder, opened, el, rules, action, urls, ev in rows]
        with open(a.json, "w") as f:
            json.dump(out, f, indent=1)
    print(f"\n{sum(1 for r in rows if r[9] == 'channel test')} of {len(rows)} venues qualify for a channel test. Scores compare venues only within similar "
          "sampling depth (see 'opened'); they are evidence bands, not conversion rates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
