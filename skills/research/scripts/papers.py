#!/usr/bin/env python3
"""Search papers across arXiv, Semantic Scholar and OpenAlex, or read a paper's full text.

  papers.py search "sparse autoencoders" --since 12m --limit 15
  papers.py search "reward hacking agents" --since 2026-01-01 --sources arxiv,openalex --format jsonl
  papers.py search "mechanistic interpretability" --since 6m --code      # add GitHub repo via Hugging Face
  papers.py fulltext 2310.01405                                          # section list with sizes
  papers.py fulltext 2310.01405 --section method --max-chars 6000        # read one section
  papers.py fulltext 2310.01405 --all --max-chars 40000                  # whole text
  papers.py lookup "ImpossibleBench"                       # exact title or id, no date window
  papers.py cites 2507.02778 --limit 30                    # forward: who cites it (replications, critiques)
  papers.py refs 2507.02778                                # backward: what it builds on
  papers.py similar 2507.02778                             # Semantic Scholar recommendations
  papers.py author "Neel Nanda" --since 12m                # a researcher's recent papers
  papers.py hf "reward hacking"                            # Hugging Face papers: upvotes, community
  papers.py hf --daily                                     # today's Hugging Face daily papers
  papers.py reviews "sparse autoencoders"                  # OpenReview forums; read reviews with fetch.py

A search hit is a lead. Run `fulltext` on any paper your answer depends on.
All sources are free and need no key. Semantic Scholar rate-limits shared IPs hard;
when it fails the script says so and carries on with the other sources.
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
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (BROWSER_UA, clip, emit, get_json, http_get, log,  # noqa: E402
                     looks_blocked, md_escape, parse_since)

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?|([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?")
GITHUB_RE = re.compile(r"https?://github\.com/[\w.\-]+/[\w.\-]+", re.I)


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def arxiv_id_from(s):
    if not s:
        return ""
    m = re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?", s)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- sources

def search_arxiv(q, since, limit, raw=False, sort="relevance"):
    if raw:
        sq = q
    else:
        terms = re.findall(r'"[^"]+"|\S+', q)
        sq = " AND ".join(f"all:{t}" if t.startswith('"') else f"all:{t}" for t in terms)
    if since:
        sq += f" AND submittedDate:[{since.strftime('%Y%m%d')}0000 TO 209912312359]"
    params = {"search_query": sq, "start": 0, "max_results": min(limit, 100),
              "sortBy": "submittedDate" if sort == "date" else "relevance", "sortOrder": "descending"}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    status, body, _ = http_get(url, headers={"User-Agent": BROWSER_UA}, retries=2, backoff=5, timeout=25)
    if status != 200:
        log(f"[arxiv] failed: HTTP {status} {body[:80]!r}")
        return []
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        log(f"[arxiv] bad XML: {e}")
        return []
    out = []
    for e in root.findall(ATOM + "entry"):
        aid = arxiv_id_from(e.findtext(ATOM + "id", ""))
        if not aid:
            continue
        summary = re.sub(r"\s+", " ", e.findtext(ATOM + "summary", "")).strip()
        comment = e.findtext(ARXIV_NS + "comment", "") or ""
        code = [c.rstrip(".,;)") for c in GITHUB_RE.findall(summary + " " + comment)]
        out.append({
            "title": re.sub(r"\s+", " ", e.findtext(ATOM + "title", "")).strip(),
            "arxiv_id": aid,
            "doi": (e.findtext(ARXIV_NS + "doi") or "").lower(),
            "date": (e.findtext(ATOM + "published", "") or "")[:10],
            "authors": [a.findtext(ATOM + "name", "") for a in e.findall(ATOM + "author")][:6],
            "abstract": summary,
            "venue": (e.findtext(ARXIV_NS + "journal_ref") or ""),
            "citations": None,
            "url": f"https://arxiv.org/abs/{aid}",
            "code": code[0] if code else "",
            "source": "arxiv",
        })
    return out


def s2_rows(items):
    out = []
    for p in items or []:
        ext = p.get("externalIds") or {}
        aid = ext.get("ArXiv") or ""
        out.append({
            "title": p.get("title") or "",
            "arxiv_id": aid,
            "doi": (ext.get("DOI") or "").lower(),
            "date": p.get("publicationDate") or (str(p["year"]) if p.get("year") else ""),
            "authors": [a.get("name", "") for a in (p.get("authors") or [])][:6],
            "abstract": p.get("abstract") or "",
            "venue": "arXiv preprint" if (p.get("venue") or "").lower().startswith("arxiv") else (p.get("venue") or ""),
            "citations": p.get("citationCount"),
            "url": f"https://arxiv.org/abs/{aid}" if aid else (p.get("url") or ""),
            "code": "",
            "source": "semantic_scholar",
        })
    return out


def search_s2(q, since, limit, sort="relevance"):
    """Relevance search first. It answers HTTP 429 to most anonymous IPs, so fall back to the
    bulk endpoint, which was still answering. Bulk has no relevance rank: it is sorted by date, newest first.
    With sort="date" the relevance endpoint is skipped and bulk is used directly."""
    fields = "title,year,publicationDate,citationCount,venue,externalIds,abstract,authors,url"
    params = {"query": q, "limit": min(limit, 100), "fields": fields}
    if since:
        params["publicationDateOrYear"] = f"{since.isoformat()}:"
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    if sort != "date":
        data, status, err = get_json(url, retries=1, backoff=3, timeout=25)
        if data is not None:
            return s2_rows(data.get("data"))
        log(f"[semantic_scholar] relevance search failed: HTTP {status}; trying date-ranked bulk discovery (no relevance rank)")
    bq = {"query": q, "fields": fields, "sort": "publicationDate:desc"}
    if since:
        bq["publicationDateOrYear"] = f"{since.isoformat()}:"
    data, status, err = get_json("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(bq),
                                 retries=1, backoff=3, timeout=30)
    if data is None:
        log(f"[semantic_scholar] failed: HTTP {status} {err[:100]}")
        return []
    return s2_rows((data.get("data") or [])[: max(limit, 10)])


def abstract_from_inverted(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def search_openalex(q, since, limit, sort="relevance"):
    flt = f"title_and_abstract.search:{q}"
    if since:
        flt += f",from_publication_date:{since.isoformat()}"
    params = {"filter": flt, "per-page": min(limit, 100), "sort": "publication_date:desc" if sort == "date" else "relevance_score:desc",
              "select": "id,title,publication_date,cited_by_count,doi,ids,primary_location,authorships,abstract_inverted_index"}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    data, status, err = get_json(url, retries=3, backoff=4)
    if data is None:
        log(f"[openalex] failed: HTTP {status} {err[:100]}")
        return []
    out = []
    for w in data.get("results") or []:
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        aid = arxiv_id_from(doi) if "arxiv" in doi else ""
        loc = (w.get("primary_location") or {})
        venue = ((loc.get("source") or {}).get("display_name")) or ""
        if venue.lower().startswith("arxiv"):
            venue = "arXiv preprint"
        if not aid:
            aid = arxiv_id_from(loc.get("landing_page_url") or "")
        out.append({
            "title": w.get("title") or "",
            "arxiv_id": aid,
            "doi": doi,
            "date": w.get("publication_date") or "",
            "authors": [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])][:6],
            "abstract": abstract_from_inverted(w.get("abstract_inverted_index")),
            "venue": venue,
            "citations": w.get("cited_by_count"),
            "url": f"https://arxiv.org/abs/{aid}" if aid else (f"https://doi.org/{doi}" if doi else (w.get("id") or "")),
            "code": "",
            "source": "openalex",
        })
    return out


def merge(results):
    """Dedupe by arXiv id, then DOI, then normalised title. Keep the richest fields."""
    merged = {}
    order = []
    for r in results:
        keys = []
        if r["arxiv_id"]:
            keys.append("a:" + r["arxiv_id"])
        if r["doi"] and "arxiv" not in r["doi"]:
            keys.append("d:" + r["doi"])
        keys.append("t:" + norm_title(r["title"]))
        hit = next((merged[k] for k in keys if k in merged), None)
        # A title match never merges two records whose stable ids conflict (two papers can share a title).
        if hit is not None:
            ids_conflict = (hit.get("arxiv_id") and r.get("arxiv_id") and hit["arxiv_id"].split("v")[0] != r["arxiv_id"].split("v")[0]) or \
                (hit.get("doi") and r.get("doi") and "arxiv" not in hit["doi"] + r["doi"] and hit["doi"] != r["doi"])
            if ids_conflict:  # any contradictory stable id keeps the records apart, whatever else matches
                hit = None
                keys = [k for k in keys if not k.startswith("t:") and k not in merged]
        if hit is None:
            hit = dict(r)
            hit["sources"] = [r["source"]]
            order.append(hit)
        else:
            if r["source"] not in hit["sources"]:
                hit["sources"].append(r["source"])
            if r["citations"] is not None:
                hit["citations"] = max(hit["citations"] or 0, r["citations"])
            for f in ("arxiv_id", "doi", "venue", "abstract", "code"):
                if not hit.get(f) and r.get(f):
                    hit[f] = r[f]
            if hit["source"] != "arxiv" and r["source"] == "arxiv":
                hit["date"], hit["url"] = r["date"] or hit["date"], r["url"]
        for k in keys:
            merged[k] = hit
    return order


def in_window(date, since):
    """Keep undated rows and year-only dates in or after the window's year."""
    if not date:
        return True
    if len(date) < 10:
        return date[:4].isdigit() and int(date[:4]) >= since.year
    return date >= since.isoformat()


