#!/usr/bin/env python3
"""Read Reddit through the Arctic Shift archive API (free, no key, no login).

Reddit's own site returns 403 or a login page to scripts, and WebFetch is blocked.
Arctic Shift mirrors posts and comments. It lags live Reddit by hours to days, and
removed posts may be missing their text.

  reddit.py search "superpowers" -s ClaudeAI,ClaudeCode --since 6m --min-score 20
  reddit.py search '"claude code"' -s ClaudeAI --since 30d --by score
  reddit.py search "uv|poetry" -s Python --since 12m          # | means OR (one call per term)
  reddit.py thread 1w0irg8 --limit 15                         # id or full reddit URL
  reddit.py thread https://www.reddit.com/r/ClaudeAI/comments/1w0irg8/ --pages 2
  reddit.py subs claudeskill                                  # find subreddits by name prefix
  reddit.py top -s claudeskills --since 90d --by comments     # browse a subreddit, no query
  reddit.py comments "grpo" -s LocalLLaMA --since 6m          # search comment bodies
  reddit.py rules SaaS,startups                               # posting rules before any outreach

Notes
  - search matches the TITLE (fast). --fulltext matches title and body and often times out.
  - A multi-word query is a phrase match. Wrap it in quotes for an exact phrase.
  - The server sleeps hard on bursts: calls are spaced 6 to 8 seconds, and 422 "Timeout"
    answers are retried with backoff. A search across 4 subreddits takes about a minute.
  - Thread URLs are built as https://www.reddit.com/r/<sub>/comments/<id>.
"""
import argparse
import os
import random
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import clip, coverage, emit, http_get, iso_from_ts, log, md_escape, parse_since  # noqa: E402
import json  # noqa: E402

BASE = "https://arctic-shift.photon-reddit.com/api"
_last_call = [0.0]


def paced_get(path, params, pace, tries=5):
    """One Arctic Shift call, spaced from the previous call, retried on 422/429/5xx.
    Returns (json_or_None, error_string)."""
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    err = ""
    for attempt in range(tries):
        wait = _last_call[0] + random.uniform(pace, pace + 2) - time.time()
        if wait > 0:
            time.sleep(wait)
        status, body, _ = http_get(url, timeout=15, retries=0)
        _last_call[0] = time.time()
        if status == 200:
            try:
                d = json.loads(body)
            except ValueError:
                return None, "not JSON: " + body[:100].decode("utf8", "replace")
            if d.get("data") is not None:
                return d, ""
            err = str(d.get("error"))
        else:
            err = f"HTTP {status} {body[:100].decode('utf8', 'replace')}"
            if status in (401, 403, 429):  # blocked or rate limited: hand control back
                log(f"[reddit] {path} {err[:70]}")
                return None, err
        if attempt < tries - 1:
            backoff = min(8 * (attempt + 1), 40)
            log(f"[reddit] {path} {err[:70]} -> retry {attempt + 1}/{tries - 1} after {backoff}s")
            time.sleep(backoff)
        else:
            log(f"[reddit] {path} {err[:70]}")
    return None, err


def thread_url(sub, pid):
    return f"https://www.reddit.com/r/{sub}/comments/{pid}"


def fetch_posts(query, sub, since, limit, pace, fulltext):
    base = {"subreddit": sub, "limit": min(limit, 100)}
    base["query" if fulltext else "title"] = query
    first = {**base, "sort": "desc"}
    if since:
        first["after"] = since.isoformat()
    data, error = paced_get("posts/search", first, pace, tries=1)
    if data is None and since and error.startswith("HTTP 422"):
        # second request keeps the date scope and drops the sort parameter
        params = {**base, "after": since.isoformat()}
        data, error = paced_get("posts/search", params, pace, tries=1)
    return (data["data"], "") if data is not None else ([], error)


