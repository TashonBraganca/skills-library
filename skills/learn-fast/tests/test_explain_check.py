#!/usr/bin/env python3
"""explain_check.py: a plain page passes; jargon, symbols, number dumps, crowded diagrams and a missing
catch fail; soft problems warn. Includes the false passes GPT Sol found on 2026-11-21."""
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
CHECK = HERE.parent / "scripts" / "explain_check.py"
good = (HERE / "good_page.html").read_text()
many_labels = "".join(f'<text x="1" y="{k}">part {k}</text>' for k in range(6))
long_step = "Checking every shelf " + "and every bin " * 30


def run(html):
    p = subprocess.run([sys.executable, str(CHECK), "-", "--terms", str(HERE / "terms.txt")], input=html,
                       capture_output=True, text=True)
    return p.returncode, p.stdout.count("\nWARN") + p.stdout.startswith("WARN")


cases = [  # (name, html, want rc, want at least one warning)
    ("plain page passes", good, 0, False),
    ("acronym-heavy step 1 fails", good.replace("You want one song.", "You want one LLM KV answer."), 0, True),
    ("listed term in step 1 fails", good.replace("You want one song.", "You want one embedding."), 1, None),
    ("listed term in step 2 warns", good.replace("You read three signs", "You read three embedding signs"), 0, True),
    ("number in step 1 warns", good.replace("You want one song.", "You want one of 1,000 songs."), 0, True),
    ("three quantities warn", good.replace("about 300 covers", "about 300 of 90,000 covers, 2% of them"), 0, True),
    ("symbol in a later step warns", good.replace("You keep the best match", "You keep the top λ match"), 0, True),
    ("letter-digit id warns", good.replace("You keep the best match", "You keep K3"), 0, True),
    ("formula in inline code warns, not fails", good.replace("You keep the best match", "You keep <code>x = 3</code>"), 0, True),
    ("Greek in the takeaway warns", good.replace("it reads a few signs", "it reads λ signs"), 0, True),
    ("symbol in an SVG label warns", good.replace(">you</text>", ">KV CACHE λ = 300</text>"), 0, True),
    ("two new terms in one step fail", good.replace("whole <dfn>group</dfn>", "whole <dfn>group</dfn> or <dfn>cluster</dfn>"), 1, None),
    ("rare word without dfn warns", good.replace("smaller signs split it", "smaller signs bifurcate it"), 0, True),
    ("jargon inside Go deeper is ignored", good, 0, False),
    ("open Go deeper fails", good.replace("<details>", "<details open>"), 1, None),
    ("crowded diagram fails", good.replace("</svg>", many_labels + "</svg>"), 1, None),
    ("nested data-show scopes intersect", good.replace("</svg>", '<g data-show="1"><g data-show="3">' + many_labels + "</g></g></svg>"), 0, False),
    ("step over 80 words fails", good.replace("Checking every shelf", long_step), 1, None),
    ("missing takeaway fails", good.replace(" data-takeaway", ""), 1, None),
    ("missing catch fails", good.replace(" data-catch", ""), 1, None),
    ("step ids out of order fail", good.replace('data-step="3"', 'data-step="8"'), 1, None),
    ("number in the opener warns", good.replace("even when the library is huge", "even with 90,000 songs"), 0, True),
]
fails = 0
for name, html, want_rc, want_warn in cases:
    rc, warns = run(html)
    ok = rc == want_rc and (want_warn is None or (warns > 0) == want_warn)
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: rc {rc} (want {want_rc}), warnings {warns}")
print(f"{len(cases) - fails}/{len(cases)} cases correct")
sys.exit(1 if fails else 0)