def add_code_links(rows):
    for r in rows:
        if r.get("code") or not r.get("arxiv_id"):
            continue
        data, status, _ = get_json(f"https://huggingface.co/api/papers/{r['arxiv_id']}", retries=1, backoff=2)
        if data and data.get("githubRepo"):
            r["code"] = data["githubRepo"]
            r["code_stars"] = data.get("githubStars")
        time.sleep(0.3)


def cmd_search(a):
    since = parse_since(a.since)
    srcs = [s.strip() for s in a.sources.split(",") if s.strip()]
    per = max(a.limit, 10)
    jobs = []
    if "arxiv" in srcs:
        jobs.append(lambda: search_arxiv(a.query, since, per, a.raw_arxiv, a.sort))
    if "s2" in srcs or "semantic_scholar" in srcs:
        jobs.append(lambda: search_s2(a.query, since, per, a.sort))
    if "openalex" in srcs:
        jobs.append(lambda: search_openalex(a.query, since, per, a.sort))
    raw = []
    with ThreadPoolExecutor(max_workers=3) as ex:  # one request per host, so arXiv's 1-per-3s rule holds
        for res in ex.map(lambda j: j(), jobs):
            raw += res
    counts = {s: sum(1 for r in raw if r["source"] == s) for s in ("arxiv", "semantic_scholar", "openalex")}
    log(f"[papers] raw hits per source: {counts}")
    rows = merge(raw)
    if since:  # drop anything the source let through that is older than the window
        rows = [r for r in rows if in_window(r["date"], since)]
    if a.sort == "citations":
        rows.sort(key=lambda r: -(r["citations"] or 0))
    elif a.sort == "date":
        rows.sort(key=lambda r: r["date"], reverse=True)
    else:  # relevance: items found by more sources first, keep source order inside a tie
        rows.sort(key=lambda r: -len(r["sources"]))
    rows = rows[: a.limit]
    if a.code:
        add_code_links(rows)
    if not rows:
        log("[papers] no rows available. Check source failures and effective ranking above before treating this query as a null result.")
        return 2
    if a.format == "jsonl":
        for r in rows:
            r = dict(r)
            r["abstract"] = clip(r["abstract"], a.abstract_chars)
            emit(r)
    else:
        print(f"# Papers: {a.query}\n\nsince {since or 'any date'}, {len(rows)} merged results, "
              f"raw per source {counts}\n")
        print("| # | date | title | cites | venue | code | found by |\n|---|---|---|---|---|---|---|")
        for i, r in enumerate(rows, 1):
            title = f"[{md_escape(r['title'])}]({r['url']})" if r["url"] else md_escape(r["title"])
            print(f"| {i} | {r['date']} | {title} | {r['citations'] if r['citations'] is not None else '?'} | "
                  f"{md_escape(clip(r['venue'], 30)) or '-'} | {r['code'] or '-'} | {','.join(r['sources'])} |")
        if a.abstract_chars:
            print()
            for i, r in enumerate(rows, 1):
                print(f"{i}. **{clip(r['title'], 90)}** ({', '.join(r['authors'][:3])}): {clip(r['abstract'], a.abstract_chars)}")
    return 0