def cmd_search(a):
    since = parse_since(a.since)
    subs = [s.strip().strip("/").removeprefix("r/") for s in a.subreddits.split(",") if s.strip()]
    terms = [t.strip() for t in a.query.split("|") if t.strip()]
    seen, rows, failed, capped = set(), [], [], [0]
    for sub in subs:
        for term in terms:
            data, err = fetch_posts(term, sub, since, a.limit, a.pace, a.fulltext)
            if not err and len(data) >= min(a.limit, 100):
                capped[0] += 1
            if err:
                failed.append(f"r/{sub} {term!r}: {err[:80]}")
                continue
            for p in data:
                if p["id"] in seen:
                    continue
                if since and p.get("created_utc", 0) < time.mktime(since.timetuple()):
                    continue
                if a.min_score is not None and (p.get("score") or 0) < a.min_score:
                    continue
                seen.add(p["id"])
                rows.append({
                    "id": p["id"], "subreddit": p.get("subreddit", sub), "date": iso_from_ts(p.get("created_utc")),
                    "score": p.get("score"), "comments": p.get("num_comments"), "title": p.get("title", ""),
                    "text": clip(p.get("selftext", ""), a.text_chars) if p.get("selftext") not in ("[removed]", "[deleted]") else "",
                    "link": p.get("url") if p.get("url") and "reddit.com" not in p.get("url", "") else "",
                    "thread": thread_url(p.get("subreddit", sub), p["id"]),
                })
    for f in failed:
        log(f"[reddit] FAILED {f}")
    if not rows:
        log("[reddit] 0 posts. A title search is literal: try a shorter or quoted term, more subreddits, or --fulltext. "
            "0 posts after failures above means the API timed out, not that nobody posted.")
        return 2
    rows.sort(key=(lambda r: -(r["score"] or 0)) if a.by == "score" else (lambda r: r["date"]), reverse=(a.by != "score"))
    found = len(rows)
    rows = rows[: a.top]
    cov = lambda: coverage(a.format, "reddit/arctic-shift title search", a.query, subreddits=subs, window_from=str(since or ""),
                           sort=a.by, calls=len(subs) * len(terms), failed_calls=len(failed), items=found, shown=len(rows),
                           capped_calls=capped[0], stop="error" if failed else ("capped: raise --limit or narrow the window" if capped[0] else "complete"),
                           gaps=("title and body match" if a.fulltext else "title match only") + "; archive lags live Reddit")
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        cov()
        return 3 if failed else 0
    print(f"# Reddit posts for {a.query!r} in {', '.join('r/' + s for s in subs)}, since {since or 'any date'} "
          f"({len(rows)} shown, sorted by {a.by}, title match, archive may lag live Reddit)\n")
    for r in rows:
        print(f"- {r['date']} | {r['score']} pts | {r['comments']} comments | r/{r['subreddit']} | "
              f"[{md_escape(r['title'])}]({r['thread']})")
        if r["text"]:
            print(f"    {r['text']}")
    if failed:
        print(f"\nIncomplete: {len(failed)} call(s) failed ({'; '.join(failed)[:300]}). Re-run those subreddits.")
    cov()
    return 3 if failed else 0


def parse_thread_id(s):
    m = re.search(r"/comments/([a-z0-9]+)", s)
    if m:
        return m.group(1)
    m = re.fullmatch(r"(?:t3_)?([a-z0-9]{5,8})", s.strip())
    return m.group(1) if m else ""


