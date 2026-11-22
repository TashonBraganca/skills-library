#!/usr/bin/env python3
"""YouTube search and transcripts without an API key.

  youtube.py search "mechanistic interpretability tutorial" --since 12m --limit 8
  youtube.py transcript dQw4w9WgXcQ                       # id or any youtube URL
  youtube.py transcript https://youtu.be/dQw4w9WgXcQ --timestamps --max-chars 8000
  youtube.py transcript VIDEO --lang de                   # another caption language
  youtube.py transcript VIDEO --no-ytdlp                  # force the built-in route

Transcript routes, in order:
  1. yt-dlp, if it is on PATH (`yt-dlp --write-auto-subs --skip-download`). Most robust.
  2. The built-in route: YouTube's Android player endpoint, then the caption track it lists.
     No install needed. It is an unofficial route and YouTube may change it, so the script
     says plainly when it fails. If yt-dlp is missing and this route breaks: brew install yt-dlp.

Auto-generated captions have no punctuation and mangle names and numbers. Quote them as
"auto-caption says", and check any figure or name against the description or a written source.
Search reads YouTube's results page. Ranking is YouTube's, so recency and relevance are mixed.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import BROWSER_UA, clip, emit, http_get, log, md_escape, parse_since  # noqa: E402

ANDROID_UA = "com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip"
# YouTube's own "upload date" filter codes for the results page.
SP_FILTER = {"hour": "EgIIAQ%3D%3D", "day": "EgIIAg%3D%3D", "week": "EgIIAw%3D%3D",
             "month": "EgIIBA%3D%3D", "year": "EgIIBQ%3D%3D"}


def video_id(s):
    s = s.strip()
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    u = urllib.parse.urlparse(s)
    if u.hostname and "youtu.be" in u.hostname:
        return u.path.strip("/")[:11]
    q = urllib.parse.parse_qs(u.query)
    if "v" in q:
        return q["v"][0][:11]
    m = re.search(r"/(?:shorts|embed|live)/([\w-]{11})", u.path)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- search

def pick_filter(since):
    if not since:
        return ""
    import datetime as dt
    days = (dt.date.today() - since).days
    if days > 366:
        return ""
    return SP_FILTER["day" if days <= 1 else "week" if days <= 7 else "month" if days <= 31 else "year"]


def find_json(page, marker):
    i = page.find(marker)
    if i < 0:
        return None
    i = page.find("{", i)
    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(page)):
        c = page[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(page[i: j + 1])
                except ValueError:
                    return None
    return None


def walk(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                yield v
            else:
                yield from walk(v, key)
    elif isinstance(o, list):
        for x in o:
            yield from walk(x, key)


def txt(o):
    if not o:
        return ""
    return o.get("simpleText") or "".join(r.get("text", "") for r in o.get("runs", []))


def cmd_search(a):
    since = parse_since(a.since)
    sp = pick_filter(since)
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(a.query) + (f"&sp={sp}" if sp else "")
    status, body, _ = http_get(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en-US,en;q=0.9",
                                             "Cookie": "CONSENT=YES+1"}, timeout=30, retries=2)
    page = body.decode("utf8", "replace")
    data = find_json(page, "ytInitialData") if status == 200 else None
    if not data:
        log(f"[youtube] search page gave no results data (HTTP {status}). YouTube may be showing a consent or bot page.")
        return 2
    if since:
        bucket = next((k for k, v in SP_FILTER.items() if v == sp), "none")
        log(f"[youtube] requested cutoff={since}; upload bucket={bucket}; verify video dates individually")
    rows = []
    for v in walk(data, "videoRenderer"):
        vid = v.get("videoId")
        if not vid:
            continue
        rows.append({
            "id": vid, "title": txt(v.get("title")), "channel": txt(v.get("ownerText")),
            "published": txt(v.get("publishedTimeText")), "views": txt(v.get("viewCountText")),
            "length": txt(v.get("lengthText")), "url": f"https://www.youtube.com/watch?v={vid}",
            "snippet": txt((v.get("detailedMetadataSnippets") or [{}])[0].get("snippetText")),
            "requested_cutoff": since.isoformat() if since else None, "upload_bucket": sp or None,
        })
    if not rows:
        log("[youtube] page parsed but held no video results")
        return 2
    rows = rows[: a.limit]
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0
    print(f"# YouTube search: {a.query}" + (f" (upload filter: {sp and [k for k, v in SP_FILTER.items() if v == sp][0]})" if sp else "") + f", {len(rows)} results\n")
    for i, r in enumerate(rows, 1):
        print(f"{i}. [{md_escape(clip(r['title'], 100))}]({r['url']}) | {r['channel']} | {r['published']} | {r['views']} | {r['length']}")
        if r["snippet"]:
            print(f"    {clip(r['snippet'], 200)}")
    return 0


# ---------------------------------------------------------------- transcript

def caption_xml_to_lines(xml_bytes):
    """Timedtext XML (format 3) -> [(start_seconds, text)]."""
    root = ET.fromstring(xml_bytes)
    out = []
    for p in root.iter("p"):
        t = p.get("t")
        text = html.unescape("".join(p.itertext())).replace("\n", " ").strip()
        if text and t is not None:
            out.append((int(t) / 1000.0, re.sub(r"\s+", " ", text)))
    return out


def vtt_to_lines(vtt):
    """WebVTT from yt-dlp -> [(start_seconds, text)], with rolling-caption repeats removed."""
    out, last = [], ""
    for block in re.split(r"\n\n+", vtt):
        m = re.search(r"(\d+):(\d\d):(\d\d)\.(\d+) --> ", block)
        if not m:
            continue
        start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        lines = [re.sub(r"<[^>]+>", "", l).strip() for l in block.split("\n")[1:]]
        for l in lines:
            if l and l != last:
                out.append((float(start), l))
                last = l
    return out


def meta_from_player(pr):
    vd = pr.get("videoDetails") or {}
    mf = (pr.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    return {"title": vd.get("title", ""), "channel": vd.get("author", ""), "seconds": int(vd.get("lengthSeconds") or 0),
            "views": vd.get("viewCount", ""), "published": mf.get("publishDate", "") or mf.get("uploadDate", ""),
            "description": vd.get("shortDescription", "")}


def builtin_route(vid, lang):
    body = {"context": {"client": {"clientName": "ANDROID", "clientVersion": "20.10.38", "androidSdkVersion": 34, "hl": "en"}},
            "videoId": vid}
    status, raw, _ = http_get("https://www.youtube.com/youtubei/v1/player?prettyPrint=false", method="POST",
                              data=json.dumps(body).encode(), retries=2, backoff=3,
                              headers={"User-Agent": ANDROID_UA, "Content-Type": "application/json"})
    try:
        pr = json.loads(raw)
    except ValueError:
        return None, None, f"player endpoint returned HTTP {status}, not JSON"
    ps = pr.get("playabilityStatus") or {}
    if ps.get("status") != "OK":
        return None, meta_from_player(pr), f"video not playable: {ps.get('status')} {ps.get('reason', '')}"
    tracks = (((pr.get("captions") or {}).get("playerCaptionsTracklistRenderer") or {}).get("captionTracks")) or []
    meta = meta_from_player(pr)
    if not tracks:
        return None, meta, "this video has no caption tracks (no manual or auto captions)"
    # prefer a manual track in the language, then the auto track, then any track starting with the language
    def rank(t):
        code = t.get("languageCode", "")
        return (0 if code == lang else 1 if code.startswith(lang) else 2, 1 if t.get("kind") == "asr" else 0)
    base = lang.lower().split("-")[0]
    matching = [t for t in tracks if t.get("languageCode", "").lower().split("-")[0] == base]
    if not matching:
        return None, meta, f"no caption track for {lang}"
    t = min(matching, key=rank)
    status, xml, _ = http_get(t["baseUrl"], headers={"User-Agent": ANDROID_UA}, retries=2, backoff=3)
    if status != 200 or not xml.strip():
        return None, meta, f"caption download returned HTTP {status} with {len(xml)} bytes (YouTube may have changed this route)"
    try:
        lines = caption_xml_to_lines(xml)
    except ET.ParseError as e:
        return None, meta, f"caption XML did not parse: {e}"
    meta["track"] = f"{t.get('languageCode')}{' (auto-generated)' if t.get('kind') == 'asr' else ' (manual)'}"
    if not meta["published"]:  # the Android player response has no publish date; the watch page does
        st, page, _ = http_get(f"https://www.youtube.com/watch?v={vid}", retries=1,
                               headers={"User-Agent": BROWSER_UA, "Cookie": "CONSENT=YES+1", "Accept-Language": "en-US,en;q=0.9"})
        m = re.search(rb'"(?:publishDate|uploadDate)":"(\d{4}-\d\d-\d\d)', page) if st == 200 else None
        meta["published"] = m.group(1).decode() if m else ""
    return lines, meta, ""


def ytdlp_route(vid, lang):
    tmp = tempfile.mkdtemp(prefix="ytsub-")
    cmd = ["yt-dlp", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", f"{lang}.*,{lang}",
           "--sub-format", "vtt", "--no-warnings", "--print", "%(title)s\t%(channel)s\t%(duration)s\t%(view_count)s\t%(upload_date)s",
           "-o", os.path.join(tmp, "%(id)s"), f"https://www.youtube.com/watch?v={vid}"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return None, {}, f"yt-dlp failed: {type(exc).__name__}"
    files = glob.glob(os.path.join(tmp, "*.vtt"))
    parts = (p.stdout.strip().split("\n")[0] if p.stdout.strip() else "").split("\t")
    meta = {"title": parts[0] if parts else "", "channel": parts[1] if len(parts) > 1 else "",
            "seconds": int(float(parts[2])) if len(parts) > 2 and parts[2] not in ("", "NA") else 0,
            "views": parts[3] if len(parts) > 3 else "", "published": parts[4] if len(parts) > 4 else "", "description": ""}
    if not files:
        return None, meta, f"yt-dlp wrote no subtitle file (exit {p.returncode}): {p.stderr.strip()[-200:]}"
    meta["track"] = os.path.basename(files[0])
    return vtt_to_lines(open(files[0], encoding="utf8").read()), meta, ""


def fmt_time(s):
    s = int(s)
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:d}:{s % 60:02d}"


def cmd_transcript(a):
    vid = video_id(a.video)
    if not vid:
        log("could not find a video id in that input")
        return 2
    route, lines, meta, err = "", None, None, ""
    if shutil.which("yt-dlp") and not a.no_ytdlp:
        route = "yt-dlp"
        lines, meta, err = ytdlp_route(vid, a.lang)
        if not lines:
            log(f"[youtube] yt-dlp route failed ({err}); trying the built-in route")
    else:
        if not a.no_ytdlp:
            log("[youtube] yt-dlp is not installed, using the built-in route (brew install yt-dlp for a sturdier one)")
    if not lines:
        route = "built-in (android player endpoint)"
        lines, meta, err = builtin_route(vid, a.lang)
    if not lines:
        log(f"[youtube] NO TRANSCRIPT for {vid}: {err}")
        if meta and meta.get("title"):
            print(f"# {meta['title']} ({meta.get('channel')})\nhttps://www.youtube.com/watch?v={vid}\n\nTranscript unavailable: {err}")
        return 2
    if a.format == "jsonl":
        emit({"kind": "video", "id": vid, **{k: meta.get(k) for k in ("title", "channel", "published", "views", "seconds", "track")}})
        for t, x in lines:
            emit({"kind": "caption", "t": t, "text": x})
        return 0
    print(f"# {meta['title']}")
    print(f"{meta['channel']} | published {meta.get('published') or '?'} | {fmt_time(meta['seconds'])} | {meta.get('views') or '?'} views")
    print(f"https://www.youtube.com/watch?v={vid}")
    print(f"transcript: {meta.get('track')} via {route}, {len(lines)} caption lines\n")
    if meta.get("description") and not a.no_description:
        print(f"Description: {clip(meta['description'], 700)}\n")
    if a.timestamps:
        body, last = [], -99
        for t, x in lines:
            if t - last >= 30:
                body.append(f"\n[{fmt_time(t)}] ")
                last = t
            body.append(x + " ")
        text = "".join(body).strip()
    else:
        text = " ".join(x for _, x in lines)
    if a.max_chars and len(text) > a.max_chars:
        text = text[: a.max_chars] + f"\n\n[clipped: {len(text)} chars total]"
    print(text)
    return 0


def cmd_comments(a):
    """Top or newest comments through yt-dlp (no API key). Audience reaction lives here, not in transcripts."""
    import json as _json
    vid = a.video
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", vid)
    vid = m.group(1) if m else vid
    if not shutil.which("yt-dlp"):
        log("[youtube] comments need yt-dlp: brew install yt-dlp")
        return 2
    cmd = ["yt-dlp", "--skip-download", "--write-comments", "--no-warnings", "-J",
           "--extractor-args", f"youtube:max_comments={a.limit},all,0,0;comment_sort={a.sort}",
           f"https://www.youtube.com/watch?v={vid}"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        log(f"[youtube] yt-dlp timed out after {a.timeout}s")
        return 3
    if p.returncode != 0 or not p.stdout.strip():
        log(f"[youtube] yt-dlp failed (exit {p.returncode}): {p.stderr.strip()[-200:]}")
        return 3
    info = _json.loads(p.stdout)
    cs = [c for c in (info.get("comments") or []) if a.replies or c.get("parent") == "root"]
    if not cs:
        log("[youtube] no comments returned (disabled, or none yet).")
        return 2
    rows = [{"date": time.strftime("%Y-%m-%d", time.gmtime(c.get("timestamp") or 0)), "likes": c.get("like_count"),
             "author": c.get("author"), "reply": c.get("parent") != "root", "text": (c.get("text") or "").replace("\n", " "),
             "url": f"https://www.youtube.com/watch?v={vid}&lc={c.get('id')}"} for c in cs]
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0
    print(f"# Comments on {info.get('title')!r} ({info.get('channel')}, {info.get('upload_date')}, "
          f"{len(rows)} read, sort {a.sort})\n")
    for r in rows:
        print(f"- {r['date']} | {r['likes']} likes | {'reply | ' if r['reply'] else ''}{r['author']}: {clip(r['text'], a.text_chars)} <{r['url']}>")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search YouTube videos")
    s.add_argument("query")
    s.add_argument("--since", default="", help="12m, 90d, ...: maps to YouTube's day/week/month/year upload filter")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--format", choices=["md", "jsonl"], default="md")
    s.set_defaults(fn=cmd_search)
    t = sub.add_parser("transcript", help="metadata and captions for one video")
    t.add_argument("video", help="video id or URL")
    t.add_argument("--lang", default="en")
    t.add_argument("--timestamps", action="store_true", help="a [m:ss] marker every ~30 seconds")
    t.add_argument("--max-chars", type=int, default=12000, help="0 = no clip")
    t.add_argument("--no-ytdlp", action="store_true", help="skip yt-dlp even if installed")
    cm = sub.add_parser("comments", help="top or newest comments of one video (needs yt-dlp)")
    cm.add_argument("video"); cm.add_argument("--limit", type=int, default=60)
    cm.add_argument("--sort", choices=["top", "new"], default="top"); cm.add_argument("--replies", action="store_true")
    cm.add_argument("--text-chars", type=int, default=300); cm.add_argument("--timeout", type=int, default=180)
    cm.add_argument("--format", choices=["md", "jsonl"], default="md")
    cm.set_defaults(fn=cmd_comments)
    t.add_argument("--no-description", action="store_true")
    t.add_argument("--format", choices=["md", "jsonl"], default="md")
    t.set_defaults(fn=cmd_transcript)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