# ---------------------------------------------------------------- fulltext

class SectionParser(HTMLParser):
    """Turns arXiv LaTeXML HTML into (heading, text) sections."""
    SKIP = {"script", "style", "nav", "header", "footer", "button", "svg", "math"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections = [["(front matter)", []]]
        self.skip = 0
        self.in_h = 0
        self.h_buf = []
        self.in_article = False
        self.alt_math = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "article" or "ltx_document" in (d.get("class") or ""):
            self.in_article = True
        if tag == "math":
            self.skip += 1
            alt = d.get("alttext")
            if alt:
                self.sections[-1][1].append(" " + alt + " ")
            return
        if tag in self.SKIP:
            self.skip += 1
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self.in_h += 1
            self.h_buf = []
        if tag in ("p", "div", "li", "tr", "br", "figcaption"):
            self.sections[-1][1].append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if tag in ("h1", "h2", "h3", "h4") and self.in_h:
            self.in_h -= 1
            title = re.sub(r"\s+", " ", "".join(self.h_buf)).strip()
            if title:
                if tag == "h1" and len(self.sections) == 1:
                    self.sections[0][0] = title + " [title and abstract]"
                else:
                    self.sections.append([title, []])
        if tag in ("p", "div", "li", "tr"):
            self.sections[-1][1].append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_h:
            self.h_buf.append(data)
        self.sections[-1][1].append(data)


def fetch_arxiv_html(aid):
    for url in (f"https://arxiv.org/html/{aid}",):
        status, body, _ = http_get(url, headers={"User-Agent": BROWSER_UA}, retries=2, backoff=3, timeout=45)
        if status == 200 and b"ltx_" in body[:200000]:
            return url, body.decode("utf8", "replace")
    return None, None


def pdf_text(aid):
    """Fallback 1: local pdftotext. Fallback 2: Jina Reader on the PDF URL."""
    pdf = f"https://arxiv.org/pdf/{aid}"
    if shutil.which("pdftotext"):
        status, body, _ = http_get(pdf, headers={"User-Agent": BROWSER_UA}, timeout=90)
        if status == 200 and body[:4] == b"%PDF":
            p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=body, capture_output=True)
            if p.returncode == 0 and len(p.stdout) > 1000:
                return "pdftotext", p.stdout.decode("utf8", "replace")
    status, body, _ = http_get("https://r.jina.ai/" + pdf, timeout=90, retries=1, backoff=5,
                               headers={"Accept": "text/plain"})
    text = body.decode("utf8", "replace")
    bad, why = looks_blocked(text, status, min_chars=2000)
    if not bad:
        return "jina-reader(pdf)", text
    log(f"[fulltext] PDF fallback failed: {why}")
    return None, ""