def cmd_thread(a):
    pid = parse_thread_id(a.thread)
    if not pid:
        log("give a thread id (like 1w0irg8) or a reddit.com/.../comments/<id> URL")
        return 2
    d, err = paced_get("posts/ids", {"ids": pid, "fields": "id,title,selftext,score,num_comments,created_utc,subreddit,url,author"}, a.pace)
    if d is None or not d["data"]:
        log(f"[reddit] post {pid} not found in the archive ({err or 'empty'}). It may be too new or removed.")
        return 2
    post = d["data"][0]
    comments, after = {}, None
    comments_failed = False
    for page in range(a.pages):
        params = {"link_id": pid, "limit": 100, "fields": "id,body,score,author,created_utc,parent_id"}
        if after:
            params["after"] = after
        c, err = paced_get("comments/search", params, a.pace)
        if c is None:
            log(f"[reddit] comments page {page + 1} failed: {err}")
            comments_failed = True
            break
        batch = c["data"]
        if not batch:
            break
        for x in batch:
            comments[x["id"]] = x
        after = max(x["created_utc"] for x in batch)
        if len(batch) < 50:
            break
    allc = list(comments.values())
    if not allc and (post.get("num_comments") or 0) > 0:
        log("[reddit] partial thread: expected comments unavailable. Try again later.")
        comments_failed = True
    removed = ("[removed]", "[deleted]")
    allc = [c for c in allc if c.get("body") not in removed]
    allc.sort(key=lambda c: -(c.get("score") or 0))
    top = allc[: a.limit]
    if a.format == "jsonl":
        emit({"kind": "post", **{k: post.get(k) for k in ("id", "title", "score", "num_comments", "subreddit", "author")},
              "date": iso_from_ts(post.get("created_utc")),
              "text": clip(post.get("selftext", ""), a.post_chars) if a.post_chars else post.get("selftext", ""),
              "text_complete": not a.post_chars or len(post.get("selftext", "")) <= a.post_chars,
              "total_chars": len(post.get("selftext", "") or ""),
              "thread": thread_url(post.get("subreddit", ""), pid), "comments_partial": comments_failed})
        for c in top:
            emit({"kind": "comment", "id": c["id"], "score": c.get("score"), "author": c.get("author"),
                  "date": iso_from_ts(c.get("created_utc")), "top_level": c.get("parent_id", "").startswith("t3_"),
                  "url": thread_url(post.get("subreddit", ""), pid) + "/_/" + c["id"] + "/",
                  "parent_id": c.get("parent_id"),
                  "text": clip(c.get("body", ""), a.text_chars)})
        return 3 if comments_failed else 0
    print(f"# {post.get('title')}")
    print(f"r/{post.get('subreddit')} | {iso_from_ts(post.get('created_utc'))} | {post.get('score')} pts | "
          f"{post.get('num_comments')} comments on Reddit | {len(allc)} loaded from the archive")
    print(thread_url(post.get("subreddit", ""), pid))
    if comments_failed:
        print("PARTIAL: comments failed to load or are missing from the archive.")
    print()
    if post.get("selftext") and post["selftext"] not in removed:
        print(f"Post text: {clip(post['selftext'], a.post_chars) if a.post_chars else post['selftext']}\n")
    print(f"Top {len(top)} comments by score (top-level marked T, replies R):\n")
    for c in top:
        kind = "T" if c.get("parent_id", "").startswith("t3_") else "R"
        print(f"- [{kind}] {c.get('score')} pts, {c.get('author')}, {iso_from_ts(c.get('created_utc'))}: "
              f"{clip(c.get('body', ''), a.text_chars)} "
              f"<{thread_url(post.get('subreddit', ''), pid)}/_/{c['id']}/>")
    return 3 if comments_failed else 0


def cmd_subs(a):
    """Subreddit discovery by name prefix: size and age decide where to search."""
    d, err = paced_get("subreddits/search", {"subreddit_prefix": a.prefix, "limit": min(a.limit, 100)}, a.pace)
    if d is None:
        log(f"[reddit] subreddit search failed: {err}")
        return 3
    rows = []
    for x in d["data"]:
        meta = x.get("_meta") or {}
        rows.append({"subreddit": x.get("display_name"), "posts": meta.get("num_posts"),
                     "comments": meta.get("num_comments"), "first_post": iso_from_ts(meta.get("earliest_post")),
                     "description": clip(x.get("public_description") or x.get("title") or "", 160)})
    if not rows:
        log("[reddit] no subreddit starts with that prefix. Try a shorter prefix or a synonym.")
        return 2
    rows.sort(key=lambda r: -(r["posts"] or 0))
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0
    print(f"# Subreddits starting with {a.prefix!r} (archive counts; subscriber numbers are unreliable)\n")
    for r in rows:
        print(f"- r/{r['subreddit']} | {r['posts']} posts | {r['comments']} comments | since {r['first_post']} | {r['description']}")
    return 0


