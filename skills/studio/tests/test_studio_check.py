#!/usr/bin/env python3
"""Regression test for scripts/studio_check.py: a fixture that does every step passes, and each
single fault trips exactly its own check.  Run: python3 tests/test_studio_check.py"""
import json
import shutil
import subprocess
import sys
import tempfile
import struct
import zlib


def png(w=400, h=300):
    """A real, decodable PNG with noise so it is over 1 KB."""
    import random
    rnd = random.Random(w * h)
    raw = b"".join(b"\x00" + bytes(rnd.randrange(256) for _ in range(w * 3)) for _ in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


PNG = png()
from pathlib import Path

CHECK = Path(__file__).resolve().parent.parent / "scripts" / "studio_check.py"
HOSTS = ["stripe.com", "linear.app", "www.awwwards.com/sites/mercury", "dribbble.com/shots/111-a",
         "godly.website/website/b-2", "pitch.com", "vercel.com", "raycast.com", "cash.app", "arc.net", "tally.so", "mmm.page"]
DESIGN = """# Test
## Borrowed
| Aspect | From | What |
|---|---|---|
| Type | 01-stripe-com | tight display scale |
| Palette | 07-vercel-com | mono with one hot accent |
| Hero structure | 04-dribbble-com-shots-111-a | split hero with live object |
| Layout rhythm | 06-pitch-com | wide-narrow alternation |
| Motion signature | default | spring snap |
## Approved
Split hero with a live ledger object, ink-stamp motif, rows snap together as the signature moment.
## Motion plan
- signature: rows snap together with confetti
- reduced motion shows the matched state
- hero entrance
- hero drag
- scroll pin story
- scrubbed band
- hover lift
- press squash
- counter roll
- confetti signature
## Skills used
| Stage | Skill | File | Changed |
|---|---|---|---|
| directions | antialgorithm | .claude/skills/antialgorithm/SKILL.md | killed the first idea |
| motion | animate | .claude/skills/animate/SKILL.md | durations |
| gsap | gsap-core | .claude/skills/gsap-core/SKILL.md | gsap.matchMedia |
| scroll | gsap-scrolltrigger | .claude/skills/gsap-scrolltrigger/SKILL.md | pin spacing |
| components | emil-design-eng | .claude/skills/emil-design-eng/SKILL.md | focus rings |
| finish | impeccable | .claude/skills/impeccable/SKILL.md | critique fixes |
"""


def build(root):
    (root / "design/refs").mkdir(parents=True)
    (root / "design/sketches").mkdir()
    (root / "site").mkdir()
    refs = []
    for i, h in enumerate(HOSTS, 1):
        n = f"{i:02d}-" + h.replace("/", "-").replace(".", "-")
        (root / f"design/refs/{n}.png").write_bytes(PNG)
        refs.append({"url": "https://" + h, "status": "ok", "files": {"first_screen": n + ".png"}, "borrow": "type scale"})
    (root / "design/refs/refs.json").write_text(json.dumps(refs))
    types = ["award", "saas", "dribbble", "component", "motion", "type", "3d"]
    (root / "design/candidates.txt").write_text("".join(
        f"https://ex{i}.com {types[i % 7]} {'keep' if i < 12 else 'drop'} four word reason here\n" for i in range(35)))
    for s in "abc":
        (root / f"design/sketches/{s}.png").write_bytes(PNG)
    (root / "design/final-1440.png").write_bytes(PNG)
    (root / "design/final-390.png").write_bytes(PNG)
    (root / "DESIGN.md").write_text(DESIGN)
    (root / "site/index.html").write_text("<script>gsap.registerPlugin(ScrollTrigger)</script>")
    (root / "site/style.css").write_text('body{font-family:"Space Grotesk"}')
    (root / "README.md").write_text("readme")


def edit_refs(root, fn):
    p = root / "design/refs/refs.json"
    d = json.loads(p.read_text())
    fn(d)
    p.write_text(json.dumps(d))


def sub(root, path, old, new):
    p = root / path
    p.write_text(p.read_text().replace(old, new))


CASES = [  # (name, mutation, check names that must FAIL)
    ("clean", lambda r: None, set()),
    ("25 candidates", lambda r: sub(r, "design/candidates.txt", "".join(
        (r / "design/candidates.txt").read_text().splitlines(True)[25:]), ""), {"candidates looked at"}),
    ("one URL repeated 50 times (Sol's false pass)", lambda r: (r / "design/candidates.txt").write_text(
        "".join(f"https://same.com {t} keep reason\n" for t in ["a", "b", "c", "d", "e"] * 10)), {"candidates looked at"}),
    ("gallery page kept", lambda r: edit_refs(r, lambda d: d[1].update(url="https://onepagelove.com/style/fun")),
     {"no gallery pages kept"}),
    ("placeholder screenshots (Sol's false pass)", lambda r: [(r / f"design/refs/{p.name}").write_bytes(b"x")
     for p in sorted((r / "design/refs").glob("*.png"))[:4]], {"usable references", "screenshots exist", "references change the look"}),
    ("one-byte sketches", lambda r: (r / "design/sketches/c.png").write_bytes(b"x"), {"3 sketched directions"}),
    ("two default rows", lambda r: sub(r, "DESIGN.md", "| 06-pitch-com", "| default"), {"references change the look"}),
    ("same decision twice", lambda r: sub(r, "DESIGN.md", "mono with one hot accent", "tight display scale"), {"distinct decisions"}),
    ("no approved direction", lambda r: sub(r, "DESIGN.md", "## Approved", "## Notes"), {"approved direction recorded"}),
    ("gsap without gsap skill", lambda r: sub(r, "DESIGN.md", "| gsap | gsap-core | .claude/skills/gsap-core/SKILL.md | gsap.matchMedia |\n| scroll | gsap-scrolltrigger | .claude/skills/gsap-scrolltrigger/SKILL.md | pin spacing |\n", ""), {"gsap skills read"}),
    ("no signature moment", lambda r: (sub(r, "DESIGN.md", "- signature: rows snap together with confetti\n", ""), sub(r, "DESIGN.md", "- confetti signature\n", "")), {"signature moment"}),
    ("no final captures", lambda r: (r / "design/final-390.png").unlink(), {"shipped page captured"}),
    ("default font is a warning only", lambda r: (r / "site/style.css").write_text("h1{font-family:Bricolage Grotesque}"), set()),
    ("unsplash", lambda r: (r / "site/hero.html").write_text("<img src=https://images.unsplash.com/x>"), {"no Unsplash or picsum"}),
    ("30 MB site", lambda r: (r / "site/big.bin").write_bytes(b"0" * 30_000_000), {"site size"}),
]


def fails(root):
    out = subprocess.run([sys.executable, str(CHECK), str(root)], capture_output=True, text=True)
    assert "Traceback" not in out.stderr, out.stderr
    return {l[6:].split(":")[0] for l in out.stdout.splitlines() if l.startswith("FAIL  ")}, out.returncode


def main():
    bad = 0
    with tempfile.TemporaryDirectory() as t:
        base = Path(t) / "base"
        build(base)
        for name, mutate, want in CASES:
            root = Path(t) / "case"
            shutil.rmtree(root, ignore_errors=True)
            shutil.copytree(base, root)
            mutate(root)
            got, rc = fails(root)
            ok = got == want and rc == (1 if want else 0)
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name}: want {sorted(want)} got {sorted(got)} rc={rc}")
    print(f"{len(CASES) - bad} of {len(CASES)} cases pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