HEADING_RE = re.compile(r"^\s*((?:1?\d(?:\.\d{1,2}){0,2}\.?|[A-H]\.\d{0,2}|Appendix [A-Z]:?)\s+[A-Z][A-Za-z][^\n]{2,80}|[A-Z][A-Z,:&-]+(?: [A-Z][A-Z,:&-]+){0,7})\s*$", re.M)


def resplit(secs, limit=30000):
    """Some arXiv HTML puts most of a paper in one element. Split an oversized section on
    numbered heading lines so --section works; leave well-structured papers alone."""
    out = []
    for title, text in secs:
        if len(text) < limit:
            out.append((title, text))
            continue
        cuts = [m for m in HEADING_RE.finditer(text)]
        if len(cuts) < 3:
            out.append((title, text))
            continue
        if cuts[0].start() > 0:
            out.append((title, text[: cuts[0].start()].strip()))
        for i, m in enumerate(cuts):
            end = cuts[i + 1].start() if i + 1 < len(cuts) else len(text)
            out.append((m.group(1).strip() + " [split by heading]", text[m.end(): end].strip()))
    return out


def cmd_fulltext(a):
    m = re.search(r"(?<!\d)\d{4}\.\d{4,5}(?:v\d+)?(?!\d)", a.paper)
    if m is None:
        log("give an arXiv id like 2310.01405 or an arxiv.org URL")
        return 2
    aid = m.group(0)  # keeps an explicit version such as 2310.01405v3
    url, page = fetch_arxiv_html(aid)
    if page:
        p = SectionParser()
        p.feed(page)
        if not p.in_article:
            page = None  # no article markup: take the PDF branch
    secs = []
    if page:
        for title, parts in p.sections:
            text = re.sub(r"[ \t]+", " ", "".join(parts))
            text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
            if text:
                secs.append((title, text))
        # The abstract sits after the author block in the first section. Split it out.
        if secs and secs[0][0].endswith("[title and abstract]"):
            m = re.search(r"\n\s*Abstract\.?\s*\n", secs[0][1])
            if m:
                head = secs[0][1][: m.start()]
                secs[0:1] = [(secs[0][0].replace("[title and abstract]", "[front matter]"), head.strip()),
                             ("Abstract", secs[0][1][m.end():].strip())]
        via = f"arxiv html ({url})"
    else:
        via, text = pdf_text(aid)
        if not text:
            log(f"[fulltext] no HTML or PDF text for {aid}. Open https://arxiv.org/abs/{aid} by hand, "
                f"or install poppler (brew install poppler) for pdftotext.")
            return 2
        secs = [("(pdf text, no section split)", text)]
    secs = resplit(secs)
    total = sum(len(t) for _, t in secs)
    if total < 1500:
        log(f"[fulltext] only {total} chars extracted; treat as a failed read, not as the paper")
        return 2
    print(f"# {aid} via {via}: {len(secs)} sections, {total} chars\n")
    if a.all:
        budget = a.max_chars
        for title, text in secs:
            print(f"\n## {title}\n")
            print(text[:budget])
            budget -= len(text)
            if budget <= 0:
                print("\n[truncated at --max-chars]")
                break
        return 0
    if a.section:
        want = [s.lower() for s in a.section]
        hit = [(t, x) for t, x in secs if any(w in t.lower() for w in want)]
        if not hit:
            log(f"[fulltext] no section matches {a.section}. Use "
                f"the section table (run without --section). First 25: " + "; ".join(clip(t, 40) for t, _ in secs[:25]))
            return 2
        budget = a.max_chars
        for title, text in hit:
            print(f"\n## {title}\n")
            print(text[:budget])
            budget -= len(text)
            if budget <= 0:
                print("\n[truncated at --max-chars]")
                break
        return 0
    print("| # | section | chars |\n|---|---|---|")
    for i, (t, x) in enumerate(secs, 1):
        print(f"| {i} | {md_escape(clip(t, 80))} | {len(x)} |")
    gh = sorted(set(GITHUB_RE.findall(" ".join(x for _, x in secs))))
    print(f"\nGitHub links in the text: {', '.join(gh[:8]) if gh else 'none found'}")
    print("\nRead sections with --section <word> (e.g. method, experiments, limitations) or --all.")
    return 0


