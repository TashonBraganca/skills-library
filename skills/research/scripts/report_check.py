#!/usr/bin/env python3
"""Gate a saved research report's structure and evidence links before it is handed over.

  report_check.py <report.md> --brief brief.md [--depth standard|deep --log log.md]
                  [--claims claims.jsonl --evidence evidence.jsonl]

It checks structure and links, not truth: a writer can still invent a passage and its locator.
Reopening the source for every decisive claim is the check that catches that (SKILL.md section 7).

FAIL (exit 1):
  - no per-ask table ("Did we answer what was asked"), a row naming more or fewer than one ask id,
    row ids that differ from the brief, a field status other than match/mismatch/unknown/n/a, n/a in a
    field the brief does not mark "[optional: <field>]", or an ask closed as answered with a mismatched
    or unknown field (or without outcome and evidence type matching)
  - an answered ask with no supporting register row: the row's ask cell names the id, its stance is
    supports, and it has a URL, a locator and an excerpt or value
  - a URL anywhere in the reader-facing part (everything above the audit-trail rule) that is not in
    the evidence register
  - no evidence register table with the columns id, ask, URL, locator, excerpt or value, stance
  - no null-results or coverage section
  - --claims without --evidence, or claims.py check reporting a mismatch or misattribution
  --depth deep (needs --log): 3+ round blocks with unique numbers, each with "Queries run:" and
  "Register rows added:" (ids that exist in the register, or "none (<reason>)"); fewer rounds pass
  only with a final "Decision: stop (<reason>)". A Refute pass row (unique, complete, with a verdict)
  naming each answered ask id. A "Strongest case against" with at least one item. A register row
  whose stance cell is contradicts, or a null-results line quoting the query that looked for one.
WARN (exit 3 when only warnings): untagged numbers (claims.py untagged); no confidence word in the
Answer; fewer than 20 register sources on a deep report.
Exit 0 structure passed, 2 bad input.
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
URL_RE = re.compile(r"https?://[^\s)\]>|]+")
STATUS = ("match", "mismatch", "unknown", "n/a")
FIELDS = ("outcome", "population", "comparator", "constraints", "evidence type")


def section(text, *names):
    for n in names:
        m = re.search(r"^#{1,3}\s*" + n + r".*?$(.*?)(?=^#{1,3}\s|\Z)", text, re.M | re.S | re.I)
        if m:
            return m.group(1)
    return None


def table(text):
    """(header cells lowercased, list of row cell lists) of the first Markdown table in text."""
    lines = [l for l in (text or "").splitlines() if l.strip().startswith("|")]
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines
            if not re.match(r"^\|\s*[-:| ]+\|?\s*$", l.strip())]
    if not rows:
        return [], []
    return [h.lower() for h in rows[0]], rows[1:]


def col(header, *names):
    for i, h in enumerate(header):
        if any(n in h for n in names):
            return i
    return None


def urls(text):
    return {u.rstrip(".,;") for u in URL_RE.findall(text or "")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--brief", help="brief with ask ids written as Q1:, Q2: ...")
    ap.add_argument("--no-brief", action="store_true", help="single-ask report with no separate brief")
    ap.add_argument("--claims"); ap.add_argument("--evidence")
    ap.add_argument("--depth", choices=["standard", "deep"], default="standard")
    ap.add_argument("--log", help="the research round log (required for --depth deep)")
    a = ap.parse_args()
    try:
        text = open(a.report).read()
        brief_text = open(a.brief).read() if a.brief else ""
    except OSError as e:
        print(f"INPUT ERROR: {e}")
        return 2
    if a.claims and not a.evidence:
        print("INPUT ERROR: --claims needs --evidence (the rows the numbers came from)")
        return 2
    fails, warns = [], []

    # reader-facing part: everything above the audit-trail rule or heading
    cut = re.search(r"^(?:---\s*$|#{1,2}\s*Appendix|#{1,2}\s*Audit trail)", text, re.M | re.I)
    reader = text[:cut.start()] if cut else (section(text, r"Answer") or "")

    # evidence register, parsed by column
    register = section(text, r"Evidence register", r"Evidence", r"Sources")
    header, reg_rows = table(register)
    c_id, c_ask, c_url = col(header, "id"), col(header, "ask", "question"), col(header, "url", "source")
    c_loc, c_exc, c_stance = col(header, "locator"), col(header, "excerpt", "value"), col(header, "stance")
    if register is None or not reg_rows:
        fails.append("no evidence register table")
    missing = [n for n, c in (("id", c_id), ("ask", c_ask), ("URL", c_url), ("locator", c_loc),
                              ("excerpt or value", c_exc), ("stance", c_stance)) if c is None]
    if register is not None and missing:
        fails.append(f"the evidence register lacks columns: {', '.join(missing)} (header in references/evidence-register.md)")
    reg_urls = urls(register)
    reg_ids = {r[c_id].strip().lower() for r in reg_rows if c_id is not None and c_id < len(r) and r[c_id].strip()}

    def cell(r, c):
        return r[c].strip() if c is not None and c < len(r) else ""

    # per-ask table
    asked = section(text, r"Did we answer")
    _, rows = table(asked)
    if asked is None:
        fails.append('no "Did we answer what was asked" section')
    elif not rows:
        fails.append("the per-ask table has no rows")
    optional = {}
    for m in re.finditer(r"^\s*[-*]?\s*\**(Q\d+)\**\s*[:.](.*)$", brief_text, re.M):
        o = re.search(r"\[optional:([^\]]*)\]", m.group(2), re.I)
        optional[m.group(1)] = {x.strip().lower() for x in o.group(1).split(",")} if o else set()
    answered, row_ids = [], []
    for r in rows:
        cells = [c.lower() for c in r]
        if len(cells) < 7:
            fails.append(f"per-ask row needs ask, five field statuses and a disposition: {' | '.join(r)[:100]}")
            continue
        ids = [x.upper() for x in re.findall(r"\bq\d+\b", cells[0])]
        if len(ids) != 1:
            fails.append(f"each per-ask row must name exactly one ask id (found {len(ids)}): {r[0][:80]}")
            continue
        qid, fields, disp = ids[0], cells[1:6], cells[-1]
        row_ids.append(qid)
        if any(c not in STATUS for c in fields):
            fails.append(f"{qid}: each field status must be exactly match, mismatch, unknown or n/a")
        for fname, val in zip(FIELDS, fields):
            if val == "n/a" and fname not in optional.get(qid, set()):
                fails.append(f"{qid}: '{fname}' is n/a but the brief does not mark it optional")
        if not re.fullmatch(r"(answered|unresolved)(\s*\([^)]*\))?", disp):
            fails.append(f"{qid}: disposition must be answered or unresolved")
        if disp.startswith("answered"):
            answered.append(qid)
            if any(c in ("mismatch", "unknown") for c in fields) or fields[0] != "match" or fields[4] != "match":
                fails.append(f"{qid}: closed as answered with a field that does not match")
    if a.brief:
        ids = sorted(set(re.findall(r"^\s*[-*]?\s*\**(Q\d+)\**\s*[:.]", brief_text, re.M)))
        if not ids:
            fails.append("the brief names no ask ids (write them as Q1:, Q2: ...)")
        for q in ids:
            if row_ids.count(q) != 1:
                fails.append(f"ask {q} from the brief has {row_ids.count(q)} rows (need exactly 1)")
        extra = sorted(set(row_ids) - set(ids))
        if extra:
            fails.append(f"per-ask rows name ids not in the brief: {extra}")
    elif not a.no_brief:
        fails.append("no --brief given (use --no-brief only for a single-ask report)")

    # every answered ask needs a real supporting row
    for q in answered:
        ok = [r for r in reg_rows if re.fullmatch(rf"\s*{q}\s*", cell(r, c_ask), re.I)
              and cell(r, c_stance).lower().startswith("support") and URL_RE.search(cell(r, c_url))
              and len(cell(r, c_loc)) >= 3 and len(cell(r, c_exc)) >= 3]
        if not ok:
            fails.append(f"{q} is answered but no register row for it has stance supports, a URL, a locator and an excerpt or value")

    # links in the reader-facing part
    for u in sorted(urls(reader) - reg_urls):
        fails.append(f"cited for the reader but not in the evidence register: {u}")
    answer = section(text, r"Answer") or ""
    if len(re.sub(r"\s+", "", answer)) < 40:
        fails.append("the Answer section is empty or nearly empty")
    cov = section(text, r"Null", r"Coverage", r"Checked, Inferred, Unknown", r"What we could not reach")
    if cov is None or len(cov.strip()) < 10:
        fails.append("no null-results or coverage section, or it is empty")

    if a.depth == "deep":
        try:
            log = open(a.log).read() if a.log else None
        except OSError:
            log = None
        if log is None:
            fails.append("deep: --log research/<topic>/log.md is required and must be readable")
        else:
            parts = re.split(r"^##\s*Round\s+(\d+)", log, flags=re.M | re.I)
            nums, good = [], []
            for k in range(1, len(parts) - 1, 2):
                n, body = parts[k], parts[k + 1]
                nums.append(n)
                q = re.search(r"Queries run:\s*(\S.*)", body)
                rr = re.search(r"Register rows added:\s*(.*)", body)
                if not q or not rr:
                    continue
                added = rr.group(1).strip()
                if re.match(r"none\s*\(\s*\w", added, re.I):
                    good.append(n)
                    continue
                listed = {x.lower() for x in re.findall(r"[A-Za-z]*\d+[A-Za-z0-9-]*", added)}
                if listed and listed <= reg_ids:
                    good.append(n)
                else:
                    fails.append(f"deep: round {n} lists register rows {sorted(listed - reg_ids)[:5] or '(none)'} that are not in the register (write 'none (<reason>)' if it found nothing)")
            if len(nums) != len(set(nums)):
                fails.append(f"deep: round numbers repeat ({', '.join(nums)})")
            if len(set(good)) < 3:
                tail = parts[-1] if len(parts) > 1 else ""
                if good and re.search(r"Decision:\s*stop\s*\(?\s*\w", tail, re.I):
                    warns.append(f"deep: {len(set(good))} complete round(s); stopped early with a stated reason")
                else:
                    fails.append(f"deep: the log has {len(set(good))} complete round block(s) (need 3, or a final 'Decision: stop (<reason>)')")
        if len(reg_urls) < 20:
            warns.append(f"deep: {len(reg_urls)} register sources (planning target 20+); say what coverage is missing")
        _, ref_rows = table(section(text, r"Refute pass", r"Refute"))
        seen, complete = set(), []
        for r in ref_rows:
            key = "|".join(c.lower() for c in r)
            if key in seen or not r or not re.match(r"(survives|weakened|refuted|unverified)\b", r[-1].strip().lower()):
                continue
            if all(len(c.strip()) >= 3 for c in r):
                seen.add(key)
                complete.append(key)
        for q in answered:
            if not any(re.search(rf"\b{q.lower()}\b", k) for k in complete):
                fails.append(f"deep: no complete Refute pass row names {q} (one attempt to break each decisive claim)")
        if not complete:
            fails.append("deep: the Refute pass has no complete row with a verdict")
        against = section(text, r"Strongest case against", r"Devil")
        if not against or not re.search(r"^\s*(?:[-*]|\d+[.)])\s+\S", against, re.M):
            fails.append('deep: no "Strongest case against" section with a material objection')
        has_contra = any(cell(r, c_stance).lower().startswith("contradict") for r in reg_rows)
        nulls = section(text, r"Null", r"Coverage") or ""
        if not has_contra and not re.search(r"contradict[^\n]*[\"'`][^\"'`\n]{4,}[\"'`]", nulls, re.I):
            fails.append('deep: no register row with stance contradicts, and no null-results line quoting the query that looked for one')
    elif 0 < len(reg_urls) < 5:
        warns.append(f"only {len(reg_urls)} distinct sources in the register")
    if answer and not re.search(r"\b(settled|likely|contested|unknown)\b", answer, re.I):
        warns.append("the Answer section gives no confidence (settled, likely, contested, unknown)")

    p = subprocess.run([sys.executable, os.path.join(HERE, "claims.py"), "untagged", a.report] +
                       (["--claims", a.claims] if a.claims else []), capture_output=True, text=True)
    if p.returncode not in (0, 3):
        fails.append(f"claims.py untagged could not run (exit {p.returncode}): {(p.stderr or p.stdout).strip()[-150:]}")
    elif p.returncode == 3:
        warns.append(f"{sum(l.startswith(a.report) for l in p.stdout.splitlines())} line(s) with untagged numbers or unknown tags")
    if a.claims:
        c = subprocess.run([sys.executable, os.path.join(HERE, "claims.py"), "check", "--claims", a.claims,
                            "--evidence", a.evidence], capture_output=True, text=True)
        if c.returncode in (1, 2):
            bad = [l for l in c.stdout.splitlines() if re.search(r"MISMATCH|MISATTRIBUTED|ERROR", l)]
            fails.append(f"claims.py check failed (exit {c.returncode}): {'; '.join(bad[:3]) or c.stderr.strip()[-150:]}")
        elif c.returncode == 3:
            warns.append("claims.py check: some numbers are unsupported or ambiguous; list them as unverified")
    for f in fails:
        print("FAIL", f)
    for w in warns:
        print("WARN", w)
    print("OK: report structure passed" if not fails and not warns else f"{len(fails)} failure(s), {len(warns)} warning(s)")
    return 1 if fails else (3 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
