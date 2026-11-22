#!/usr/bin/env python3
"""Check a studio project folder against what studio says was done, for the route the job took.

  studio_check.py <project> --route direction   # after step 0: hunt, board, sketches, pick
  studio_check.py <project> --route web         # new or redesigned page or site (default)
  studio_check.py <project> --route scoped      # an edit inside an existing surface
  studio_check.py <project> --route video --video out.mp4 [--seconds 12 --size 1080x1920]
  studio_check.py <project> --route 3d

Exit 0: no FAIL. 1: at least one FAIL. 2: bad input. Prints PASS, WARN or FAIL per check.
Evidence is checked, not paperwork: images must exist and decode, URLs count once, Borrowed rows
must name different decisions. Visual quality and the owner's choice stay with people.

History: the 2026-11-19 sandboxed run captured 11 gallery pages out of 15, opened 6, read no
specialist and shipped the default look. On 2026-11-21 GPT Sol passed the old checker with one URL
repeated 50 times, missing screenshots and one-byte sketches. Both are regression cases.
"""
import argparse
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ref_board import is_listing  # noqa: E402

BORROW_ROWS = ("type", "palette", "hero", "layout", "motion")
DEFAULT_FONTS = re.compile(r"bricolage grotesque|figtree|instrument serif", re.I)
SKIP_DIRS = {"node_modules", ".git", ".taste-skill", "design", "shots", ".claude", ".agents"}
USABLE = {"ok", "approved"}  # "needs review" counts once a person sets status "approved" in refs.json


class Report:
    def __init__(self):
        self.rows = []

    def add(self, level, name, detail):
        self.rows.append((level, name, detail))

    def ok(self, cond, name, good, bad, level="FAIL"):
        self.add("PASS" if cond else level, name, good if cond else bad)


def image_size(path):
    """(width, height) of a real PNG or JPEG, else None. A one-byte placeholder is not an image."""
    try:
        b = Path(path).read_bytes()
    except OSError:
        return None
    if len(b) < 1000:
        return None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24])
        return (w, h) if w and h else None
    if b[:2] == b"\xff\xd8":
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return (w, h)
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    return None


