#!/usr/bin/env python3
"""Search Hacker News through the Algolia API (free, no key).

  hn.py search "mechanistic interpretability" --since 12m --min-points 20
  hn.py search "uv vs poetry" --kind comment --since 6m --limit 20
  hn.py search '"reward hacking"' --since 12m               # quotes force the exact phrase
  hn.py search "vllm problems" --by date --since 90d          # newest first
  hn.py thread 43250000 --limit 30                            # top comments of one story

Output is Markdown by default, or JSON lines with --format jsonl.
HN is strong for developer reactions to tools and launches. It skews to US
software people and is thin for anything outside that world.
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import coverage, clip, emit, get_json, iso_from_ts, log, md_escape, parse_since  # noqa: E402

BASE = "https://hn.algolia.com/api/v1"


def strip_html(s):
    s = re.sub(r"<p>", "\n", s or "")
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def cmd_search(a):
    since = parse_since(a.since)
    ep = "search_by_date" if a.by == "date" else "search"
    tags = {"story": "story", "comment": "comment", "all": ""}[a.kind]
    filters = []
    if since:
        filters.append(f"created_at_i>{int(time.mktime(since.timetuple()))}")
    if a.min_points and a.kind != "comment":
        filters.append(f"points>={a.min_points}")
    params = {"query": a.query, "hitsPerPage": min(a.limit, 100), "advancedSyntax": "true", "page": a.page}
    if tags:
        params["tags"] = tags
    if filters:
        params["numericFilters"] = ",".join(filters)
    url = f"{BASE}/{ep}?" + urllib.parse.urlencode(params)
    data, status, err = get_json(url, retries=3, backoff=3)
    if data is None:
        log(f"[hn] failed: HTTP {status} {err}")
        return 2
    log(f"[hn] page={data.get('page')} total_pages={data.get('nbPages')} total_hits={data.get('nbHits')}")
    hits = data.get("hits") or []
    if not hits:
        log(f"[hn] 0 hits for {a.query!r} since {since}. Loosen the query or --min-points; HN search is literal-word.")
        coverage(a.format, "hn/algolia", a.query, window_from=str(since or ""), sort=a.by, page=data.get("page"),
                 total_pages=data.get("nbPages"), total_hits=data.get("nbHits"), items=0, stop="complete_empty")
        return 2
    rows = []
    for h in hits:
        is_c = "comment" in (h.get("_tags") or [])
        oid = h.get("objectID")
        story_id = h.get("story_id") if is_c else oid
        rows.append({
            "kind": "comment" if is_c else "story",
            "date": iso_from_ts(h.get("created_at_i")),
            "title": h.get("title") or h.get("story_title") or "",
            "text": clip(strip_html(h.get("comment_text") or h.get("story_text") or ""), a.text_chars),
            "points": h.get("points"),
            "comments": h.get("num_comments"),
            "author": h.get("author"),
            "hn_url": f"https://news.ycombinator.com/item?id={oid}",
            "story_url": h.get("url") or h.get("story_url") or "",
            "story_id": story_id,
        })
    cov = lambda: coverage(a.format, "hn/algolia", a.query, window_from=str(since or ""), sort=a.by, page=data.get("page"), total_pages=data.get("nbPages"), total_hits=data.get("nbHits"), items=len(rows), stop="complete" if (data.get("page") or 0) == 0 and (data.get("nbPages") or 1) <= 1 else f"partial: page {(data.get('page') or 0) + 1} of {data.get('nbPages')} read")
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        cov()
        return 0
    print(f"# HN {a.kind} results for {a.query!r}, since {since or 'any date'}, sorted by {a.by} "
          f"({data.get('nbHits')} total, showing {len(rows)})\n")
    for r in rows:
        if r["kind"] == "story":
            print(f"- {r['date']} | {r['points']} pts | {r['comments']} comments | "
                  f"[{md_escape(r['title'])}]({r['hn_url']})" + (f" -> {r['story_url']}" if r["story_url"] else ""))
            if r["text"]:
                print(f"    {r['text']}")
        else:
            print(f"- {r['date']} | comment by {r['author']} on \"{clip(r['title'], 70)}\" "
                  f"([thread](https://news.ycombinator.com/item?id={r['story_id']}), [comment]({r['hn_url']}))")
            print(f"    {r['text']}")
    cov()
    return 0


def walk(node, depth, out, max_depth):
    for c in node.get("children") or []:
        if c.get("text"):
            out.append((depth, c))
        if depth < max_depth:
            walk(c, depth + 1, out, max_depth)


def cmd_thread(a):
    story_id = re.sub(r"\D", "", a.item.split("id=")[-1]) if "id=" in a.item else a.item
    data, status, err = get_json(f"{BASE}/items/{story_id}", retries=3, backoff=3)
    if data is None:
        log(f"[hn] failed: HTTP {status} {err}")
        return 2
    out = []
    walk(data, 0, out, a.depth)
    ordered = out[: a.limit]
    if a.format == "jsonl":
        emit({"kind": "story", "id": data.get("id"), "title": data.get("title"), "url": data.get("url"),
              "points": data.get("points"), "date": (data.get("created_at") or "")[:10]})
        for d, c in ordered:
            emit({"kind": "comment", "depth": d, "author": c.get("author"), "date": (c.get("created_at") or "")[:10],
                  "text": clip(strip_html(c["text"]), a.text_chars),
                  "hn_url": f"https://news.ycombinator.com/item?id={c.get('id')}"})
        return 0
    print(f"# {data.get('title')} ({data.get('points')} pts, {(data.get('created_at') or '')[:10]})")
    print(f"{data.get('url') or ''}\nhttps://news.ycombinator.com/item?id={story_id}\n")
    print(f"{len(out)} comments loaded to depth {a.depth}; showing {len(ordered)} in API tree order.\n")
    for d, c in ordered:
        print("  " * d + f"- [{c.get('author')}](https://news.ycombinator.com/item?id={c['id']}) "
              f"({(c.get('created_at') or '')[:10]}): {clip(strip_html(c['text']), a.text_chars)}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search stories or comments")
    s.add_argument("query")
    s.add_argument("--kind", choices=["story", "comment", "all"], default="story")
    s.add_argument("--since", default="12m", help="12m, 90d, 1y, YYYY-MM-DD, or '' for any date")
    s.add_argument("--by", choices=["relevance", "date"], default="relevance")
    s.add_argument("--min-points", type=int, default=0)
    s.add_argument("--page", type=int, default=0, help="zero-based result page")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--text-chars", type=int, default=300)
    s.add_argument("--format", choices=["md", "jsonl"], default="md")
    s.set_defaults(fn=cmd_search)
    t = sub.add_parser("thread", help="read the comments of one HN story")
    t.add_argument("item", help="story id or news.ycombinator.com/item?id= URL")
    t.add_argument("--limit", type=int, default=30)
    t.add_argument("--depth", type=int, default=2)
    t.add_argument("--text-chars", type=int, default=500)
    t.add_argument("--format", choices=["md", "jsonl"], default="md")
    t.set_defaults(fn=cmd_thread)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
