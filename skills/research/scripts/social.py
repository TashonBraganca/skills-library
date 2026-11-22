#!/usr/bin/env python3
"""Free social and Q&A sources with public JSON: X, Bluesky, Stack Exchange, Lobsters, dev.to,
LessWrong and Alignment Forum, Discourse forums, Hugging Face discussions, App Store reviews.

  social.py x search "sparse autoencoder" --since 90d --min-faves 20 --feed top
  social.py x search "interpretability" --from neelnanda5 --since 12m --feed latest
  social.py x post https://x.com/karpathy/status/1617979122625712128    # the post and its author's thread
  social.py bluesky "mechanistic interpretability" --since 90d --sort top --limit 10
  social.py stackoverflow "pytorch hooks memory leak" --since 12m --sort votes
  social.py stackoverflow --site ai.stackexchange.com "sparse autoencoder"
  social.py answers 69086989 --site stackoverflow            # top answers of one question
  social.py lobsters --tag ai --pages 3 --grep "agent|claude"    # no free full-text search, so we filter tag pages
  social.py lobsters --story spmgsd                          # one story with its comments
  social.py devto --tag llm --top 30 --grep "evaluation"     # dev.to has no free text search, so we filter a tag
  social.py lesswrong "reward hacking" --since 12m           # LessWrong / Alignment Forum posts (--af for AF only)
  social.py lesswrong "reward hacking" --comments            # comments: where the objections are
  social.py discourse discuss.huggingface.co "grpo reward"   # any Discourse forum (HF, PyTorch, OpenAI, Cursor...)
  social.py hfdiscuss Qwen/Qwen3-8B                          # Hugging Face model, dataset or space discussions
  social.py appreviews 284882215 --country us --pages 2      # Apple App Store reviews (app id from the store URL)

X: uses the FixTweet API (api.fxtwitter.com/2). It is a free volunteer service, not an official X
API. Its search endpoint stopped answering in Nov 2026; x search then falls back to a site:x.com web
search plus per-post lookups, which samples far fewer posts and ignores min_faves. It supports X search operators (min_faves, since, from, lang). It can break or rate-limit
without notice, returns 20 posts per page, and its profile-timeline endpoint truncates its own JSON,
so use `--from user` search instead.
Each source has blind spots, listed in the social-search skill. Counts and dates come from the
API, but a post is still only a lead until you read what it says.
Bluesky: api.bsky.app answers; the public.api.bsky.app host returns 403 for search from scripts.
Lobsters: lobste.rs/search is behind a bot check, so search is done by reading tag feeds.
Stack Exchange: about 300 anonymous requests per day per IP.
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.parse
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import BROWSER_UA, clip, coverage, emit, get_json, iso_from_ts, log, md_escape, parse_since  # noqa: E402


def strip_html(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()


def show(rows, a, title, line, failed=False):
    """Print rows. Exit 3 when rows came back but a later page failed (partial coverage)."""
    if not rows:
        log("[social] no results. Widen --since, shorten the query, or try another source.")
        return 2
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 3 if failed else 0
    print(f"# {title}, {len(rows)} results\n")
    if failed:
        print("PARTIAL: a later page failed to load, so this is not the full sample.\n")
    for r in rows:
        print(line(r))
        if r.get("text"):
            print(f"    {clip(r['text'], a.text_chars)}")
        if r.get("quote"):
            qt = r["quote"]
            print(f"    quoted @{qt.get('author')}: {clip(qt.get('text', ''), 160)} <{qt.get('url')}>")
    return 3 if failed else 0


# ---------------------------------------------------------------- x (FixTweet API)

FX = "https://api.fxtwitter.com"


def x_row(r):
    from email.utils import parsedate_to_datetime
    try:
        day = parsedate_to_datetime(r.get("created_at", "")).strftime("%Y-%m-%d")
    except Exception:
        day = ""
    au = r.get("author") or {}
    text = r.get("text", "")
    q = r.get("quote")
    return {"date": day, "author": au.get("screen_name"), "followers": au.get("followers"), "likes": r.get("likes"),
            "reposts": r.get("reposts"), "replies": r.get("replies"), "views": r.get("views"),
            "text": text.replace("\n", " "), "url": r.get("url"), "id": r.get("id"),
            "quote": {"author": (q.get("author") or {}).get("screen_name"), "text": q.get("text", ""),
                      "url": q.get("url")} if q else None}


def cmd_x_search(a):
    since = parse_since(a.since)
    q = a.query
    if a.frm:
        q += f" from:{a.frm.lstrip('@')}"
    if since:
        q += f" since:{since.isoformat()}"
    if a.min_faves:
        q += f" min_faves:{a.min_faves}"
    if a.lang:
        q += f" lang:{a.lang}"
    if a.no_replies:
        q += " -filter:replies"
    if a.pages < 1:
        log("[x] --pages must be at least 1")
        return 2
    rows, cursor, failed = [], None, False
    for page in range(a.pages):
        params = {"q": q, "feed": a.feed, "count": 20}
        if cursor:
            params["cursor"] = cursor
        data, status, err = get_json(f"{FX}/2/search?" + urllib.parse.urlencode(params), retries=2, backoff=4, timeout=45)
        if data is None:
            log(f"[x] page {page + 1} failed: HTTP {status} {err[:120]}. FixTweet may be down or rate-limiting.")
            failed = True
            break
        got = data.get("results")
        if not isinstance(got, list):
            log("[x] unexpected search response: no results array")
            failed = True
            break
        rows += [x_row(r) for r in got]
        cursor = (data.get("cursor") or {}).get("bottom")
        if not got or not cursor:
            break
        time.sleep(1.5)
    via = "x/fxtwitter"
    if failed and not rows:
        # FixTweet search died (HTTP 404 / timeouts since about Nov 2026) while single-post lookups still work.
        # Fallback: find post URLs with a site:x.com web search, then read each post through the lookup.
        import websearch
        wq = f'site:x.com "{a.query}"' + (f" from {a.frm.lstrip('@')}" if a.frm else "")
        hits, engine, werr = websearch.run(wq, since, "auto")
        log(f"[x] search API down; fallback via {engine} web search: {len(hits)} hits {werr[:80]}")
        for h in hits[: max(a.limit, 10)]:
            m = re.search(r"x\.com/[^/]+/status/(\d+)", h.get("url", ""))
            if not m:
                continue
            d, st, er = get_json(f"{FX}/2/thread/{m.group(1)}", retries=1, backoff=2, timeout=30)
            if isinstance(d, dict) and isinstance(d.get("status"), dict):
                r = x_row(d["status"])
                if not since or str(r.get("date", ""))[:10] >= since.isoformat():
                    rows.append(r)
        via = f"x/web-search({engine})+fxtwitter-lookup"
        cursor = None
    seen, uniq = set(), []
    for r in rows:
        if r["id"] not in seen:
            seen.add(r["id"])
            uniq.append(r)
    for r in uniq:
        r["coverage_partial"] = failed or bool(cursor)
    rc = show(uniq[: a.limit], a, f"X posts for [{q}] (feed {a.feed}; FixTweet API, unofficial; X coverage is partial)",
              lambda r: f"- {r['date']} | {r['likes']} likes, {r['reposts']} reposts, {r['replies']} replies, {r['views']} views | "
                        f"@{r['author']} ({r['followers']} followers) | {r['url']}", failed=failed)
    stop = "error" if failed else ("cursor_remaining" if cursor and len(rows) else "complete")
    coverage(a.format, via, q, window_from=str(since or ""), sort=a.feed, pages_read=page + 1,
             items=len(uniq), shown=min(len(uniq), a.limit), stop=stop,
             gaps="replies by other accounts are not sampled; loud accounts dominate")
    return rc


def cmd_x_post(a):
    m = re.search(r"status/(\d+)", a.post)
    pid = m.group(1) if m else re.sub(r"\D", "", a.post)
    data, status, err = get_json(f"{FX}/2/thread/{pid}", retries=2, backoff=4, timeout=45)
    if data is None:
        log(f"[x] failed: HTTP {status} {err[:120]}")
        return 2
    status_obj = data.get("status")
    if not isinstance(status_obj, dict):
        log("[x] unexpected thread response: no status object")
        return 2
    rows = [x_row(status_obj)] + [x_row(t) for t in data.get("thread", []) if t.get("id") != pid]
    return show(rows[: a.limit], a, f"X post {pid} and the author's thread",
                lambda r: f"- {r['date']} | {r['likes']} likes, {r['reposts']} reposts, {r['replies']} replies, {r['views']} views | @{r['author']} | {r['url']}")


# ---------------------------------------------------------------- bluesky

def cmd_bluesky(a):
    since = parse_since(a.since)
    params = {"q": a.query, "limit": min(a.limit, 100), "sort": a.sort}
    if since:
        params["since"] = since.isoformat() + "T00:00:00Z"
    if a.lang:
        params["lang"] = a.lang
    url = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?" + urllib.parse.urlencode(params)
    data, status, err = get_json(url, retries=2, backoff=3, headers={"User-Agent": BROWSER_UA})
    if data is None:
        log(f"[bluesky] failed: HTTP {status} {err[:120]}")
        coverage(a.format, "bluesky", a.query, window_from=str(since or ""), sort=a.sort, items=0, stop=f"error: HTTP {status}")
        return 3
    rows = []
    for p in data.get("posts", []):
        rec = p.get("record") or {}
        handle = (p.get("author") or {}).get("handle", "")
        rkey = p["uri"].rsplit("/", 1)[-1]
        rows.append({"date": (rec.get("createdAt") or "")[:10], "author": handle, "likes": p.get("likeCount"),
                     "reposts": p.get("repostCount"), "replies": p.get("replyCount"),
                     "text": rec.get("text", "").replace("\n", " "),
                     "url": f"https://bsky.app/profile/{handle}/post/{rkey}"})
    more = bool(data.get("cursor")) and len(data.get("posts", [])) >= min(a.limit, 100)
    rc = show(rows, a, f"Bluesky posts for {a.query!r} since {since or 'any date'} (sort {a.sort})",
                lambda r: f"- {r['date']} | {r['likes']} likes, {r['reposts']} reposts, {r['replies']} replies | @{r['author']} | {r['url']}")
    coverage(a.format, "bluesky", a.query, window_from=str(since or ""), sort=a.sort, items=len(rows),
             stop=("complete_empty" if not rows else "partial: more results behind the cursor" if more else "complete"))
    return 3 if (more and rc == 0) else rc


# ---------------------------------------------------------------- stack exchange

def cmd_stack(a):
    since = parse_since(a.since)
    params = {"q": a.query, "site": a.site, "pagesize": min(a.limit, 100), "order": "desc", "sort": a.sort,
              "filter": "withbody"}
    if since:
        params["fromdate"] = int(time.mktime(since.timetuple()))
    if a.tagged:
        params["tagged"] = a.tagged
    url = "https://api.stackexchange.com/2.3/search/advanced?" + urllib.parse.urlencode(params)
    data, status, err = get_json(url, retries=2, backoff=4)
    if data is None:
        log(f"[stackexchange] failed: HTTP {status} {err[:120]}")
        return 2
    if data.get("quota_remaining") is not None:
        log(f"[stackexchange] quota remaining today: {data['quota_remaining']}")
    rows = [{"date": iso_from_ts(q.get("creation_date")), "score": q.get("score"), "answers": q.get("answer_count"),
             "answered": q.get("is_answered"), "accepted": bool(q.get("accepted_answer_id")),
             "views": q.get("view_count"), "title": html.unescape(q.get("title", "")), "tags": q.get("tags"),
             "id": q.get("question_id"), "url": q.get("link"), "text": strip_html(q.get("body", ""))} for q in data.get("items", [])]
    return show(rows, a, f"{a.site} questions for {a.query!r} since {since or 'any date'} (sort {a.sort})",
                lambda r: f"- {r['date']} | score {r['score']} | {r['answers']} answers{' (accepted)' if r['accepted'] else ''} | "
                          f"{r['views']} views | [{md_escape(r['title'])}]({r['url']}) | id {r['id']}")


def cmd_answers(a):
    params = {"site": a.site, "order": "desc", "sort": "votes", "filter": "withbody", "pagesize": min(a.limit, 100)}
    url = f"https://api.stackexchange.com/2.3/questions/{a.question_id}/answers?" + urllib.parse.urlencode(params)
    data, status, err = get_json(url, retries=2, backoff=4)
    if data is None:
        log(f"[stackexchange] failed: HTTP {status} {err[:120]}")
        return 2
    rows = [{"date": iso_from_ts(x.get("creation_date")), "score": x.get("score"), "accepted": x.get("is_accepted"),
             "author": (x.get("owner") or {}).get("display_name"), "text": strip_html(x.get("body", "")),
             "url": f"https://{a.site if '.' in a.site else a.site + '.com'}/a/{x.get('answer_id')}"} for x in data.get("items", [])]
    return show(rows, a, f"Answers to question {a.question_id} on {a.site}",
                lambda r: f"- {r['date']} | score {r['score']}{' | ACCEPTED' if r['accepted'] else ''} | {r['author']} | {r['url']}")


# ---------------------------------------------------------------- lobsters

def lobsters_get(path):
    return get_json("https://lobste.rs" + path, retries=2, backoff=3, headers={"User-Agent": BROWSER_UA})


def cmd_lobsters(a):
    if a.story:
        data, status, err = lobsters_get(f"/s/{a.story}.json")
        if data is None:
            log(f"[lobsters] failed: HTTP {status} {err[:120]}")
            return 2
        print(f"# {data.get('title')} ({data.get('score')} pts, {(data.get('created_at') or '')[:10]})")
        print(f"{data.get('url')}\n{data.get('comments_url') or 'https://lobste.rs/s/' + a.story}\n")
        cs = sorted(data.get("comments", []), key=lambda c: -(c.get("score") or 0))[: a.limit]
        for c in cs:
            print(f"- {c.get('score')} pts, {(c.get('commenting_user') if isinstance(c.get('commenting_user'), str) else (c.get('commenting_user') or {}).get('username'))}, "
                  f"{(c.get('created_at') or '')[:10]}: {clip(strip_html(c.get('comment', '')), a.text_chars)}")
        return 0
    since = parse_since(a.since)
    base = f"/t/{a.tag}.json" if a.tag else ("/newest.json" if a.newest else "/hottest.json")
    pat = re.compile(a.grep, re.I) if a.grep else None
    rows, seen, failed = [], set(), False
    for page in range(1, a.pages + 1):
        data, status, err = lobsters_get(base + (f"?page={page}" if page > 1 else ""))
        if data is None:
            log(f"[lobsters] page {page} failed: HTTP {status} {err[:100]}")
            failed = True
            break
        for s in data:
            day = (s.get("created_at") or "")[:10]
            if s.get("short_id") in seen:
                continue
            seen.add(s.get("short_id"))
            if since and day < since.isoformat():
                continue
            hay = " ".join([s.get("title", ""), s.get("description_plain", ""), " ".join(s.get("tags", [])), s.get("url", "")])
            if pat and not pat.search(hay):
                continue
            rows.append({"date": day, "score": s.get("score"), "comments": s.get("comment_count"), "title": s.get("title"),
                         "tags": s.get("tags"), "link": s.get("url"), "url": s.get("comments_url"), "id": s.get("short_id")})
        time.sleep(1)
    rows.sort(key=lambda r: -(r["score"] or 0))
    for r in rows:
        r["coverage_partial"] = failed
    return show(rows[: a.limit], a, f"Lobsters {a.tag or ('newest' if a.newest else 'hottest')}, {a.pages} page(s), filter {a.grep!r}",
                lambda r: f"- {r['date']} | {r['score']} pts | {r['comments']} comments | [{md_escape(r['title'])}]({r['url']}) | {','.join(r['tags'] or [])} | id {r['id']}", failed=failed)


# ---------------------------------------------------------------- dev.to

def cmd_devto(a):
    pat = re.compile(a.grep, re.I) if a.grep else None
    rows, failed = [], False
    for page in range(1, a.pages + 1):
        params = {"per_page": 100, "page": page}
        if a.tag:
            params["tag"] = a.tag
        if a.top:
            params["top"] = a.top
        data, status, err = get_json("https://dev.to/api/articles?" + urllib.parse.urlencode(params), retries=2, backoff=3,
                                     headers={"User-Agent": BROWSER_UA})
        if data is None:
            log(f"[devto] page {page} failed: HTTP {status} {err[:100]}")
            failed = True
            break
        for x in data:
            hay = " ".join([x.get("title", ""), x.get("description", ""), " ".join(x.get("tag_list", []))])
            if pat and not pat.search(hay):
                continue
            rows.append({"date": (x.get("published_at") or "")[:10], "reactions": x.get("public_reactions_count"),
                         "comments": x.get("comments_count"), "title": x.get("title"), "author": (x.get("user") or {}).get("username"),
                         "tags": x.get("tag_list"), "url": x.get("url"), "text": x.get("description")})
        time.sleep(1)
    rows.sort(key=lambda r: -(r["reactions"] or 0))
    for r in rows:
        r["coverage_partial"] = failed
    return show(rows[: a.limit], a, f"dev.to articles tag={a.tag!r} top={a.top}d filter {a.grep!r}",
                lambda r: f"- {r['date']} | {r['reactions']} reactions | {r['comments']} comments | [{md_escape(r['title'])}]({r['url']}) | @{r['author']}", failed=failed)


# ---------------------------------------------------------------- lesswrong / alignment forum

def cmd_lesswrong(a):
    """LessWrong's Algolia-style search (also serves Alignment Forum content, flagged af)."""
    import json as _json
    from _common import http_get
    since = parse_since(a.since)
    idx = "test_comments" if a.comments else "test_posts"
    rows, failed, nb_pages, pages_read = [], False, None, 0
    for page in range(a.pages):
        body = _json.dumps([{"indexName": idx, "params": {"query": a.query, "hitsPerPage": 50, "page": page}}]).encode()
        status, raw, _ = http_get("https://www.lesswrong.com/api/search", data=body,
                                  headers={"content-type": "application/json", "User-Agent": BROWSER_UA}, timeout=30, retries=2)
        if status != 200:
            log(f"[lesswrong] HTTP {status} {raw[:100]!r}")
            failed = True
            break
        res = _json.loads(raw)
        res0 = res[0] if isinstance(res, list) else res["results"][0]
        hits = res0.get("hits", [])
        nb_pages = res0.get("nbPages")
        pages_read = page + 1
        if not hits:
            break
        for h in hits:
            date = (h.get("postedAt") or "")[:10]
            if since and date and date < since.isoformat():
                continue
            if a.af and str(h.get("af")) != "True":
                continue
            if a.comments:
                url = f"https://www.lesswrong.com/posts/{h.get('postId')}/{h.get('postSlug')}?commentId={h.get('_id')}"
                title = f"comment on: {h.get('postTitle')}"
            else:
                url = f"https://www.lesswrong.com/posts/{h.get('_id')}/{h.get('slug')}"
                title = h.get("title", "")
            rows.append({"date": date, "score": h.get("baseScore"), "comments": h.get("commentCount"),
                         "author": h.get("authorDisplayName"), "af": h.get("af"), "title": title,
                         "link": h.get("url") or "", "url": url, "text": (h.get("body") or "").replace("\n", " ")})
    if a.by == "score":
        rows.sort(key=lambda r: -(r["score"] or 0))
    else:
        rows.sort(key=lambda r: r["date"], reverse=True)
    rows = rows[: a.limit]
    kind = "comments" if a.comments else "posts"
    rc = show(rows, a, f"LessWrong/AF {kind} for {a.query!r} since {since or 'any date'} (sorted by {a.by}; karma is a proxy)",
                lambda r: f"- {r['date']} | {r['score']} karma | {r['comments'] if r['comments'] is not None else ''} comments | "
                          f"{'AF | ' if str(r['af']) == 'True' else ''}{r['author']} | {md_escape(clip(r['title'], 100))} | {r['url']}"
                          + (f" | links to {r['link']}" if r['link'] else ""), failed)
    coverage(a.format, "lesswrong/" + kind, a.query, window_from=str(since or ""), sort=a.by, pages_read=pages_read,
             total_pages=nb_pages, items=len(rows),
             stop="error" if failed else ("complete" if nb_pages is not None and pages_read >= nb_pages else f"partial: {pages_read} of {nb_pages} pages"),
             gaps="text search only; cross-posts counted once by URL")
    return rc