def cmd_top(a):
    """Every post in one subreddit inside the window, paged by date, ranked locally."""
    since = parse_since(a.since)
    sub = a.subreddit.strip().strip("/").removeprefix("r/")
    rows, before, failed, stop = {}, None, "", "page_cap"
    for _ in range(a.pages):
        params = {"subreddit": sub, "limit": 100, "sort": "desc",
                  "fields": "id,title,score,num_comments,created_utc,selftext,url,link_flair_text"}
        if before:
            params["before"] = before
        if since:
            params["after"] = since.isoformat()
        d, err = paced_get("posts/search", params, a.pace)
        if d is None:
            failed, stop = err, "error"
            break
        batch = [p for p in d["data"] if p["id"] not in rows]
        if not batch:
            stop = "window_reached" if since else "empty_page"
            break
        if len(d["data"]) < 100:
            for p in batch:
                rows[p["id"]] = p
            stop = "window_reached" if since else "end_of_archive"
            break
        for p in batch:
            rows[p["id"]] = p
        before = int(min(p["created_utc"] for p in batch))
    if not rows:
        log(f"[reddit] no posts read ({failed or 'empty window'}).")
        return 3 if failed else 2
    key = {"score": lambda p: -(p.get("score") or 0), "comments": lambda p: -(p.get("num_comments") or 0),
           "date": lambda p: -(p.get("created_utc") or 0)}[a.by]
    ranked = sorted(rows.values(), key=key)[: a.top]
    oldest = iso_from_ts(min(p["created_utc"] for p in rows.values()))
    partial = stop in ("error", "page_cap")
    if a.format == "jsonl":
        for p in ranked:
            emit({"id": p["id"], "stop_reason": stop, "posts_read": len(rows), "oldest_read": oldest, "date": iso_from_ts(p.get("created_utc")), "score": p.get("score"),
                  "comments": p.get("num_comments"), "flair": p.get("link_flair_text"), "title": p.get("title"),
                  "text": clip(p.get("selftext", ""), a.text_chars), "thread": thread_url(sub, p["id"])})
        return 3 if partial else 0
    print(f"# r/{sub}: {len(rows)} posts read back to {oldest}, top {len(ranked)} by {a.by}")
    print(f"Stop reason: {stop}. " + ("PARTIAL: the window was not fully read" + (f" (error: {failed[:80]})" if failed else
          f"; raise --pages above {a.pages}") + "." if partial else "The whole window was read."))
    print()
    for p in ranked:
        flair = f" [{p['link_flair_text']}]" if p.get("link_flair_text") else ""
        print(f"- {iso_from_ts(p.get('created_utc'))} | {p.get('score')} pts | {p.get('num_comments')} comments |{flair} "
              f"[{md_escape(p.get('title', ''))}]({thread_url(sub, p['id'])})")
        if a.text_chars and p.get("selftext") not in (None, "", "[removed]", "[deleted]"):
            print(f"    {clip(p['selftext'], a.text_chars)}")
    return 3 if partial else 0


def cmd_comments(a):
    """Search comment bodies. Comments hold the failure reports and objections titles miss."""
    since = parse_since(a.since)
    subs = [s.strip().strip("/").removeprefix("r/") for s in a.subreddits.split(",") if s.strip()]
    rows, failed = [], []
    for sub in subs:
        # sort=desc and limit=100 make the archive time out on large subreddits (checked
        # 2026-11-19). The default order is newest first, so page by `before` in small pages.
        before, got = None, 0
        for _ in range(a.pages):
            params = {"body": a.query, "subreddit": sub, "limit": 25,
                      "fields": "id,body,score,author,created_utc,link_id,subreddit"}
            if since:
                params["after"] = since.isoformat()
            if before:
                params["before"] = before
            d, err = paced_get("comments/search", params, a.pace, tries=3)
            if d is None:
                failed.append(f"r/{sub} after {got} comments: {err[:80]}")
                break
            if not d["data"]:
                break
            for c in d["data"]:
                got += 1
                if c.get("body") in ("[removed]", "[deleted]") or (a.min_score is not None and (c.get("score") or 0) < a.min_score):
                    continue
                link = (c.get("link_id") or "").removeprefix("t3_")
                rows.append({"id": c["id"], "subreddit": c.get("subreddit", sub), "date": iso_from_ts(c.get("created_utc")),
                             "score": c.get("score"), "author": c.get("author"), "text": clip(c.get("body", ""), a.text_chars),
                             "url": thread_url(c.get("subreddit", sub), link) + "/_/" + c["id"] + "/", "thread_id": link})
            before = int(min(c["created_utc"] for c in d["data"]))
            if len(d["data"]) < 25:
                break
    cov = lambda: coverage(a.format, "reddit/arctic-shift comment search", a.query, subreddits=subs, window_from=str(since or ""),
                           sort=a.by, pages_max=a.pages, items=len(rows), failed=failed,
                           stop="error" if failed else "complete_or_page_cap: raise --pages to be sure")
    for f in failed:
        log(f"[reddit] FAILED {f}")
    if not rows:
        cov()
        log("[reddit] 0 comments." + (" Calls failed, so this is not a null result." if failed else ""))
        return 3 if failed else 2
    rows.sort(key=(lambda r: -(r["score"] or 0)) if a.by == "score" else (lambda r: r["date"]), reverse=(a.by == "date"))
    rows = rows[: a.top]
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 3 if failed else 0
    _c = cov
    print(f"# Reddit comments matching {a.query!r} in {', '.join('r/' + s for s in subs)}, since {since or 'any date'} ({len(rows)} shown)\n")
    for r in rows:
        print(f"- {r['date']} | {r['score']} pts | r/{r['subreddit']} | {r['author']}: {r['text']} <{r['url']}>")
    if failed:
        print(f"\nIncomplete: {'; '.join(failed)[:300]}")
    _c()
    return 3 if failed else 0


