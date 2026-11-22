#!/usr/bin/env python3
"""Ask a different model family (GPT through the Codex CLI) to attack a plan, diff, report or skill.

A model misses its own errors far more often than the same errors written by someone else
(Self-Correction Bench, arXiv 2507.02778). A reviewer from another model family, with fresh
context, catches what the author cannot. The reviewer only reads: sandbox read-only.

  second_opinion.py --files plan.md src/train.py --ask "Will this eval leak?" --out review/plan-sol.md
  second_opinion.py --files report.md --ask "Check every number against runs/" --effort high
  second_opinion.py --dry-run --files x.md --ask "..."          # print the prompt, spend nothing

Exit codes: 0 review written, 1 codex failed, 2 bad input, 3 written but empty or truncated.
Costs Codex usage (typically 30k to 150k tokens). The script prints the tokens used.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

CONTRACT = """You are a harsh senior reviewer from a different model family. Read only: edit nothing,
install nothing, start no agents. You may read any file named below and run read-only commands.

Question from the author: {ask}

{blind}Material (read every file in full before judging):
{files}
{context}
Rules:
- Find what is wrong, missing, or weaker than a better available option. No praise, no summary of
  what the material says.
- Each finding: the exact line or claim quoted, the concrete failure it causes (inputs, situation,
  wrong result), how sure you are, and the exact fix (replacement text, code or check).
- Name at least one materially different approach the author did not consider, and say what
  evidence would show it is better. If none is better, say why in one line.
- Mark anything you could not verify. Do not invent file contents, numbers or citations.
- Sort findings into: ACT ON (would change the result), CONSIDER (likely improves it), NOTED (minor).
- End with a one-line verdict: ship, ship with fixes, or rework.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files", nargs="+", required=True, help="files the reviewer must read")
    ap.add_argument("--ask", required=True, help="what the reviewer should attack")
    ap.add_argument("--blind", nargs="*", default=[], help="source files the reviewer reads first, forming its own answer before seeing --files")
    ap.add_argument("--context", default="", help="decisions already made, constraints, what not to reopen")
    ap.add_argument("--out", help="where to write the review (default: ./second-opinion-<time>.md)")
    ap.add_argument("--model", default=os.environ.get("SECOND_OPINION_MODEL", "gpt-6.2-sol"))
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh"])
    ap.add_argument("--timeout", type=int, default=1800, help="seconds")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    missing = [f for f in a.files + a.blind if not os.path.exists(f)]
    overlap = {os.path.realpath(f) for f in a.files} & {os.path.realpath(f) for f in a.blind}
    if overlap:
        print(f"--blind and --files overlap: {sorted(overlap)}; the reviewer must not see the draft in stage one", file=sys.stderr)
        return 2
    if missing:
        print(f"missing files: {missing}", file=sys.stderr)
        return 2
    files = "\n".join(f"- {os.path.abspath(f)}" for f in a.files)
    ctx = f"\nAlready decided (do not reopen without new evidence): {a.context}\n" if a.context else ""
    blind = ""
    if a.blind:
        bl = "\n".join(f"- {os.path.abspath(f)}" for f in a.blind)
        blind = ("BLIND FIRST: before opening the material below, read only these source files and write your own "
                 "short answer to the question (approach, decisive check, likely conclusion) under a heading "
                 "INDEPENDENT ANSWER:\n" + bl + "\nThen open the material and compare.\n\n")
    prompt = CONTRACT.format(ask=a.ask, files=files, context=ctx, blind=blind)
    if a.dry_run:
        print(prompt)
        return 0
    if not shutil.which("codex"):
        print("codex CLI not found. Install Codex or ask the owner for another reviewer.", file=sys.stderr)
        return 1
    out = os.path.abspath(a.out or f"second-opinion-{time.strftime('%Y%m%d-%H%M%S')}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    log_path = out + ".log"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as pf:
        pf.write(prompt)
        prompt_path = pf.name
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "-m", a.model,
           "-c", f"model_reasoning_effort={a.effort}", "-o", out, "-"]
    print(f"[second-opinion] {a.model} ({a.effort}) reviewing {len(a.files)} file(s) -> {out}", file=sys.stderr)
    try:
        # stdin must come from a file: an inherited terminal stdin makes codex exec wait forever
        with open(prompt_path) as stdin, open(log_path, "w") as log:
            rc = subprocess.run(cmd, stdin=stdin, stdout=log, stderr=subprocess.STDOUT, timeout=a.timeout).returncode
    except subprocess.TimeoutExpired:
        print(f"[second-opinion] timed out after {a.timeout}s; partial log at {log_path}", file=sys.stderr)
        return 1
    finally:
        os.unlink(prompt_path)
    log_text = open(log_path, errors="replace").read()
    m = re.search(r"tokens used\s*\n\s*([\d,]+)", log_text)
    tokens = m.group(1) if m else "unknown"
    if rc != 0:
        print(f"[second-opinion] codex exit {rc}; see {log_path}. Tokens: {tokens}", file=sys.stderr)
        return 1
    body = open(out, errors="replace").read() if os.path.exists(out) else ""
    print(f"[second-opinion] done. Tokens used: {tokens}. Review: {out}", file=sys.stderr)
    if len(body.strip()) < 200 or not re.search(r"ACT ON", body) or not re.search(r"verdict", body, re.I):
        print("[second-opinion] review is empty or missing its sections; read the log before trusting it.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