# ---------------------------------------------------------------- discourse forums

def cmd_discourse(a):
    host = a.host.replace("https://", "").replace("http://", "").strip("/")
    q = a.query + (f" after:{parse_since(a.since).isoformat()}" if a.since else "") + (f" order:{a.order}" if a.order else "")
    data, status, err = get_json(f"https://{host}/search.json?" + urllib.parse.urlencode({"q": q}),
                                 retries=2, headers={"User-Agent": BROWSER_UA, "Accept": "application/json"})
    if data is None:
        log(f"[discourse] {host} failed: HTTP {status} {err[:100]}")
        return 3
    topics = {t["id"]: t for t in data.get("topics", [])}
    rows = []
    for p in data.get("posts", [])[: a.limit]:
        t = topics.get(p.get("topic_id"), {})
        rows.append({"date": (p.get("created_at") or "")[:10], "likes": p.get("like_count"), "author": p.get("username"),
                     "title": t.get("title", ""), "replies": t.get("posts_count"),
                     "url": f"https://{host}/t/{t.get('slug', 'topic')}/{p.get('topic_id')}/{p.get('post_number', 1)}",
                     "text": strip_html(p.get("blurb", ""))})
    return show(rows, a, f"{host} posts for {a.query!r} (Discourse search; blurbs only, open the post)",
                lambda r: f"- {r['date']} | {r['likes']} likes | {r['replies']} posts in topic | {r['author']} | "
                          f"{md_escape(clip(r['title'], 100))} | {r['url']}")