S2_FIELDS = "title,year,publicationDate,citationCount,venue,externalIds,abstract,authors,url"


def s2_paper_ref(x):
    """arXiv id, DOI, S2 id or URL -> Semantic Scholar paper reference."""
    m = re.search(r"(?<!\d)(\d{4}\.\d{4,5})(?:v\d+)?(?!\d)", x)
    if m:
        return "arXiv:" + m.group(1)
    if x.lower().startswith("10.") or x.lower().startswith("doi:"):
        return "DOI:" + x.split(":", 1)[-1] if x.lower().startswith("doi:") else "DOI:" + x
    return x


def print_rows(rows, title, fmt, abstract_chars=0):
    if fmt == "jsonl":
        for r in rows:
            emit(r)
        return
    print(f"# {title}\n")
    print("| # | date | title | cites | venue | link |\n|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        print(f"| {i} | {r.get('date','')[:10]} | {md_escape(clip(r.get('title',''), 110))} | {r.get('citations','')} | "
              f"{md_escape(clip(r.get('venue',''), 30))} | {r.get('url','')} |")
        if abstract_chars and r.get("abstract"):
            print(f"|   | | {md_escape(clip(r['abstract'], abstract_chars))} | | | |")


def cmd_lookup(a):
    """Exact title or id lookup across sources with no date window."""
    q = a.query.strip()
    doi = q.split("doi.org/")[-1].removeprefix("doi:").removeprefix("DOI:") if re.match(r"^(doi:|https?://doi\.org/)?10\.\d{4,9}/", q, re.I) else ""
    aid = "" if doi else (arxiv_id_from(q) if re.search(r"\d{4}\.\d{4,5}", q) else "")
    rows = []
    if doi:
        data, status, err = get_json(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields={S2_FIELDS}", retries=1, timeout=25)
        if data:
            rows = s2_rows([data])
        elif status not in (404,):
            log(f"[lookup] Semantic Scholar failed (HTTP {status}); this is not a null result")
            return 3
    elif aid:
        ver = re.search(r"\d{4}\.\d{4,5}(v\d+)", q)
        data, status, err = get_json(f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{aid}?fields={S2_FIELDS}", retries=1, timeout=25)
        if data:
            rows = [r for r in s2_rows([data]) if r.get("arxiv_id", "").split("v")[0] == aid]
            if not rows:
                log(f"[lookup] Semantic Scholar answered with a different arXiv id than {aid}; not using it")
        if not rows:
            st, body, _ = http_get(f"https://export.arxiv.org/api/query?id_list={aid}&max_results=1", timeout=25, retries=2)
            if st == 200:
                try:
                    root = ET.fromstring(body)
                    for e in root.findall(ATOM + "entry"):
                        eid = (e.findtext(ATOM + "id") or "").rsplit("/", 1)[-1]
                        if eid.split("v")[0] == aid and (e.findtext(ATOM + "title") or "").strip():
                            rows = [{"title": " ".join(e.findtext(ATOM + "title").split()), "arxiv_id": aid, "doi": "",
                                     "date": (e.findtext(ATOM + "published") or "")[:10], "authors": [], "citations": None,
                                     "abstract": " ".join((e.findtext(ATOM + "summary") or "").split()), "venue": "arXiv preprint",
                                     "url": f"https://arxiv.org/abs/{aid}", "code": "", "source": "arxiv"}]
                except ET.ParseError:
                    pass
            if not rows:
                log(f"[lookup] Semantic Scholar (HTTP {status}) and arXiv (HTTP {st}) gave no verified record for {aid}; "
                    "not a null result if either failed")
                return 3 if (status not in (200, 404) or st != 200) else 2
        if ver:
            for r in rows:
                r["url"] = f"https://arxiv.org/abs/{aid}{ver.group(1)}"
                r["arxiv_id"] = aid + ver.group(1)
            log(f"[lookup] requested version {ver.group(1)} kept in the link; the metadata describes the paper, check the version history on the abs page")
    else:
        data, status, err = get_json("https://api.semanticscholar.org/graph/v1/paper/search/match?" +
                                     urllib.parse.urlencode({"query": a.query, "fields": S2_FIELDS}), retries=1, timeout=25)
        s2_failed = data is None and status not in (404,)
        if data and data.get("data"):
            rows = s2_rows(data["data"])
        with ThreadPoolExecutor(2) as ex:
            fa = ex.submit(search_arxiv, f'"{a.query}"', None, 5)
            fo = ex.submit(search_openalex, a.query, None, 5)
            extra = (fa.result() or []) + (fo.result() or [])
        want = norm_title(a.query)
        # keep only real title matches: equal, or the query is the title's full prefix (subtitle dropped)
        ql = a.query.strip().lower()
        rows = [r for r in rows + extra if norm_title(r.get("title")) == want
                or (r.get("title") or "").lower().startswith(ql + ":")]
        if not rows and s2_failed:
            log(f"[lookup] Semantic Scholar failed (HTTP {status}) and no other source matched; not a null result")
            return 3
    if not rows:
        log("[lookup] no exact match. Try the full title, the arXiv id, or `search --since ''`.")
        return 2
    rows = merge(rows)[: a.limit]
    print_rows(rows, f"Lookup: {a.query} (no date window)", a.format, a.abstract_chars)
    return 0


def s2_graph(path, ref, limit, key):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{urllib.parse.quote(ref, safe=':')}/{path}?" + \
        urllib.parse.urlencode({"fields": S2_FIELDS + ",contexts,isInfluential" if path == "citations" else S2_FIELDS,
                                "limit": min(limit, 1000)})
    data, status, err = get_json(url, retries=2, backoff=4, timeout=30)
    if data is None:
        log(f"[semantic_scholar] {path} failed: HTTP {status} {err[:100]}")
        return None
    items = data.get("data") or []
    rows = s2_rows([x.get(key) or {} for x in items])
    for r, x in zip(rows, items):
        r["influential"] = x.get("isInfluential")
        ctx = x.get("contexts") or []
        r["context"] = clip(ctx[0], 300) if ctx else ""
    return rows


