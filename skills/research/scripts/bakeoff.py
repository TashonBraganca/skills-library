#!/usr/bin/env python3
"""Fetcher bake-off. Runs each fetcher on each URL and records success, text size and seconds.

  bakeoff.py --out /tmp/bakeoff.json
  bakeoff.py --out /tmp/bakeoff.json --only arxiv-html,github-readme

A fetch counts as a success only if fetch.py's validity check passes (HTTP 2xx, enough text,
no CAPTCHA, login, challenge or JavaScript wall) AND the text contains a token that only the
real page has (column "token"). The second check stops a 200 response that holds a stub from
being scored as a win.

Crawl4AI runs from a throwaway venv, never a global install:
  uv venv /tmp/c4a && VIRTUAL_ENV=/tmp/c4a uv pip install crawl4ai
  PLAYWRIGHT_BROWSERS_PATH=/tmp/c4a-pw /tmp/c4a/bin/playwright install chromium-headless-shell
  C4A_PYTHON=/tmp/c4a/bin/python C4A_PW=/tmp/c4a-pw python3 bakeoff.py --out r.json
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch  # noqa: E402
from _common import looks_blocked  # noqa: E402

# (key, category, url, token that only the real page contains)
URLS = [
    ("spa-hn-algolia", "JS-heavy SPA", "https://hn.algolia.com/?q=interpretability&type=story&dateRange=pastYear", "points"),
    ("spa-tradingview", "JS-heavy SPA", "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/", "Symbol"),
    ("cf-nowsecure", "Cloudflare test page", "https://nowsecure.nl/", "passed"),
    ("cf-g2", "Cloudflare-protected", "https://www.g2.com/products/github-copilot/reviews", "Copilot"),
    ("arxiv-html", "arXiv HTML paper", "https://arxiv.org/html/2310.01405", "Representation Engineering"),
    ("medium", "Medium post", "https://medium.com/@etredal/getting-started-with-mechanistic-interpretability-9c750b0e83e2", "Mech Interp"),
    ("substack", "Substack post", "https://www.oneusefulthing.org/p/which-ai-should-i-use-superpowers", "context window"),
    ("github-readme", "GitHub README", "https://github.com/D4Vinci/Scrapling", "Scrapling"),
    ("docs-uv", "docs site", "https://docs.astral.sh/uv/concepts/projects/init/", "pyproject.toml"),
    ("reddit-thread", "Reddit thread", "https://www.reddit.com/r/ClaudeCode/comments/1w0irg8/are_better_models_replacing_superpowers/", "noob trap"),
    ("x-post", "X post", "https://x.com/karpathy/status/1617979122625712128", "hottest new programming language"),
    ("youtube", "YouTube page", "https://www.youtube.com/watch?v=ZCxQ_IhMHPY", "superposition"),
    ("news-guardian", "news site", "https://www.theguardian.com/technology/artificialintelligenceai", "artificial intelligence"),
    ("forum-pytorch", "forum (Discourse)", "https://discuss.pytorch.org/t/how-do-hooks-work/83109", "hook"),
    ("pdf-attention", "PDF", "https://arxiv.org/pdf/1706.03762", "Attention Is All You Need"),
]

C4A_SNIPPET = r"""
import asyncio, json, sys, time
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
async def main(url):
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False, page_timeout=45000))
        md = r.markdown
        text = getattr(md, "raw_markdown", None) or (md if isinstance(md, str) else "")
        print("@@JSON@@" + json.dumps({"success": r.success, "status": r.status_code, "text": text, "err": (r.error_message or "")[:200]}))
