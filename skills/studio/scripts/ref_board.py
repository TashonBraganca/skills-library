#!/usr/bin/env python3
"""Capture design references at full resolution and lay them out on one board to show the owner.

  ref_board.py --out refs/ URL [URL ...]
  ref_board.py --out refs/ --file refs.json      # [{"url": ..., "why": ..., "borrow": ..., "avoid": ...}]
  ref_board.py --out refs/ --file refs/refs.json --render-only   # after annotating: rebuild, no recapture
  options: --mobile (also a 390px first screen), --full (also a full-page capture, max 9000px tall)

For each URL it saves a 1440x900 first-screen PNG (never downscaled), optional mobile and full-page
PNGs, and reads from the live page: title, h1 text, the computed font family and size of h1 and body,
the page background, and the most used text and surface colours. It writes refs/refs.json and
refs/board.html (a grid you open in a browser or publish; images link to the full files).

A page that looks blocked (captcha, "access denied", "just a moment", under 200 characters of text)
is marked BLOCKED, not captured as a reference. Screenshots are for private reference only: never
ship them, and never copy a reference's code, copy, images or signature effect.
Statuses: ok; "needs review" (under 200 characters of text: open the screenshot, and set its status
to "approved" in refs.json if it is a real, useful page; studio_check.py counts ok and approved); BLOCKED (a challenge
page or 401/403/429/503, after one stealth-browser retry); FAILED (other HTTP errors, timeouts). A
mobile challenge keeps the desktop capture and records mobile_error. Consent banners get an
explicit reject or necessary-only click, never an accept.
Exit 0: every URL captured. 3: some blocked, failed or LISTING (a gallery listing page, not a site). 2: bad input.
"""
import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Challenge markers, matched in the title and the first 400 characters of text. "captcha" alone is not
# one: an article about CAPTCHAs is a real page.
BLOCK_RE = re.compile(r"just a moment\.\.\.|attention required|access denied|verify you are human|"
                      r"performing security verification|checking your browser|are you a robot|"
                      r"ray id:|cf-chl|unusual traffic from your computer|please enable javascript and cookies", re.I)
# Gallery listings are where references are found, not references (2026-11-19: 11 of 15 captures were
# gallery pages, so the board gave tone only). A single entry (awwwards.com/sites/x, dribbble.com/shots/1,
# godly.website/website/x) passes.
GALLERY_HOSTS = ("awwwards.com", "godly.website", "siteinspire.com", "onepagelove.com", "saaspo.com", "lapa.ninja",
                 "land-book.com", "landingfolio.com", "dribbble.com", "cssdesignawards.com", "httpster.net",
                 "minimal.gallery", "curated.design", "mobbin.com", "reactbits.dev", "21st.dev", "typewolf.com",
                 "behance.net", "framer.com", "webflow.com", "saasframe.io", "darkmodedesign.com", "bestfolios.com")
LIST_PATH_RE = re.compile(r"/(inspiration|category|categories|style|styles|tag|tags|industry|industries|search|"
                          r"collections?|motion|browse|explore|trending|popular|gallery|top-\d+[^/]*|best-[^/]*)(/|$)", re.I)


def is_listing(url):
    from urllib.parse import urlsplit
    u = urlsplit(url)
    host = u.netloc.lower().removeprefix("www.")
    path = u.path.rstrip("/")
    if re.search(r"(^|&)(q|query|search|s)=", u.query):
        return True
    if not any(host == g or host.endswith("." + g) for g in GALLERY_HOSTS):
        return False
    if path == "" or LIST_PATH_RE.search(path + "/"):
        return True
    return host.endswith("21st.dev") and "/s/" in path + "/"


REJECT_RE = re.compile(r"^\s*(reject all|reject|decline all|decline|only necessary|necessary only|"
                       r"reject non-essential|use necessary cookies only)\s*$", re.I)


def dismiss_banners(page):
    """Click an explicit reject or necessary-only button if a consent banner shows one. Never accepts."""
    try:
        for b in page.get_by_role("button").all()[:80]:
            try:
                if b.is_visible() and REJECT_RE.match(b.inner_text(timeout=300) or ""):
                    b.click(timeout=1500)
                    page.wait_for_timeout(500)
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def looks_blocked(info, status=None):
    hay = f"{info.get('title', '')}\n{info.get('sample', '')}"
    return bool(BLOCK_RE.search(hay)) or (status is not None and status in (401, 403, 429, 503))


def thin(info):
    return info.get("textLength", 0) < 200  # a portfolio can be this short: flag for review, do not block