def cmd_graph(a):
    ref = s2_paper_ref(a.paper)
    key = {"cites": "citingPaper", "refs": "citedPaper"}[a.cmd]
    path = {"cites": "citations", "refs": "references"}[a.cmd]
    rows = s2_graph(path, ref, a.limit, key)
    if rows is None:
        return 3
    rows = [r for r in rows if r.get("title")]
    if a.grep:
        rx = re.compile(a.grep, re.I)
        rows = [r for r in rows if rx.search(r.get("title", "") + " " + r.get("abstract", "") + " " + r.get("context", ""))]
    rows.sort(key=lambda r: r.get("date") or "", reverse=True)
    if not rows:
        log(f"[{a.cmd}] none found for {ref}. New papers show few citations; this is not evidence of no follow-up work.")
        return 2
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0
    label = "Papers citing" if a.cmd == "cites" else "Papers cited by"
    print(f"# {label} {ref} ({len(rows)}, newest first; Semantic Scholar coverage lags for new work)\n")
    for r in rows:
        flag = " [influential]" if r.get("influential") else ""
        print(f"- {r['date'][:10]} | {md_escape(clip(r['title'], 120))}{flag} | {r['url']}")
        if r.get("context"):
            print(f"    cited as: {md_escape(r['context'])}")
    return 0