# ---------------------------------------------------------------- hugging face discussions

def cmd_hfdiscuss(a):
    url = f"https://huggingface.co/api/{a.type}/{a.repo}/discussions"
    data, status, err = get_json(url, retries=2, headers={"User-Agent": BROWSER_UA})
    if data is None:
        log(f"[hf] {a.repo} discussions failed: HTTP {status} {err[:100]}")
        return 3
    prefix = "" if a.type == "models" else a.type + "/"
    rows = []
    for d in data.get("discussions", []):
        if a.grep and not re.search(a.grep, d.get("title", ""), re.I):
            continue
        rows.append({"date": (d.get("createdAt") or "")[:10], "status": d.get("status"), "pr": d.get("isPullRequest"),
                     "comments": d.get("numComments"), "author": (d.get("author") or {}).get("name"),
                     "title": d.get("title", ""), "url": f"https://huggingface.co/{prefix}{a.repo}/discussions/{d.get('num')}"})
    rows = rows[: a.limit]
    return show(rows, a, f"Hugging Face discussions on {a.repo} (newest first; first page of the API)",
                lambda r: f"- {r['date']} | {r['status']}{' PR' if r['pr'] else ''} | {r['comments']} comments | {r['author']} | "
                          f"{md_escape(clip(r['title'], 100))} | {r['url']}")