def stealth_capture(url, path):
    """Retry a blocked page in Scrapling's stealth browser (Cloudflare solver on). Returns probe info or None."""
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError:
        return None
    box = {}

    def act(page):
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(2500)
        dismiss_banners(page)
        box["info"] = page.evaluate(PROBE)
        if not looks_blocked(box["info"]):
            page.screenshot(path=str(path))
            box["shot"] = True
        return page
    try:
        StealthyFetcher.fetch(url, headless=True, solve_cloudflare=True, page_action=act, timeout=90000)
    except Exception as e:
        box["error"] = str(e).splitlines()[0][:200]
    return box
PROBE = """() => {
  const cs = el => el ? getComputedStyle(el) : null;
  const h1 = document.querySelector('h1'); const b = document.body || document.documentElement;
  const pick = s => s ? {family: s.fontFamily, size: s.fontSize, weight: s.fontWeight, lineHeight: s.lineHeight} : null;
  const text = new Map(), surf = new Map();
  for (const el of Array.from(document.querySelectorAll('body *')).slice(0, 4000)) {
    const r = el.getBoundingClientRect(); if (r.width * r.height < 40 || r.top > 2700) continue;
    const s = getComputedStyle(el);
    if (el.childNodes.length && Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim()))
      text.set(s.color, (text.get(s.color) || 0) + 1);
    const bg = s.backgroundColor; if (bg && !bg.endsWith(', 0)') && bg !== 'transparent')
      surf.set(bg, (surf.get(bg) || 0) + r.width * r.height);
  }
  const top = m => Array.from(m.entries()).sort((a, b) => b[1] - a[1]).slice(0, 6).map(e => e[0]);
  return {title: document.title, h1: h1 ? h1.innerText.trim().slice(0, 140) : '',
          h1Font: pick(cs(h1)), bodyFont: pick(cs(b)), background: b ? cs(b).backgroundColor : null,
          textColors: top(text), surfaceColors: top(surf), textLength: ((b && b.innerText) || '').length,
          sample: ((b && b.innerText) || '').slice(0, 400)};
}"""


def slug(url, i):
    s = re.sub(r"^https?://(www\.)?", "", url)
    return f"{i:02d}-" + re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:60]


def capture(page, ctx_mobile, ref, out, i, full, mobile):
    url = ref["url"]
    name = slug(url, i)
    rec = {**ref, "status": "ok", "files": {}}
    try:
        resp = page.goto(url, wait_until="load", timeout=45000)
        status = resp.status if resp else None
        page.wait_for_timeout(1800)
        dismiss_banners(page)
        try:
            info = page.evaluate(PROBE)
        except Exception:  # some sites (Dribbble) are still swapping the document: wait once, retry
            page.wait_for_timeout(2500)
            info = page.evaluate(PROBE)
        rec.update(info)
        rec["http_status"] = status
        if status and status >= 400 and not looks_blocked(info, status):
            rec.update(status="FAILED", error=f"HTTP {status}")
            rec.pop("sample", None)
            return rec
        if looks_blocked(info, status):
            rec.update(status="BLOCKED", error="challenge page", _retry=name)
            rec.pop("sample", None)
            return rec
        page.screenshot(path=str(out / f"{name}.png"))
        rec["files"]["first_screen"] = f"{name}.png"
        if is_listing(url):
            rec["status"] = "LISTING"
            rec["error"] = "gallery listing page: open it, pick sites from it, and capture those instead"
        elif thin(info):
            rec["status"] = "needs review"
            rec["error"] = "under 200 characters of text: open the screenshot before using it"
        if full:
            h = min(page.evaluate("document.documentElement.scrollHeight"), 9000)
            page.set_viewport_size({"width": 1440, "height": h})
            page.screenshot(path=str(out / f"{name}-full.png"))
            page.set_viewport_size({"width": 1440, "height": 900})
            rec["files"]["full_page"] = f"{name}-full.png"
        if mobile:
            mp = ctx_mobile.new_page()
            try:
                mresp = mp.goto(url, wait_until="load", timeout=45000)
                mp.wait_for_timeout(1500)
                dismiss_banners(mp)
                minfo = mp.evaluate(PROBE)
                if looks_blocked(minfo, mresp.status if mresp else None):
                    rec["mobile_error"] = "mobile view showed a challenge page; desktop kept"
                else:
                    mp.screenshot(path=str(out / f"{name}-390.png"))
                    rec["files"]["mobile"] = f"{name}-390.png"
            except Exception as e:
                rec["mobile_error"] = str(e).splitlines()[0][:200]
            finally:
                mp.close()
    except Exception as e:  # network, timeout, navigation: record and keep going
        rec["status"] = "FAILED"
        rec["error"] = str(e).splitlines()[0][:200]
    rec.pop("sample", None)
    return rec


