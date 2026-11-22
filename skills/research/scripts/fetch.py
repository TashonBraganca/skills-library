#!/usr/bin/env python3
"""Fetch any URL as clean text. Tries several fetchers and rejects block pages.

  fetch.py https://example.com/post
  fetch.py https://arxiv.org/abs/2310.01405 --max-chars 6000
  fetch.py https://site.com/spa --chain stealthy,jina        # choose the chain
  fetch.py https://site.com/doc.pdf                          # PDFs go through Jina Reader
  fetch.py URL --json                                        # one JSON object: ok, via, status, chars, text
  fetch.py URL --save /tmp/page.txt                          # keep the full text, print a clipped copy

Default chain, from the 2026-11-18 bake-off (archive/fetch-bakeoff-2026-11-18.md):
  scrapling (fast HTTP)  ->  jina (Jina Reader, renders JS)  ->  stealthy (headless browser)  ->  urllib
A fetcher counts only if the page passes the validity check: HTTP 2xx, enough text,
and no CAPTCHA, login, challenge or "enable JavaScript" wall.

Special routes (skip with --no-route):
  x.com / twitter.com status URL  -> api.fxtwitter.com (the post text, counts and date)
  reddit.com thread URL           -> reddit.py thread (Arctic Shift archive)
  youtube.com / youtu.be video    -> youtube.py (metadata and transcript)

Exit code 0 = valid content printed, 2 = every fetcher failed (reasons on stderr).
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import BROWSER_UA, http_get, log, looks_blocked  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CHAIN = ["scrapling", "jina", "stealthy", "urllib"]


# ---------------------------------------------------------------- html to text

class TextExtractor(HTMLParser):
    DROP = {"script", "style", "noscript", "svg", "template", "iframe", "head", "nav", "footer", "aside", "form", "button"}
    BLOCK = {"p", "div", "section", "article", "main", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6",
             "pre", "blockquote", "table", "ul", "ol", "dt", "dd", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.drop = 0
        self.stack = []
        self.buf = {"all": [], "article": [], "main": []}
        self.open = {"article": 0, "main": 0}
        self.heading = None

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        if tag in self.DROP and tag != "head":
            self.drop += 1
            return
        if tag == "head":
            self.drop += 1
            return
        if tag in ("article", "main"):
            self.open[tag] += 1
        if tag in self.BLOCK:
            self._put("\n")
            if tag[0] == "h" and len(tag) == 2:
                self._put("\n" + "#" * int(tag[1]) + " ")
            if tag == "li":
                self._put("- ")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in self.DROP:
            self.drop = max(0, self.drop - 1)
            return
        if tag in ("article", "main"):
            self.open[tag] = max(0, self.open[tag] - 1)
        if tag in self.BLOCK:
            self._put("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.drop:
            return
        self._put(data)

    def _put(self, s):
        self.buf["all"].append(s)
        for k in ("article", "main"):
            if self.open[k]:
                self.buf[k].append(s)


def tidy(s):
    s = html.unescape(s)
    s = re.sub(r"[ \t ]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def html_to_text(page):
    p = TextExtractor()
    try:
        p.feed(page)
    except Exception:
        pass
    cands = [tidy("".join(p.buf["article"])), tidy("".join(p.buf["main"])), tidy("".join(p.buf["all"]))]
    for c in cands[:2]:
        if len(c) >= 800:
            return tidy(p.title), c
    return tidy(p.title), cands[2]


def js_shell(page, text):
    """A near-empty app shell: the content needs JavaScript."""
    return len(text) < 600 and re.search(r'id="(root|__next|app)"|<noscript>.*enable javascript', page, re.I | re.S)


# ---------------------------------------------------------------- fetchers
# Each returns dict(ok, via, status, title, text, reason, seconds).

def result(via, t0, ok=False, status=None, title="", text="", reason=""):
    return {"ok": ok, "via": via, "status": status, "title": title, "text": text, "reason": reason,
            "seconds": round(time.time() - t0, 2)}


def judge(via, t0, status, page_html, min_chars, is_markdown=False):
    if page_html[:4] == b"%PDF" if isinstance(page_html, bytes) else False:
        return result(via, t0, status=status, reason="PDF body, not text (use jina, or install poppler for pdftotext)")
    if isinstance(page_html, bytes):
        page_html = page_html.decode("utf8", "replace")
    if is_markdown:
        title, text = "", page_html.strip()
    else:
        title, text = html_to_text(page_html)
    bad, why = looks_blocked(text, status, min_chars)
    if not bad and not is_markdown and js_shell(page_html, text):
        bad, why = True, "empty JavaScript app shell"
    if bad:
        return result(via, t0, status=status, title=title, text=text[:200], reason=why)
    return result(via, t0, ok=True, status=status, title=title, text=text)


def f_scrapling(url, min_chars, timeout):
    t0 = time.time()
    try:
        from _common import scrapling
        Fetcher, _ = scrapling()
        r = Fetcher.get(url, timeout=timeout, stealthy_headers=True, follow_redirects=True)
        body = r.body if isinstance(r.body, bytes) else str(r.body).encode()
        return judge("scrapling", t0, r.status, body, min_chars)
    except Exception as e:
        return result("scrapling", t0, reason=f"{type(e).__name__}: {str(e)[:120]}")


def f_stealthy(url, min_chars, timeout):
    t0 = time.time()
    try:
        from _common import scrapling
        _, StealthyFetcher = scrapling()
        r = StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=timeout * 1000, disable_resources=False)
        body = r.body if isinstance(r.body, bytes) else str(r.body).encode()
        return judge("stealthy", t0, r.status, body, min_chars)
    except Exception as e:
        return result("stealthy", t0, reason=f"{type(e).__name__}: {str(e)[:120]}")


def f_jina(url, min_chars, timeout):
    t0 = time.time()
    status, body, _ = http_get("https://r.jina.ai/" + url, timeout=timeout, retries=1, backoff=4,
                               headers={"Accept": "text/plain", "X-Return-Format": "markdown", "X-No-Cache": "true"})  # no-cache: Jina otherwise serves stale snapshots
    text = body.decode("utf8", "replace")
    if "Target URL returned error" in text[:600] or "requires captcha" in text[:600].lower():
        return result("jina", t0, status=status, reason=text[:160].replace("\n", " "))
    # Jina prefixes "Title:, URL Source:, Markdown Content:". Keep the title, drop the header.
    title = ""
    m = re.match(r"Title: (.*)\n", text)
    if m:
        title = m.group(1).strip()
    if "Markdown Content:" in text[:800]:
        text = text.split("Markdown Content:", 1)[1].strip()
    r = judge("jina", t0, status, text, min_chars, is_markdown=True)
    r["title"] = r["title"] or title
    return r


def f_urllib(url, min_chars, timeout):
    t0 = time.time()
    status, body, _ = http_get(url, timeout=timeout, retries=1, backoff=3,
                               headers={"User-Agent": BROWSER_UA, "Accept": "text/html,*/*;q=0.8",
                                        "Accept-Language": "en-US,en;q=0.9"})
    if status == 0:
        return result("urllib", t0, reason=body.decode("utf8", "replace")[:120])
    return judge("urllib", t0, status, body, min_chars)


FIRECRAWL_BIN = shutil.which("firecrawl-local") or os.path.expanduser("~/.cargo/bin/firecrawl-local")


def f_firecrawl(url, min_chars, timeout):
    """Firecrawl Local (free, AGPL, runs on this machine). FIRECRAWL_CLOUD=off: no cloud fallback, no
    install counting. Its success flag is not trusted: the text goes through the same block-page judge."""
    t0 = time.time()
    if not os.path.exists(FIRECRAWL_BIN):
        return result("firecrawl", t0, reason="firecrawl-local not installed (cargo install firecrawl-local)")
    env = {k: v for k, v in os.environ.items() if k != "FIRECRAWL_API_KEY"}
    env["FIRECRAWL_CLOUD"] = "off"
    try:
        p = subprocess.run([FIRECRAWL_BIN, "scrape", url, "--timeout", str(timeout * 1000)],
                           capture_output=True, text=True, timeout=timeout + 30, env=env)
    except subprocess.TimeoutExpired:
        return result("firecrawl", t0, reason="timeout")
    try:
        d = json.loads(p.stdout)
        if isinstance(d, list):
            if not d:
                return result("firecrawl", t0, reason="empty response")
            d = d[0]
        if p.returncode != 0 or d.get("success") is False:
            return result("firecrawl", t0, reason=f"firecrawl reported failure (exit {p.returncode}, success={d.get('success')})")
        data = d.get("data", d)
        md = data.get("markdown") or ""
        meta = data.get("metadata") or {}
        status = meta.get("statusCode") or meta.get("status_code")
    except (ValueError, AttributeError):
        return result("firecrawl", t0, reason=f"unparseable output (exit {p.returncode}): {p.stderr.strip()[-120:]}")
    if not md:
        return result("firecrawl", t0, status=status, reason="no markdown: " + (p.stderr.strip()[-120:] or "empty"))
    return judge("firecrawl", t0, status, md, min_chars, is_markdown=True)


FETCHERS = {"scrapling": f_scrapling, "stealthy": f_stealthy, "jina": f_jina, "urllib": f_urllib, "firecrawl": f_firecrawl}


def fetch_chain(url, chain, min_chars, timeout):
    tried = []
    for name in chain:
        r = FETCHERS[name](url, min_chars, timeout)
        tried.append(r)
        if r["ok"]:
            return r, tried
        log(f"[fetch] {name} rejected: {r['reason']} ({r['seconds']}s)")
    return None, tried


# ---------------------------------------------------------------- special routes

def route(url):
    u = urllib.parse.urlparse(url)
    host = (u.hostname or "").lower()
    if host in ("x.com", "twitter.com", "www.x.com", "www.twitter.com", "mobile.twitter.com"):
        m = re.search(r"^/([^/]+)/status/(\d+)", u.path)
        if m:
            return "x", m.groups()
    if host.endswith("reddit.com") and "/comments/" in u.path:
        return "reddit", url
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"):
        return "youtube", url
    return None, None


def run_script(name, args):
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, name)] + args,
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return 2, "", f"{name} exceeded the 60-second route deadline"
    return p.returncode, p.stdout, p.stderr


def routed_fetch(kind, arg, args):
    t0 = time.time()
    if kind == "x":
        user, sid = arg
        status, body, _ = http_get(f"https://api.fxtwitter.com/{user}/status/{sid}", retries=2, backoff=3)
        try:
            d = json.loads(body)["tweet"]
        except Exception:
            return None, f"fxtwitter returned HTTP {status}: {body[:100]!r}"
        lines = [f"@{d['author']['screen_name']} ({d['author'].get('name')}), {d.get('created_at')}",
                 f"{d.get('likes')} likes, {d.get('retweets')} reposts, {d.get('replies')} replies, {d.get('views')} views",
                 "", d.get("text", "")]
        if d.get("quote"):
            lines += ["", f"Quoting @{d['quote']['author']['screen_name']}: {d['quote'].get('text', '')}"]
        for m in (d.get("media") or {}).get("all", [])[:4]:
            lines.append(f"[media: {m.get('type')} {m.get('url')}]")
        text = "\n".join(lines)
        return result("fxtwitter", t0, ok=len(d.get("text", "")) > 0, status=status, title=f"x.com/{user}/{sid}", text=text), ""
    if kind == "reddit":
        code, out, err = run_script("reddit.py", ["thread", arg, "--limit", "12", "--pages", "1"])
        if code in (0, 3) and out.strip():
            return {**result("reddit.py (Arctic Shift)", t0, ok=True, status=200, title="reddit thread", text=out),
                    "partial": code == 3, "diagnostic": err.strip()}, ""
        return None, "reddit.py failed: " + err[-200:]
    if kind == "youtube":
        code, out, err = run_script("youtube.py", ["transcript", arg, "--max-chars", str(args.max_chars)])
        if code == 0 and len(out) > 200:
            return result("youtube.py", t0, ok=True, status=200, title="youtube video", text=out), ""
        return None, "youtube.py failed: " + err[-200:]
    return None, "unknown route"


def print_links(url, pattern, timeout):
    """Owner pages link the report, model card, code and data. Page text drops hrefs, so list them."""
    import urllib.parse as up
    from html.parser import HTMLParser
    status, body, _ = http_get(url, headers={"User-Agent": BROWSER_UA}, timeout=timeout, retries=1)
    if status != 200:
        log(f"[links] HTTP {status}; try a browser route or the raw page by hand")
        return 2

    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links, self.cur = [], None

        def handle_starttag(self, tag, attrs):
            if tag == "a" and dict(attrs).get("href"):
                self.cur = [up.urljoin(url, dict(attrs)["href"]), ""]

        def handle_data(self, d):
            if self.cur is not None:
                self.cur[1] += d

        def handle_endtag(self, tag):
            if tag == "a" and self.cur is not None:
                self.links.append((self.cur[0], " ".join(self.cur[1].split())))
                self.cur = None
    p = P()
    p.feed(body.decode("utf8", "replace"))
    rx = re.compile(pattern, re.I)
    seen = set()
    for href, text in p.links:
        if href in seen or href.startswith(("javascript:", "mailto:")) or not rx.search(href + " " + text):
            continue
        seen.add(href)
        print(f"{href}\t{text[:100]}")
    log(f"[links] {len(seen)} link(s) from {url}")
    return 0 if seen else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--chain", default=",".join(DEFAULT_CHAIN), help="comma list of: scrapling, stealthy, jina, urllib, firecrawl")
    ap.add_argument("--min-chars", type=int, default=500, help="shorter text counts as a failed fetch")
    ap.add_argument("--max-chars", type=int, default=12000, help="clip printed text (0 = no clip)")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", help="write the full text to this path")
    ap.add_argument("--no-route", action="store_true", help="skip the x.com, reddit and youtube special routes")
    ap.add_argument("--links", nargs="?", const=".", metavar="REGEX",
                    help="print the page's links (resolved href and anchor text), optionally filtered by REGEX, and exit")
    a = ap.parse_args()

    if a.links:
        return print_links(a.url, a.links, a.timeout)
    chain = [c.strip() for c in a.chain.split(",") if c.strip()]
    bad = [c for c in chain if c not in FETCHERS]
    if bad:
        log(f"unknown fetcher(s) {bad}; choose from {list(FETCHERS)}")
        return 2
    url = a.url if "://" in a.url else "https://" + a.url

    r, tried = None, []
    kind = None
    if not a.no_route:
        kind, arg = route(url)
        if kind:
            r, why = routed_fetch(kind, arg, a)
            if r and r["ok"]:
                tried.append(r)
            else:
                log(f"[fetch] {kind} route failed ({why}). Not falling back to a generic page; "
                    f"pass --no-route to request generic extraction.")
                tried.append(result(kind, time.time(), reason=why))
                r = None
    if r is None and (a.no_route or not kind):
        r, t2 = fetch_chain(url, chain, a.min_chars, a.timeout)
        tried += t2
    if r is None:
        log("[fetch] ALL FETCHERS FAILED for " + url)
        for t in tried:
            log(f"   {t['via']}: {t['reason']}")
        if a.json:
            print(json.dumps({"ok": False, "url": url, "attempts": [{k: t[k] for k in ("via", "status", "reason", "seconds")} for t in tried]}))
        return 2
    text = r["text"]
    if a.save:
        with open(a.save, "w", encoding="utf8") as f:
            f.write(text)
    shown = text if not a.max_chars or len(text) <= a.max_chars else text[: a.max_chars] + f"\n\n[clipped: {len(text)} chars total]"
    if a.json:
        print(json.dumps({"ok": True, "url": url, "via": r["via"], "status": r["status"], "title": r["title"],
                          "chars": len(text), "seconds": r["seconds"], "text": shown,
                          "partial": r.get("partial", False), "diagnostic": r.get("diagnostic", "")}, ensure_ascii=False))
    else:
        print(f"# {r['title'] or url}\nsource: {url}\nvia: {r['via']} | status {r['status']} | {len(text)} chars | {r['seconds']}s\n")
        if r.get("partial"):
            print(f"PARTIAL: {r.get('diagnostic') or 'part of the content failed to load'}\n")
        print(shown)
    return 3 if r.get("partial") else 0


if __name__ == "__main__":
    sys.exit(main())
