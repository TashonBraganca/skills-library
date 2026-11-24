"""Guard: nothing may force a summary opener onto long replies again (removed 2026-11-24).

A forced 5-line opener, and the Stop check that enforced it, condensed long answers and buried them.
This fails if the rule comes back in the library or in any installed profile, or if a profile's
injected rules block drifts from the template.
Run: python3 hooks/test_no_forced_opener.py
"""
import os, re, sys

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
FORBIDDEN = re.compile(r"over 300 words|bro restatement|OPENER_MAX_WORDS|needs_bro_opener|"
                       r"open it with up to five|open any reply over", re.I)
LIBRARY_FILES = ["templates/claude-md-fragment.md", "hooks/prose_gate.py", "hooks/skill_router.py",
                 "skills/bro/SKILL.md", "skills/writing/SKILL.md", "skills/wayfinder/SKILL.md"]
PROFILES = [".claude-work/CLAUDE.md", ".claude-personal/CLAUDE.md", ".claude-personal-mind/CLAUDE.md",
            ".claude/CLAUDE.md", ".codex/AGENTS.md", "AGENTS.md", "CLAUDE.md"]
BEGIN, END = "<!-- tashon-skills:begin -->", "<!-- tashon-skills:end -->"

def block(text):
    i, j = text.find(BEGIN), text.find(END)
    return text[i + len(BEGIN):j].strip() if i >= 0 and j > i else None

fails = 0
def check(name, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (f": {detail}" if detail and not ok else ""))
    fails += not ok

for rel in LIBRARY_FILES:
    p = os.path.join(LIB, rel)
    if os.path.exists(p):
        hits = [l.strip()[:80] for l in open(p) if FORBIDDEN.search(l)]
        check(f"no forced opener in {rel}", not hits, "; ".join(hits))

template = open(os.path.join(LIB, "templates/claude-md-fragment.md")).read()
tblock = block(template) or template.strip()
for rel in PROFILES:
    p = os.path.join(HOME, rel)
    if not os.path.exists(p):
        continue
    text = open(p).read()
    hits = [l.strip()[:80] for l in text.splitlines() if FORBIDDEN.search(l)]
    check(f"no forced opener in ~/{rel}", not hits, "; ".join(hits))
    b = block(text)
    if b is not None:
        check(f"~/{rel} rules block matches the template", b == tblock, "rerun ./install.sh")

print(f"\n{fails} failure(s)")
sys.exit(1 if fails else 0)