def board(recs, out):
    cards = []
    for r in recs:
        e = lambda k: html.escape(str(r.get(k) or ""))
        img = r["files"].get("first_screen")
        sw = "".join(f'<span class="sw" style="background:{html.escape(c)}" title="{html.escape(c)}"></span>'
                     for c in (r.get("surfaceColors") or [])[:6] + (r.get("textColors") or [])[:3])
        f1, fb = r.get("h1Font") or {}, r.get("bodyFont") or {}
        links = " ".join(f'<a href="{html.escape(v)}">{k.replace("_", " ")}</a>' for k, v in r["files"].items())
        cards.append(f"""<article class="card {e('status').lower()}">
  {f'<a href="{html.escape(img)}"><img src="{html.escape(img)}" alt="First screen of {e("url")}"></a>' if img else f'<div class="blocked">{e("status")} {e("error")}</div>'}
  <h2><a href="{e('url')}">{e('title') or e('url')}</a></h2>
  <p class="h1">{e('h1')}</p>
  <p class="meta">h1: {html.escape(f1.get('family', '')[:60])} {html.escape(f1.get('size', ''))} / body: {html.escape(fb.get('family', '')[:60])} {html.escape(fb.get('size', ''))}</p>
  <p class="sws">{sw}</p>
  <p><b>Why</b> {e('why')}</p><p><b>Borrow</b> {e('borrow')}</p><p><b>Avoid</b> {e('avoid')}</p>
  <p class="files">{links}</p></article>""")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reference board</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1f;--card:#fff;--muted:#6b6b70;--line:#e3e1dc}}
@media (prefers-color-scheme:dark){{:root{{--bg:#121214;--fg:#ededef;--card:#1c1c1f;--muted:#9a9aa0;--line:#2c2c30}}}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{display:grid;gap:20px;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));max-width:1400px;margin:auto}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.card img{{width:100%;height:auto;border-radius:6px;border:1px solid var(--line)}}
h1{{max-width:1400px;margin:0 auto 16px;font-size:22px}} h2{{font-size:16px;margin:10px 0 4px}}
.meta,.files,.h1{{color:var(--muted);font-size:13px;margin:4px 0}} .sw{{display:inline-block;width:22px;height:22px;border-radius:4px;margin-right:4px;border:1px solid var(--line)}}
.blocked{{padding:40px;text-align:center;color:var(--muted)}} a{{color:inherit}}
</style></head><body><h1>Reference board ({sum(r['status'] in ('ok', 'approved') for r in recs)} of {len(recs)} usable)</h1><main>
{''.join(cards)}</main></body></html>"""
    (out / "board.html").write_text(page)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mobile", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--render-only", action="store_true",
                    help="rebuild board.html from --file records (refs.json) without capturing again")
    a = ap.parse_args()
    refs = [{"url": u} for u in a.urls]
    if a.file:
        try:
            refs += json.load(open(a.file))
        except (OSError, json.JSONDecodeError) as e:
            print(f"cannot read {a.file}: {e}", file=sys.stderr)
            return 2
    refs = [r for r in refs if str(r.get("url", "")).startswith(("http://", "https://"))]
    if a.render_only:
        out = Path(a.out)
        missing = [f for r in refs for f in (r.get("files") or {}).values() if not (out / f).is_file()]
        if not refs or any("status" not in r for r in refs) or missing:
            print(f"--render-only needs refs.json records from a capture run; missing images: {missing[:3]}", file=sys.stderr)
            return 2
        board(refs, out)
        print(f"board re-rendered: {out / 'board.html'} ({len(refs)} records, no new capture)")
        return 0
    if not refs:
        print("no http(s) URLs given", file=sys.stderr)
        return 2
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        mctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True)
        page = ctx.new_page()
        recs = [capture(page, mctx, r, out, i + 1, a.full, a.mobile) for i, r in enumerate(refs)]
        browser.close()
    for r in recs:  # stealth retries run after the plain browser closes (two sync drivers cannot nest)
        name = r.pop("_retry", None)
        if not name:
            continue
        box = stealth_capture(r["url"], out / f"{name}.png") or {}
        if box.get("shot"):
            r.update({k: v for k, v in box["info"].items() if k != "sample"}, status="ok", via="stealth browser")
            r.pop("error", None)
            r["files"]["first_screen"] = f"{name}.png"
        else:
            r["error"] = box.get("error", "challenge page; stealth retry did not get through")
    (out / "refs.json").write_text(json.dumps(recs, indent=1))
    board(recs, out)
    bad = [r for r in recs if r["status"] in ("BLOCKED", "FAILED", "LISTING")]
    for r in recs:
        print(f"{r['status']:8} {r['url']}  {r.get('error', '')}")
    print(f"board: {out / 'board.html'} ({len(recs) - len(bad)} of {len(recs)} captured)")
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