def section(md, title):
    m = re.search(rf"^##\s+{re.escape(title)}[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.I | re.M | re.S)
    return m.group(1) if m else None


def table_rows(text):
    rows = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|?$", line):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:] if rows else rows


def site_dir(root):
    return root / "site" if (root / "site").is_dir() else root


def site_files(root):
    base = site_dir(root)
    for f in base.rglob("*"):
        if f.is_file() and not (set(f.relative_to(base).parts) & SKIP_DIRS):
            yield f


def norm_url(u):
    s = urlsplit(u.strip())
    return (s.netloc.removeprefix("www.") + s.path.rstrip("/")).lower()


def check_direction(root, r):
    d = root / "design"
    cand = d / "candidates.txt"
    if cand.is_file():
        lines = [l.split() for l in cand.read_text(errors="replace").splitlines() if l.strip().startswith("http")]
        urls = {norm_url(l[0]) for l in lines}
        types = {l[1].lower() for l in lines if len(l) > 1}
        r.ok(len(urls) >= 30, "candidates looked at", f"{len(urls)} distinct candidates",
             f"{len(urls)} distinct candidate URLs in design/candidates.txt (need 30+; a repeated URL counts once)")
        r.ok(len(types) >= 5, "candidate source types", f"{len(types)} types",
             f"{len(types)} source types {sorted(types)[:8]} (need 5+)")
    else:
        r.add("FAIL", "candidates looked at", "design/candidates.txt missing (url, source type, keep|drop, reason)")

    refs_path = d / "refs" / "refs.json"
    refs = []
    if refs_path.is_file():
        try:
            refs = json.loads(refs_path.read_text())
        except json.JSONDecodeError as e:
            r.add("FAIL", "refs.json", f"not valid JSON: {e}")
    else:
        r.add("FAIL", "refs.json", "design/refs/refs.json missing (run ref_board.py)")
    usable, seen, broken = [], set(), []
    for x in refs:
        if x.get("status") not in USABLE or is_listing(x.get("url", "")):
            continue
        key = norm_url(x.get("url", ""))
        if key in seen:
            continue
        shot = (x.get("files") or {}).get("first_screen")
        if not shot or not image_size(d / "refs" / shot):
            broken.append(x.get("url", "?"))
            continue
        seen.add(key)
        usable.append(x)
    listing = [x["url"] for x in refs if is_listing(x.get("url", ""))]
    if refs:
        r.ok(10 <= len(usable) <= 15, "usable references", f"{len(usable)} distinct captured sites or shots",
             f"{len(usable)} usable (need 10 to 15 distinct URLs with a real screenshot; gallery pages, "
             "BLOCKED, FAILED and unapproved 'needs review' do not count)")
        r.ok(not broken, "screenshots exist", "every usable reference has a real image",
             f"{len(broken)} references have a missing or placeholder screenshot, e.g. {broken[:2]}")
        r.ok(not listing, "no gallery pages kept", "none",
             f"{len(listing)} gallery pages kept, e.g. {listing[:2]}: capture the sites inside them")
        hosts = {urlsplit(x["url"]).netloc.removeprefix("www.") for x in usable}
        r.ok(len(hosts) >= 6, "reference spread", f"{len(hosts)} distinct hosts",
             f"{len(hosts)} distinct hosts among usable references", level="WARN")
        bare = [x["url"] for x in usable if not str(x.get("borrow", "")).strip()]
        r.ok(not bare, "references annotated", "every usable reference has a borrow note",
             f"{len(bare)} usable references have no 'borrow' note, e.g. {bare[:2]}")

    sk = d / "sketches"
    shots = [p for p in sorted(sk.glob("*.png")) + sorted(sk.glob("*.jpg"))] if sk.is_dir() else []
    real = [p for p in shots if (image_size(p) or (0, 0))[0] >= 320]
    r.ok(len(real) >= 3, "3 sketched directions", f"{len(real)} sketch screenshots",
         f"{len(real)} real sketch screenshots in design/sketches (need 3, each at least 320 px wide)")

    md_path = root / "DESIGN.md"
    md = md_path.read_text(errors="replace") if md_path.is_file() else ""
    if not md:
        r.add("FAIL", "DESIGN.md", "missing")
        return md, usable
    borrowed = section(md, "Borrowed")
    if borrowed is None:
        r.add("FAIL", "Borrowed table", "DESIGN.md has no '## Borrowed' section")
        return md, usable
    rows = table_rows(borrowed)
    names = {Path(f).stem for x in usable for f in (x.get("files") or {}).values()}
    names |= {re.sub(r"-390$|-full$", "", n) for n in names}
    prefixes = {n.split("-")[0] for n in names}
    covered, cited, decisions = set(), 0, []
    for cells in rows:
        hit = next((a for a in BORROW_ROWS if a in cells[0].lower()), None)
        if not hit:
            continue
        covered.add(hit)
        rest = " ".join(cells[1:]).lower()
        what = (cells[-1] if len(cells) > 2 else rest).strip().lower()
        decisions.append(what)
        if "default" in rest:
            continue
        ids = set(re.findall(r"\b(\d{2})-[a-z0-9-]+", rest)) | set(re.findall(r"\bref\s*(\d{1,2})\b", rest))
        if {i.zfill(2) for i in ids} & prefixes or any(n in rest for n in names):
            cited += 1
    missing = [a for a in BORROW_ROWS if a not in covered]
    r.ok(not missing, "Borrowed rows", "type, palette, hero, layout, motion all present",
         f"Borrowed table lacks rows for {missing}")
    r.ok(cited >= 4, "references change the look", f"{cited} of 5 rows cite a usable reference",
         f"{cited} of 5 Borrowed rows cite a usable reference (need 4)")
    dup = len(decisions) - len({x for x in decisions if x})
    r.ok(dup == 0, "distinct decisions", "each Borrowed row names its own decision",
         f"{dup} Borrowed rows repeat or leave blank the decision taken")
    approved = section(md, "Approved")
    r.ok(approved is not None and len(approved.split()) >= 8, "approved direction recorded",
         "DESIGN.md records the approved hero structure, motif and motion idea",
         "DESIGN.md needs '## Approved': the picked direction's hero structure, visual motif and motion idea")
    return md, usable


def check_build(root, md, usable, r, route):
    files = list(site_files(root))
    text = {f: f.read_text(errors="replace") for f in files
            if f.suffix.lower() in (".html", ".css", ".js", ".mjs", ".jsx", ".tsx", ".ts", ".svg", ".json")}
    blob = "\n".join(text.values())
    ledger = section(md, "Skills used") if md else None
    if ledger is None:
        r.add("FAIL", "skills ledger", "DESIGN.md has no '## Skills used' section (a row per specialist read)")
    else:
        rows = table_rows(ledger) or [[l] for l in ledger.splitlines() if l.strip().startswith(("-", "*"))]
        paths = re.findall(r"skill\.md", ledger, re.I)
        r.ok(len(rows) >= 2 and len(paths) >= 2, "skills ledger", f"{len(rows)} rows, {len(paths)} SKILL.md files named",
             "the ledger needs a row for each specialist read, with the SKILL.md file and what it changed")
        if re.search(r"\bgsap\b|scrolltrigger", blob, re.I) and "gsap" not in ledger.lower():
            r.add("FAIL", "gsap skills read", "the build uses GSAP but the ledger names no GSAP skill")
    if route == "web":
        plan = section(md, "Motion plan") if md else None
        if plan is None:
            r.add("FAIL", "motion plan", "DESIGN.md has no '## Motion plan' (write it with animate before motion code)")
        else:
            r.ok(re.search(r"signature", plan, re.I) is not None, "signature moment",
                 "the motion plan names a signature moment", "the motion plan names no signature moment")
            r.ok(re.search(r"reduced", plan, re.I) is not None, "reduced motion planned",
                 "the motion plan covers reduced motion", "the motion plan says nothing about reduced motion", level="WARN")
        caps = [root / "design" / n for n in ("final-1440.png", "final-390.png")]
        good = [c.name for c in caps if image_size(c)]
        r.ok(len(good) == 2, "shipped page captured", "design/final-1440.png and final-390.png exist",
             f"capture the shipped page to design/final-1440.png and design/final-390.png (found {good})")
        fonts = sorted({m.group(0).lower() for m in DEFAULT_FONTS.finditer(blob)})
        if fonts:
            ref_fonts = " ".join(str((x.get("h1Font") or {}).get("family", "")) for x in usable).lower()
            unjustified = [f for f in fonts if f not in ref_fonts]
            r.ok(not unjustified, "default look", f"{fonts} appear in a captured reference",
                 f"the build uses common AI-default fonts {unjustified}; say in DESIGN.md why, or change them",
                 level="WARN")
    size = sum(f.stat().st_size for f in files)
    r.ok(size < 25_000_000, "site size", f"{size / 1e6:.2f} MB in {len(files)} files",
         f"{size / 1e6:.1f} MB in {len(files)} files: ship only the files the page uses")
    if size >= 10_000_000:
        r.add("WARN", "site weight", f"{size / 1e6:.1f} MB: check it against the brief's budget")
    bad = [str(f.relative_to(root)) for f, t in text.items() if re.search(r"unsplash\.com|picsum\.photos", t, re.I)]
    r.ok(not bad, "no Unsplash or picsum", "none", f"found in {bad[:3]}")


def check_video(path, seconds, size, r):
    p = Path(path)
    if not p.is_file():
        r.add("FAIL", "video file", f"{path} not found (render the final file)")
        return
    if not shutil.which("ffprobe"):
        r.add("WARN", "video properties", "ffprobe missing: measure duration, size and audio by hand")
        return
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "json", str(p)], capture_output=True, text=True)
    try:
        info = json.loads(out.stdout)
    except json.JSONDecodeError:
        r.add("FAIL", "video file", "ffprobe could not read it")
        return
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not v:
        r.add("FAIL", "video stream", "no video stream")
        return
    dur = float(info.get("format", {}).get("duration", 0))
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    frame = float(den) / float(num) if float(num) else 0.04
    r.add("PASS", "video measured", f"{v['width']}x{v['height']}, {dur:.2f} s, audio streams: "
          f"{sum(s.get('codec_type') == 'audio' for s in streams)}")
    if size:
        w, h = (int(x) for x in size.lower().split("x"))
        r.ok((v["width"], v["height"]) == (w, h), "video size", size, f"{v['width']}x{v['height']} (want {size})")
    if seconds:
        r.ok(abs(dur - seconds) <= frame + 1e-6, "video length", f"{dur:.3f} s", f"{dur:.3f} s (want {seconds} s within one frame)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--route", choices=("direction", "web", "scoped", "video", "3d"), default="web")
    ap.add_argument("--stage", choices=("direction", "final"), help="old name: --stage direction = --route direction")
    ap.add_argument("--video"); ap.add_argument("--seconds", type=float); ap.add_argument("--size")
    a = ap.parse_args()
    root = Path(a.project).resolve()
    if not root.is_dir():
        print(f"no such folder: {root}", file=sys.stderr)
        return 2
    route = "direction" if a.stage == "direction" else a.route
    r = Report()
    md = (root / "DESIGN.md").read_text(errors="replace") if (root / "DESIGN.md").is_file() else ""
    usable = []
    if route in ("direction", "web"):
        md, usable = check_direction(root, r)
    if route in ("web", "scoped", "3d"):
        check_build(root, md, usable, r, route)
    if route == "video":
        if not a.video:
            print("--route video needs --video <file>", file=sys.stderr)
            return 2
        check_video(a.video, a.seconds, a.size, r)
    for level, name, detail in r.rows:
        print(f"{level:4}  {name}: {detail}")
    fails = sum(l == "FAIL" for l, _, _ in r.rows)
    print(f"\n{fails} FAIL, {sum(l == 'WARN' for l, _, _ in r.rows)} WARN, {sum(l == 'PASS' for l, _, _ in r.rows)} PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