def cmd_similar(a):
    ref = s2_paper_ref(a.paper)
    url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{urllib.parse.quote(ref, safe=':')}?" + \
        urllib.parse.urlencode({"fields": S2_FIELDS, "limit": min(a.limit, 100)})
    data, status, err = get_json(url, retries=2, backoff=4, timeout=30)
    if data is None:
        log(f"[semantic_scholar] recommendations failed: HTTP {status} {err[:100]}")
        return 3
    rows = s2_rows(data.get("recommendedPapers"))
    print_rows(rows, f"Recommended from {ref} (Semantic Scholar, mostly recent papers)", a.format, a.abstract_chars)
    return 0 if rows else 2


def cmd_author(a):
    data, status, err = get_json("https://api.semanticscholar.org/graph/v1/author/search?" +
                                 urllib.parse.urlencode({"query": a.name, "fields": "name,affiliations,paperCount,hIndex", "limit": 5}),
                                 retries=2, timeout=25)
    if not data or not data.get("data"):
        log(f"[author] no author match ({status} {err[:80]}). Try the full name.")
        return 2
    cands = sorted(data["data"], key=lambda x: -(x.get("paperCount") or 0))
    au = cands[0]
    log("[author] candidates: " + "; ".join(f"{c['name']} ({c.get('paperCount')} papers, id {c['authorId']})" for c in cands))
    since = parse_since(a.since)
    data, status, err = get_json(f"https://api.semanticscholar.org/graph/v1/author/{au['authorId']}/papers?" +
                                 urllib.parse.urlencode({"fields": S2_FIELDS, "limit": 100}), retries=2, timeout=30)
    if data is None:
        log(f"[author] papers failed: HTTP {status}")
        return 3
    rows = [r for r in s2_rows(data.get("data")) if not since or in_window(r.get("date", ""), since)]
    rows.sort(key=lambda r: r.get("date") or "", reverse=True)
    print_rows(rows[: a.limit], f"{au['name']} (S2 author {au['authorId']}): papers since {since or 'any date'}. "
               "Check the candidate list on stderr: names collide.", a.format, a.abstract_chars)
    return 0 if rows else 2


def cmd_hf(a):
    if a.daily:
        url = "https://huggingface.co/api/daily_papers?" + urllib.parse.urlencode({"limit": a.limit})
    else:
        if not a.query:
            log("give a query or --daily")
            return 2
        url = "https://huggingface.co/api/papers/search?" + urllib.parse.urlencode({"q": a.query, "limit": a.limit})
    data, status, err = get_json(url, retries=2, timeout=30)
    if data is None:
        log(f"[hf] failed: HTTP {status} {err[:100]}")
        return 3
    rows = []
    for x in data:
        p = x.get("paper") or {}
        rows.append({"title": p.get("title") or x.get("title", ""), "arxiv_id": p.get("id", ""),
                     "date": (p.get("publishedAt") or x.get("publishedAt") or "")[:10],
                     "upvotes": p.get("upvotes"), "comments": x.get("numComments"),
                     "url": f"https://huggingface.co/papers/{p.get('id','')}", "abstract": p.get("summary", "")})
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0 if rows else 2
    print(f"# Hugging Face papers: {'daily' if a.daily else a.query} ({len(rows)}). Upvotes measure attention, not quality.\n")
    for r in rows:
        print(f"- {r['date']} | {r['upvotes']} upvotes | {r['comments']} comments | {md_escape(clip(r['title'], 120))} | "
              f"{r['url']} | arXiv {r['arxiv_id']}")
        if a.abstract_chars and r["abstract"]:
            print(f"    {clip(r['abstract'], a.abstract_chars)}")
    return 0 if rows else 2