# ---------------------------------------------------------------- apple app store reviews

def cmd_appreviews(a):
    rows, failed = [], False
    for page in range(1, a.pages + 1):
        url = f"https://itunes.apple.com/{a.country}/rss/customerreviews/page={page}/id={a.app_id}/sortBy=mostRecent/json"
        data, status, err = get_json(url, retries=2, headers={"User-Agent": BROWSER_UA})
        if data is None:
            log(f"[appreviews] page {page} failed: HTTP {status}")
            failed = True
            break
        entries = (data.get("feed") or {}).get("entry") or []
        if isinstance(entries, dict):
            entries = [entries]
        entries = [e for e in entries if "im:rating" in e]
        if not entries:
            break
        for e in entries:
            v = lambda k: (e.get(k) or {}).get("label", "")
            if a.max_rating and int(v("im:rating") or 0) > a.max_rating:
                continue
            rows.append({"review_id": v("id"), "date": v("updated")[:10], "rating": v("im:rating"), "version": v("im:version"),
                         "author": (e.get("author") or {}).get("name", {}).get("label", ""), "title": v("title"),
                         "review_key": f"{a.country}:{a.app_id}:{v('id')}",
                         "app_url": f"https://apps.apple.com/{a.country}/app/id{a.app_id}", "text": v("content").replace("\n", " ")})
    return show(rows, a, f"App Store reviews for app {a.app_id} ({a.country}, newest first"
                + (f", rating <= {a.max_rating}" if a.max_rating else "") + ")",
                lambda r: f"- {r['date']} | {r['rating']} stars | v{r['version']} | {r['author']} | review {r['review_id']} | {md_escape(clip(r['title'], 80))}", failed)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--limit", type=int, default=15)
        p.add_argument("--text-chars", type=int, default=260)
        p.add_argument("--format", choices=["md", "jsonl"], default="md")

    x = sub.add_parser("x", help="X posts through the FixTweet API (unofficial, free)")
    xs = x.add_subparsers(dest="xcmd", required=True)
    xq = xs.add_parser("search", help="search X posts")
    xq.add_argument("query")
    xq.add_argument("--since", default="90d")
    xq.add_argument("--feed", choices=["top", "latest"], default="top")
    xq.add_argument("--min-faves", type=int, default=0)
    xq.add_argument("--from", dest="frm", default="", help="only posts by this handle")
    xq.add_argument("--lang", default="")
    xq.add_argument("--no-replies", action="store_true")
    xq.add_argument("--pages", type=int, default=1, help="pages of 20 posts")
    common(xq)
    xq.set_defaults(fn=cmd_x_search)
    xp = xs.add_parser("post", help="one post and its author's thread")
    xp.add_argument("post", help="status URL or id")
    common(xp)
    xp.set_defaults(fn=cmd_x_post)

    b = sub.add_parser("bluesky", help="search Bluesky posts")
    b.add_argument("query")
    b.add_argument("--since", default="12m")
    b.add_argument("--sort", choices=["top", "latest"], default="top")
    b.add_argument("--lang", default="")
    common(b)
    b.set_defaults(fn=cmd_bluesky)

    s = sub.add_parser("stackoverflow", aliases=["stack"], help="search Stack Overflow or any Stack Exchange site")
    s.add_argument("query")
    s.add_argument("--site", default="stackoverflow", help="e.g. stackoverflow, ai.stackexchange.com, datascience.stackexchange.com")
    s.add_argument("--since", default="12m")
    s.add_argument("--sort", choices=["relevance", "votes", "creation", "activity"], default="relevance")
    s.add_argument("--tagged", default="", help="semicolon list, e.g. python;pytorch")
    common(s)
    s.set_defaults(fn=cmd_stack)

    q = sub.add_parser("answers", help="top answers of one Stack Exchange question")
    q.add_argument("question_id")
    q.add_argument("--site", default="stackoverflow")
    common(q)
    q.set_defaults(fn=cmd_answers)

    l = sub.add_parser("lobsters", help="read Lobsters tag or front-page feeds, or one story")
    l.add_argument("--tag", default="")
    l.add_argument("--newest", action="store_true")
    l.add_argument("--pages", type=int, default=2)
    l.add_argument("--grep", default="", help="regex over title, description, tags, url")
    l.add_argument("--since", default="12m")
    l.add_argument("--story", default="", help="short id of one story, to read its comments")
    common(l)
    l.set_defaults(fn=cmd_lobsters)

    d = sub.add_parser("devto", help="filter dev.to articles by tag")
    d.add_argument("--tag", default="")
    d.add_argument("--top", type=int, default=30, help="best articles of the last N days")
    d.add_argument("--pages", type=int, default=2)
    d.add_argument("--grep", default="")
    common(d)
    d.set_defaults(fn=cmd_devto)
    lw = sub.add_parser("lesswrong", aliases=["lw", "af"], help="LessWrong and Alignment Forum posts or comments")
    lw.add_argument("query"); lw.add_argument("--comments", action="store_true"); lw.add_argument("--af", action="store_true", help="Alignment Forum items only")
    lw.add_argument("--since", default="12m"); lw.add_argument("--pages", type=int, default=2, help="pages of 50 hits")
    lw.add_argument("--by", choices=["score", "date"], default="date"); lw.add_argument("--limit", type=int, default=25)
    lw.add_argument("--text-chars", type=int, default=240); lw.add_argument("--format", choices=["md", "jsonl"], default="md")
    lw.set_defaults(fn=cmd_lesswrong)
    dc = sub.add_parser("discourse", help="search any Discourse forum")
    dc.add_argument("host", help="e.g. discuss.huggingface.co, discuss.pytorch.org, community.openai.com, forum.cursor.com")
    dc.add_argument("query"); dc.add_argument("--since", default=""); dc.add_argument("--order", choices=["latest", "likes", "views"], default="")
    dc.add_argument("--limit", type=int, default=25); dc.add_argument("--text-chars", type=int, default=240)
    dc.add_argument("--format", choices=["md", "jsonl"], default="md")
    dc.set_defaults(fn=cmd_discourse)
    hd = sub.add_parser("hfdiscuss", help="Hugging Face model, dataset or space discussions")
    hd.add_argument("repo"); hd.add_argument("--type", choices=["models", "datasets", "spaces"], default="models")
    hd.add_argument("--grep"); hd.add_argument("--limit", type=int, default=30); hd.add_argument("--text-chars", type=int, default=0)
    hd.add_argument("--format", choices=["md", "jsonl"], default="md")
    hd.set_defaults(fn=cmd_hfdiscuss)
    ap_ = sub.add_parser("appreviews", help="Apple App Store reviews for one app")
    ap_.add_argument("app_id"); ap_.add_argument("--country", required=True, help="storefront: us, in, gb... (the buyer's country)"); ap_.add_argument("--pages", type=int, default=3)
    ap_.add_argument("--max-rating", type=int, default=0, help="keep reviews at or below this rating (complaints)")
    ap_.add_argument("--text-chars", type=int, default=300); ap_.add_argument("--format", choices=["md", "jsonl"], default="md")
    ap_.set_defaults(fn=cmd_appreviews)

    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