asyncio.run(main(sys.argv[1]))
"""


def f_crawl4ai(url, min_chars, timeout):
    t0 = time.time()
    py = os.environ.get("C4A_PYTHON")
    if not py or not os.path.exists(py):
        return fetch.result("crawl4ai", t0, reason="not run: C4A_PYTHON venv missing")
    try:
        env = dict(os.environ)
        if os.environ.get("C4A_PW"):
            env["PLAYWRIGHT_BROWSERS_PATH"] = os.environ["C4A_PW"]
        p = subprocess.run([py, "-c", C4A_SNIPPET, url], capture_output=True, text=True, timeout=timeout + 40, env=env)
    except subprocess.TimeoutExpired:
        return fetch.result("crawl4ai", t0, reason="timeout")
    line = next((l for l in p.stdout.splitlines() if l.startswith("@@JSON@@")), None)
    if not line:
        return fetch.result("crawl4ai", t0, reason=("no output: " + (p.stderr.strip().splitlines() or [""])[-1])[:160])
    d = json.loads(line[8:])
    if not d["success"]:
        return fetch.result("crawl4ai", t0, status=d["status"], reason=d["err"] or "crawl failed")
    bad, why = looks_blocked(d["text"], d["status"], min_chars)
    if bad:
        return fetch.result("crawl4ai", t0, status=d["status"], text=d["text"][:200], reason=why)
    return fetch.result("crawl4ai", t0, ok=True, status=d["status"], text=d["text"])


HERE = os.path.dirname(os.path.abspath(__file__))


def f_cli(name):
    """Run `fetch.py --chain NAME --no-route` as a child process with a hard kill timeout,
    so one hung browser cannot stall the whole run."""
    def run(url, min_chars, timeout):
        t0 = time.time()
        cmd = [sys.executable, os.path.join(HERE, "fetch.py"), url, "--chain", name, "--no-route", "--json",
               "--max-chars", "0", "--timeout", str(timeout), "--min-chars", str(min_chars)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            out, err = proc.communicate(timeout=timeout + 60)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, 9)  # kills the browser the fetcher spawned, too
            proc.communicate()
            return fetch.result(name, t0, reason=f"hard timeout after {timeout + 60}s")
        p = subprocess.CompletedProcess(cmd, proc.returncode, out, err)
        try:
            d = json.loads(p.stdout)
        except ValueError:
            return fetch.result(name, t0, reason="no JSON: " + p.stderr.strip()[-100:])
        if d.get("ok"):
            return fetch.result(name, t0, ok=True, status=d.get("status"), text=d["text"])
        att = (d.get("attempts") or [{}])[0]
        return fetch.result(name, t0, status=att.get("status"), reason=att.get("reason", "failed"))
    return run


FETCHERS = {n: f_cli(n) for n in fetch.FETCHERS}
FETCHERS["crawl4ai"] = f_crawl4ai


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", help="comma list of URL keys")
    ap.add_argument("--fetchers", default="scrapling,stealthy,jina,urllib,crawl4ai")
    ap.add_argument("--min-chars", type=int, default=500)
    ap.add_argument("--timeout", type=int, default=45)
    a = ap.parse_args()
    only = set(filter(None, a.only.split(",")))
    names = a.fetchers.split(",")
    results = []
    for key, cat, url, token in URLS:
        if only and key not in only:
            continue
        row = {"key": key, "category": cat, "url": url, "token": token, "fetchers": {}}
        for n in names:
            r = FETCHERS[n](url, a.min_chars, a.timeout)
            has = bool(r["ok"] and token.lower() in r["text"].lower())
            row["fetchers"][n] = {"valid": r["ok"], "real": has, "chars": len(r["text"]) if r["ok"] else 0,
                                  "seconds": r["seconds"], "status": r["status"], "reason": r["reason"]}
            print(f"{key:16} {n:10} valid={r['ok']!s:5} real={has!s:5} chars={len(r['text']) if r['ok'] else 0:7} "
                  f"{r['seconds']:6.1f}s {r['reason'][:70]}", flush=True)
            time.sleep(2 if n == "jina" else 0.5)
        # the real default: fetch.py with routing and the default chain
        t0 = time.time()
        p = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch.py"), url,
                            "--json", "--max-chars", "0", "--timeout", str(a.timeout)], capture_output=True, text=True)
        try:
            d = json.loads(p.stdout)
        except ValueError:
            d = {"ok": False}
        has = bool(d.get("ok") and token.lower() in d.get("text", "").lower())
        row["default"] = {"valid": bool(d.get("ok")), "real": has, "chars": d.get("chars", 0), "via": d.get("via") or None, "attempts": d.get("attempts"),
                          "seconds": round(time.time() - t0, 1)}
        print(f"{key:16} {'DEFAULT':10} valid={row['default']['valid']!s:5} real={has!s:5} chars={row['default']['chars']:7} "
              f"{row['default']['seconds']:6.1f}s via {row['default']['via']}", flush=True)
        results.append(row)
        with open(a.out, "w") as f:
            json.dump(results, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
