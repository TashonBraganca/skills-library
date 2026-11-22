#!/usr/bin/env python3
"""prose_check.py regressions, including the false positives and misses GPT Sol found on 2026-11-21."""
import json, subprocess, sys
from pathlib import Path
CHECK = Path(__file__).resolve().parents[1] / "scripts" / "prose_check.py"


def run(text, *extra):
    p = subprocess.run([sys.executable, str(CHECK), "-", "--json", *extra], input=text, capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)["flags"]


def kinds(flags, level):
    return [f["kind"] for f in flags[level]]


cases = []
rc, f = run("The run finished. Accuracy rose from 71% to 74% on 404 items.")
cases.append(("clean prose passes", rc == 0 and not f["hard"]))
rc, f = run("It's not just faster — it's better. I hope this helps!")
cases.append(("dash and residue are hard", rc == 1 and "dash" in kinds(f, "hard") and "chatbot residue" in kinds(f, "hard")))
rc, f = run("> She said “fine” – and left.\n")
cases.append(("block quote is weak, not hard", rc == 0 and not f["hard"] and f["weak"]))
rc, f = run("Can you cover Friday? Let me know if you can.")
cases.append(("a real 'let me know if' request is not hard", rc == 0))
rc, f = run("The log printed BACKOFF — retry and stopped.", "--allow", "BACKOFF — retry")
cases.append(("--allow skips an exact literal", rc == 0))
rc, f = run("The log printed BACKOFF — retry and stopped.")
cases.append(("without --allow the same dash is hard", rc == 1))
rc, f = run("Routes are learned over BGP from the WAN edge. The RIB keeps NLRI per peer.")
cases.append(("dense jargon is flagged", any("dense jargon" in k for k in kinds(f, "weak"))))
rc, f = run("```\na — b\n```\nDone.")
cases.append(("dash in a code fence is ignored", rc == 0))
fails = 0
for name, ok in cases:
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}")
print(f"{len(cases) - fails}/{len(cases)} cases correct")
sys.exit(1 if fails else 0)