def cmd_reviews(a):
    """OpenReview search. The API serves search anonymously; forum pages with reviews need fetch.py."""
    url = "https://api2.openreview.net/notes/search?" + urllib.parse.urlencode({"term": a.query, "limit": a.limit, "source": "forum"})
    data, status, err = get_json(url, retries=2, timeout=30)
    if data is None:
        log(f"[openreview] search failed: HTTP {status} {err[:100]}")
        return 3
    rows = []
    for n in data.get("notes") or []:
        c = n.get("content") or {}
        val = lambda k: (c.get(k) or {}).get("value", "") if isinstance(c.get(k), dict) else (c.get(k) or "")
        venue = val("venue")
        inv = (n.get("invitations") or [""])[0]
        if "DBLP" in inv and not a.all:
            continue  # bibliographic records carry no reviews
        rows.append({"title": val("title"), "venue": venue, "forum": n.get("forum"),
                     "url": f"https://openreview.net/forum?id={n.get('forum')}",
                     "date": time.strftime("%Y-%m-%d", time.gmtime((n.get("cdate") or 0) / 1000))})
    if a.format == "jsonl":
        for r in rows:
            emit(r)
        return 0 if rows else 2
    print(f"# OpenReview forums for {a.query!r} ({len(rows)}; DBLP records hidden, --all shows them)\n")
    for r in rows:
        print(f"- {r['date']} | {md_escape(clip(r['title'], 110))} | {r['venue']} | {r['url']}")
    print("\nRead reviews, rebuttals and the decision with: python3 $S/fetch.py '<forum url>' --max-chars 40000\n"
          "Withdrawn and rejected submissions keep their reviews: those objections are counter-evidence.")
    return 0 if rows else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search arXiv, Semantic Scholar and OpenAlex, merged")
    s.add_argument("query")
    s.add_argument("--since", default="12m", help="12m, 90d, 1y or YYYY-MM-DD (default 12m; use '' for any date)")
    s.add_argument("--limit", type=int, default=15)
    s.add_argument("--sources", default="arxiv,s2,openalex")
    s.add_argument("--sort", choices=["relevance", "citations", "date"], default="relevance")
    s.add_argument("--code", action="store_true", help="look up a GitHub repo through Hugging Face papers")
    s.add_argument("--format", choices=["md", "jsonl"], default="md")
    s.add_argument("--abstract-chars", type=int, default=0, help="print abstracts, clipped to N chars")
    s.add_argument("--raw-arxiv", action="store_true", help="treat QUERY as a raw arXiv query (cat:cs.LG AND ti:...)")
    s.set_defaults(fn=cmd_search)
    f = sub.add_parser("fulltext", help="read an arXiv paper's HTML (PDF fallback)")
    f.add_argument("paper", help="arXiv id or URL")
    f.add_argument("--section", action="append", help="print sections whose heading contains this word (repeatable)")
    f.add_argument("--all", action="store_true")
    f.add_argument("--max-chars", type=int, default=8000)
    f.set_defaults(fn=cmd_fulltext)
    lk = sub.add_parser("lookup", help="exact title or arXiv id, no date window")
    lk.add_argument("query"); lk.add_argument("--limit", type=int, default=5)
    lk.add_argument("--abstract-chars", type=int, default=300); lk.add_argument("--format", choices=["md", "jsonl"], default="md")
    lk.set_defaults(fn=cmd_lookup)
    for name, hlp in (("cites", "papers citing this one (forward)"), ("refs", "papers this one cites (backward)")):
        g = sub.add_parser(name, help=hlp)
        g.add_argument("paper", help="arXiv id, DOI or Semantic Scholar id")
        g.add_argument("--limit", type=int, default=100); g.add_argument("--grep", help="regex on title, abstract, citation context")
        g.add_argument("--format", choices=["md", "jsonl"], default="md")
        g.set_defaults(fn=cmd_graph)
    sm = sub.add_parser("similar", help="Semantic Scholar recommendations for one paper")
    sm.add_argument("paper"); sm.add_argument("--limit", type=int, default=20)
    sm.add_argument("--abstract-chars", type=int, default=0); sm.add_argument("--format", choices=["md", "jsonl"], default="md")
    sm.set_defaults(fn=cmd_similar)
    au = sub.add_parser("author", help="a researcher's recent papers")
    au.add_argument("name"); au.add_argument("--since", default="12m"); au.add_argument("--limit", type=int, default=30)
    au.add_argument("--abstract-chars", type=int, default=0); au.add_argument("--format", choices=["md", "jsonl"], default="md")
    au.set_defaults(fn=cmd_author)
    hf = sub.add_parser("hf", help="Hugging Face papers search or daily list")
    hf.add_argument("query", nargs="?"); hf.add_argument("--daily", action="store_true")
    hf.add_argument("--limit", type=int, default=20); hf.add_argument("--abstract-chars", type=int, default=0)
    hf.add_argument("--format", choices=["md", "jsonl"], default="md")
    hf.set_defaults(fn=cmd_hf)
    rv = sub.add_parser("reviews", help="OpenReview forums (reviews, rebuttals, decisions) for a topic or title")
    rv.add_argument("query"); rv.add_argument("--limit", type=int, default=15); rv.add_argument("--all", action="store_true")
    rv.add_argument("--format", choices=["md", "jsonl"], default="md")
    rv.set_defaults(fn=cmd_reviews)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