def cmd_rules(a):
    """A subreddit's posting rules (archived copy). Read before planning any public participation."""
    subs = ",".join(x.strip().removeprefix("r/") for x in a.subreddits.split(",") if x.strip())
    d, err = paced_get("subreddits/rules", {"subreddits": subs}, a.pace)
    if d is None:
        log(f"[reddit] rules failed: {err}")
        return 3
    if not d["data"]:
        log("[reddit] no rules found in the archive; read the sidebar by hand")
        return 2
    for entry in d["data"]:
        print(f"# r/{entry.get('subreddit')} rules (archived copy; check the live sidebar before posting)\n")
        for r in entry.get("rules") or []:
            print(f"- {r.get('short_name')}: {clip((r.get('description') or '').replace(chr(10), ' '), a.text_chars)}")
        print()
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search post titles in one or more subreddits")
    s.add_argument("query", help="title text; use | for OR; quote for an exact phrase")
    s.add_argument("-s", "--subreddits", required=True, help="comma list, e.g. ClaudeAI,LocalLLaMA")
    s.add_argument("--since", default="12m", help="12m, 90d, 1y, YYYY-MM-DD or '' (default 12m)")
    s.add_argument("--limit", type=int, default=100, help="posts fetched per call, max 100")
    s.add_argument("--top", type=int, default=25, help="posts printed")
    s.add_argument("--min-score", type=int, default=None, help="off by default: low and negative scores hold complaints")
    s.add_argument("--by", choices=["score", "date"], default="score")
    s.add_argument("--fulltext", action="store_true", help="match body too (slow, often 422 Timeout)")
    s.add_argument("--text-chars", type=int, default=220)
    s.add_argument("--pace", type=float, default=6.0, help="seconds between calls (6 to 8 recommended)")
    s.add_argument("--format", choices=["md", "jsonl"], default="md")
    s.set_defaults(fn=cmd_search)
    t = sub.add_parser("thread", help="top comments of one thread")
    t.add_argument("thread", help="thread id or reddit URL")
    t.add_argument("--limit", type=int, default=15)
    t.add_argument("--pages", type=int, default=2, help="comment pages of ~100 to load")
    t.add_argument("--text-chars", type=int, default=500, help="characters per comment")
    t.add_argument("--post-chars", type=int, default=0, help="characters of post text (0 = all)")
    t.add_argument("--pace", type=float, default=6.0)
    t.add_argument("--format", choices=["md", "jsonl"], default="md")
    t.set_defaults(fn=cmd_thread)
    u = sub.add_parser("subs", help="find subreddits by name prefix")
    u.add_argument("prefix")
    u.add_argument("--limit", type=int, default=25)
    u.add_argument("--pace", type=float, default=3.0)
    u.add_argument("--format", choices=["md", "jsonl"], default="md")
    u.set_defaults(fn=cmd_subs)
    b = sub.add_parser("top", help="browse one subreddit in a window, ranked locally (no query)")
    b.add_argument("-s", "--subreddit", required=True)
    b.add_argument("--since", default="12m")
    b.add_argument("--pages", type=int, default=5, help="pages of 100 posts, newest first")
    b.add_argument("--top", type=int, default=30)
    b.add_argument("--by", choices=["score", "comments", "date"], default="score")
    b.add_argument("--text-chars", type=int, default=200)
    b.add_argument("--pace", type=float, default=4.0)
    b.add_argument("--format", choices=["md", "jsonl"], default="md")
    b.set_defaults(fn=cmd_top)
    c = sub.add_parser("comments", help="search comment bodies in one or more subreddits")
    c.add_argument("query")
    c.add_argument("-s", "--subreddits", required=True)
    c.add_argument("--since", default="12m")
    c.add_argument("--pages", type=int, default=4, help="pages of 25 comments, newest first")
    c.add_argument("--top", type=int, default=30)
    c.add_argument("--min-score", type=int, default=None)
    c.add_argument("--by", choices=["score", "date"], default="score")
    c.add_argument("--text-chars", type=int, default=400)
    c.add_argument("--pace", type=float, default=6.0)
    c.add_argument("--format", choices=["md", "jsonl"], default="md")
    c.set_defaults(fn=cmd_comments)
    r = sub.add_parser("rules", help="posting rules of one or more subreddits")
    r.add_argument("subreddits"); r.add_argument("--text-chars", type=int, default=400)
    r.add_argument("--pace", type=float, default=3.0)
    r.set_defaults(fn=cmd_rules)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
