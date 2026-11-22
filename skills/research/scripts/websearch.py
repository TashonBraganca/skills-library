#!/usr/bin/env python3
"""Free web search through Brave Search or Yahoo Search HTML pages. No key.

  websearch.py "site:x.com mechanistic interpretability" --since 12m
  websearch.py "\\"why I stopped using\\" langchain" --since 6m --limit 15
  websearch.py "site:reddit.com/r/ClaudeAI superpowers" --since 90d --format jsonl
  websearch.py "site:producthunt.com ai code review"

Results are LEADS. A snippet is not evidence: open the URL (fetch.py) and read it.
The snippet date, when Brave shows one, is printed; the page's own date still has to be checked.
Engines: brave (shows result dates, but answers HTTP 429 once an IP searches a lot) and
yahoo (Bing-backed, steadier, no result dates). The default `--engine auto` tries Brave once,
then Yahoo, and prints which engine answered.
Operators that work: site:, quotes, -term, filetype:. --since uses Brave's freshness filter
(day, week, month, year) and Yahoo's (day, week, month only). Yahoo ignores windows over a month,
so check dates on the pages themselves.
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import clip, emit, log, looks_blocked, md_escape, parse_since  # noqa: E402
import datetime as dt  # noqa: E402

BLOCK_START = re.compile(r'<div class="snippet[^"]*"[^>]*data-type="web"')


def freshness(since):
    if not since:
        return ""
    days = (dt.date.today() - since).days
    return "pd" if days <= 1 else "pw" if days <= 7 else "pm" if days <= 31 else "py" if days <= 366 else ""


def parse_results(page):
    starts = [m.start() for m in BLOCK_START.finditer(page)]
    out = []
    for i, st in enumerate(starts):
        blk = page[st: starts[i + 1] if i + 1 < len(starts) else st + 8000]
        a = re.search(r'<a href="(https?://[^"]+)"', blk)
        t = re.search(r'class="title[^"]*"[^>]*title="([^"]*)"', blk) or re.search(r'class="title[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        s = re.search(r'class="content[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        if not a or not t:
            continue
        snippet = re.sub(r"<[^>]+>", "", s.group(1)) if s else ""
        snippet = html.unescape(re.sub(r"\s+", " ", snippet)).strip()
        date = ""
        m = re.match(r"^(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4}|\d+ (?:hours?|days?|weeks?|months?) ago)\s*-\s*", snippet)
        if m:
            date, snippet = m.group(1), snippet[m.end():]
        out.append({"title": html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip(),
                    "url": html.unescape(a.group(1)), "snippet": snippet, "date": date})
    return out


def yahoo_freshness(since):
    if not since:
        return ""
    days = (dt.date.today() - since).days
    return "d" if days <= 1 else "w" if days <= 7 else "m" if days <= 31 else ""


def parse_yahoo(page):
    out = []
    for blk in re.split(r'<li[^>]*><div class="dd[^"]*algo-sr', page)[1:]:
        a = re.search(r'/RU=([^/]+)/RK=', blk)
        t = re.search(r'<h3[^>]*>(.*?)</h3>', blk, re.S)
        s = re.search(r'class="compText[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        if not a or not t:
            continue
        url = urllib.parse.unquote(a.group(1))
        title = html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip()
        snippet = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s.group(1) if s else ""))).strip()
        date = ""
        m = re.match(r"^((?:[A-Z][a-z]{2} \d{1,2}, \d{4})|(?:\d{1,2} \w+ \d{4})|(?:\d+ (?:hours?|days?|weeks?|months?) ago))\s*[·\-]\s*", snippet)
        if m:
            date, snippet = m.group(1), snippet[m.end():]
        out.append({"title": title, "url": url, "snippet": snippet, "date": date})
    return out


def search_yahoo(query, since):
    params = {"p": query}
    f = yahoo_freshness(since)
    if f:
        params["btf"] = f
    url = "https://search.yahoo.com/search?" + urllib.parse.urlencode(params)
    try:
        from _common import scrapling
        Fetcher, _ = scrapling()
        r = Fetcher.get(url, timeout=30, stealthy_headers=True)
        status, page = r.status, (r.body.decode("utf8", "replace") if isinstance(r.body, bytes) else str(r.body))
    except Exception as e:
        return [], f"fetch error {type(e).__name__}: {str(e)[:100]}"
    if status != 200:
        return [], f"HTTP {status}"
    rows = parse_yahoo(page)
    return rows, "" if rows else "0 results parsed"


def search(query, since, tries=3):
    params = {"q": query}
    f = freshness(since)
    if f:
        params["tf"] = f
    url = "https://search.brave.com/search?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        # Brave answers 429 to Python's urllib (TLS fingerprint) but 200 to Scrapling's browser-like client.
        try:
            from _common import scrapling
            Fetcher, _ = scrapling()
            r = Fetcher.get(url, timeout=30, stealthy_headers=True)
            status, page = r.status, (r.body.decode("utf8", "replace") if isinstance(r.body, bytes) else str(r.body))
        except Exception as e:
            return [], f"fetch error {type(e).__name__}: {str(e)[:100]}"
        if status == 200:
            rows = parse_results(page)
            if rows:
                return rows, ""
            bad, why = looks_blocked(re.sub(r"<[^>]+>", " ", page)[:3000], 200, 50)
            return [], "0 results parsed" + (f" ({why})" if bad else "")
        if status == 429 and attempt < tries - 1:
            wait = 6 * (attempt + 1)
            log(f"[websearch] 429 from Brave, waiting {wait}s")
            time.sleep(wait)
            continue
        return [], f"HTTP {status}"
    return [], "rate limited"


def x_date(url):
    """x.com status ids are snowflakes: the post time is inside the id."""
    m = re.search(r"(?:x|twitter)\.com/[^/]+/status/(\d+)", url)
    if not m:
        return ""
    ms = (int(m.group(1)) >> 22) + 1288834974657
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


def run(query, since, engine):
    """Returns (rows, engine_used, error)."""
    errs = []
    if engine in ("auto", "brave"):
        rows, err = search(query, since, tries=1 if engine == "auto" else 3)
        if rows:
            return rows, "brave", ""
        errs.append(f"brave: {err}")
    if engine in ("auto", "yahoo"):
        rows, err = search_yahoo(query, since)
        if rows:
            return rows, "yahoo", "; ".join(errs)
        errs.append(f"yahoo: {err}")
    return [], engine, "; ".join(errs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--since", default="", help="12m, 90d, 1y or YYYY-MM-DD; rounded to Brave's day/week/month/year filter")
    ap.add_argument("--engine", choices=["auto", "brave", "yahoo"], default="auto")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--format", choices=["md", "jsonl"], default="md")
    a = ap.parse_args()
    since = parse_since(a.since)
    rows, used, err = run(a.query, since, a.engine)
    if not rows:
        log(f"[websearch] no results: {err}. Reword the query, drop operators, or widen --since. "
            f"Zero results here is not proof that nothing exists.")
        return 2
    if rows and err:
        log(f"[websearch] fallback: {err}")
    if since and used == "yahoo" and not yahoo_freshness(since):
        log("[websearch] requested window has no Yahoo server filter; verify dates on opened sources")
    for r in rows:
        d = x_date(r["url"])
        if d:
            r["date"] = d + " (from post id)"
        r["engine"] = used
        r["date_verified"] = bool(d)
    if since:  # Yahoo cannot filter long windows; x.com post dates are exact, so enforce them here
        rows = [r for r in rows if not r["date"][:10].count("-") == 2 or r["date"][:10] >= since.isoformat()]
    if not rows:
        log("[websearch] no returned candidates survived the date filter")
        return 2
    rows = rows[: a.limit]
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0
    print(f"# Web search: {a.query} (engine {used}" + (f", freshness {freshness(since) if used == 'brave' else yahoo_freshness(since) or 'none'}" if since else "") + f"), {len(rows)} results\n")
    for i, r in enumerate(rows, 1):
        print(f"{i}. [{md_escape(clip(r['title'], 110))}]({r['url']})" + (f" , {r['date']}" if r["date"] else ""))
        if r["snippet"]:
            print(f"    {clip(r['snippet'], 240)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
