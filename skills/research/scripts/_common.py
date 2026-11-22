"""Shared helpers for the research scripts. Python 3 stdlib only.

HTTP with retry and backoff, gzip handling, date parsing, block-page detection,
and JSON-line output. Every script imports this file from its own folder.
"""
import datetime as dt
import gzip
import json
import re
import sys
import time
import urllib.error
import logging
import urllib.request
import zlib
from email.utils import parsedate_to_datetime

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
API_UA = "skills-library-research/1.0 (personal research helper)"

# Phrases that mean "this is a wall, not the page". Only trusted on short pages.
BLOCK_PATTERNS = [
    r"just a moment\.\.\.",
    r"checking your browser",
    r"verify you are (a )?human",
    r"enable javascript and cookies to continue",
    r"attention required! \| cloudflare",
    r"making sure you.{0,3}re not a bot",
    r"access denied",
    r"request blocked",
    r"unusual traffic from your computer",
    r"are you a robot",
    r"captcha",
    r"press and hold",
    r"sign in to continue",
    r"log in to (continue|view)",
    r"you've been blocked",
    r"network security",
    r"anomaly in the request",
    r"403 forbidden",
    r"429 too many requests",
    r"rate exceeded",
    r"something went wrong\. try again",
    r"javascript is (not available|disabled)",
    r"please enable javascript",
]
BLOCK_RE = re.compile("|".join(BLOCK_PATTERNS), re.I)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def emit(obj):
    """One JSON object per line on stdout."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def looks_blocked(text, status=200, min_chars=400):
    """Return (blocked, reason). Block phrases only count on short pages, so a long
    article that mentions 'captcha' is not flagged."""
    if status is not None and (not 200 <= status < 300 or status == 202):
        return True, f"http status {status}"
    t = (text or "").strip()
    if not t:
        return True, "empty body"
    # A block marker on a short page, or in the first 80 characters of any page, is a wall.
    m = BLOCK_RE.search(t[:500])
    if m and (len(t) < 3000 or m.start() < 80):
        return True, f"possible block page: {m.group(0)!r}"
    if len(t) < min_chars:
        return True, f"too short ({len(t)} chars)"
    return False, ""


def decode_body(raw, headers):
    enc = (headers.get("Content-Encoding") or "").lower()
    if enc == "gzip":
        raw = gzip.decompress(raw)
    elif enc == "deflate":
        try:
            raw = zlib.decompress(raw)
        except zlib.error:
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    return raw


def http_get(url, headers=None, timeout=30, retries=3, backoff=4.0,
             retry_statuses=(422, 429, 500, 502, 503, 504), data=None, method=None):
    """GET (or POST with data) with retry. Returns (status, bytes, headers).
    Retries on network errors and on retry_statuses, honouring Retry-After.
    Never raises on a non-2xx status after retries; returns the last response.
    A Retry-After longer than 15 s is not slept on: the last response comes back so the
    caller can switch routes."""
    h = {"User-Agent": API_UA, "Accept-Encoding": "gzip"}
    if headers:
        h.update(headers)
    last = (0, b"", {})
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=h, data=data, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                max_bytes = 64 * 1024 * 1024  # transport limit, not a content judgement
                raw = r.read(max_bytes + 1)
                if len(raw) > max_bytes:
                    return 0, b"response exceeds 64 MiB; use the original document route", dict(r.headers)
                return r.status, decode_body(raw, r.headers), dict(r.headers)
        except urllib.error.HTTPError as e:
            try:
                body = decode_body(e.read(4096), e.headers)
            except Exception:
                body = b""
            last = (e.code, body, dict(e.headers))
            if e.code not in retry_statuses or attempt == retries:
                return last
            retry_after = e.headers.get("Retry-After")
            wait = backoff * (2 ** attempt)
            if retry_after:
                try:
                    wait = float(retry_after)
                except ValueError:
                    try:
                        wait = parsedate_to_datetime(retry_after).timestamp() - time.time()
                    except (TypeError, ValueError, OverflowError):
                        pass
            wait = max(0, wait)
            if wait > 15:
                log(f"[retry] HTTP {e.code}; retry delay {wait:.0f}s exceeds this call's budget")
                return last
            log(f"[retry] {url[:90]} -> {e.code}, waiting {wait:.0f}s ({attempt + 1}/{retries})")
            time.sleep(wait)
        except Exception as e:  # timeouts, DNS, resets
            last = (0, str(e).encode(), {})
            if attempt == retries:
                return last
            wait = backoff * (2 ** attempt)
            log(f"[retry] {url[:90]} -> {type(e).__name__}, waiting {wait:.0f}s ({attempt + 1}/{retries})")
            time.sleep(min(wait, 90))
    return last


def get_json(url, **kw):
    """Returns (parsed_json_or_None, status, error_string)."""
    status, body, _ = http_get(url, **kw)
    if status != 200:
        return None, status, body[:200].decode("utf8", "replace")
    try:
        return json.loads(body), status, ""
    except ValueError:
        return None, status, "response was not JSON: " + body[:120].decode("utf8", "replace")


def parse_since(s):
    """'12m', '90d', '2w', '1y', or YYYY-MM-DD -> datetime.date. None for ''/None."""
    if not s:
        return None
    s = s.strip().lower()
    today = dt.date.today()
    m = re.fullmatch(r"(\d+)\s*([dwmy])", s)
    if m:
        n, u = int(m.group(1)), m.group(2)
        days = int(round({"d": 1, "w": 7, "m": 30.4375, "y": 365}[u] * n))
        return today - dt.timedelta(days=days)
    return dt.date.fromisoformat(s)


def iso_from_ts(ts):
    try:
        return dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


def clip(text, n):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "..."


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def scrapling():
    """Import Scrapling fetchers and silence its per-request INFO lines. Returns (Fetcher, StealthyFetcher)."""
    from scrapling.fetchers import Fetcher, StealthyFetcher
    for name in ("scrapling", "scrapling.fetchers"):
        logging.getLogger(name).setLevel(logging.WARNING)
    return Fetcher, StealthyFetcher


def coverage(fmt, route, query, **kw):
    """One coverage record per search call, the same shape everywhere: route, query, window, sort, pages
    read, items returned, stop reason (complete, page_cap, error, cursor_remaining) and gaps. A report
    rebuilds its sample table from these lines."""
    rec = {"kind": "coverage", "route": route, "query": query, **kw}
    if fmt == "jsonl":
        emit(rec)
    else:
        print("\nCoverage: " + json.dumps(rec, ensure_ascii=False, default=str))
    return rec
