#!/usr/bin/env python3
"""Pull real design references and assets, then hand them to you as local files to LOOK at.

    scrape_inspo.py dribbble <tag> [--n 24]      # direction: what good looks like now
    scrape_inspo.py mobbin <tag>                  # real shipped product UI and flows
    scrape_inspo.py motion                        # real .mp4 motion assets
    scrape_inspo.py landing                       # landing-page layout references
    scrape_inspo.py bits                          # React Bits components (free to use)
    scrape_inspo.py t21 <query>                   # 21st.dev React components
    scrape_inspo.py github3d <query>              # open-source 3D / WebGL, prints repos to read
    scrape_inspo.py repo <github-url>             # shallow-clone the selected source
    scrape_inspo.py fetch <direct-asset-url>      # download the selected remote asset
    scrape_inspo.py palettes <dir>                # measure a folder of images -> palette JSON

This list is a starting point, not a fence. If a better source exists for what the brief
needs, go and find it, use it, and say which you used.

Downloads to ./inspo/<source>/, writes `_manifest.json` with the source URL for each file, and
prints the paths. **You must then read the image files yourself.** That step is the entire point:
text search returns captions, and choosing a
photograph from its caption is not choosing a photograph. Two measured failures make the case --
agents given only text search produced zero images across five builds, and agents that "searched"
without looking reproduced identical stock photo IDs across runs that never communicated, because
they were reciting IDs from training data and then confirming the URL resolved.

Fetcher notes, learned by testing:
  - Dribbble returns a 202 challenge to plain HTTP. StealthyFetcher goes straight through.
  - motionsites / landinghero / reactbits are JS-rendered SPAs -- plain HTTP returns an empty
    shell with a 200 status. DynamicFetcher renders them.
  - Always confirm a non-empty body. A 200 with an empty or challenge body is a silent failure.

"""
import sys, os, re, json, hashlib, struct, subprocess, urllib.request, urllib.parse
from difflib import SequenceMatcher
from html import unescape
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
OUT = os.path.abspath("./inspo")

SOURCES = {
    "motion":  "https://motionsites.ai/",
    "landing": "https://www.landinghero.ai/library",
    "landinglove": "https://www.landing.love/",
    "magicui": "https://magicui.design/docs/components",
    "bits":    "https://reactbits.dev/",
}

NOISE_WORDS = {"component", "components", "website", "websites", "design", "ui", "the", "a", "an"}


def _tokens(value):
    return {word for word in re.findall(r"[a-z0-9]+", str(value).lower())
            if len(word) > 1 and word not in NOISE_WORDS}


def _require_page(page, url, minimum=3000):
    status = getattr(page, "status", None)
    html = page.html_content or ""
    if status != 200:
        sys.exit(f"HTTP {status} from {url} - do not treat the response body as a result")
    if len(html) < minimum or re.search(r"just a moment|checking your browser", html, re.I):
        sys.exit(f"blocked or empty body from {url} ({len(html)} bytes) - do not treat as success")
    return html


def _rank_records(records, query):
    wanted = _tokens(query)
    ranked = []
    for position, record in enumerate(records):
        text = " ".join(str(value) for key, value in record.items() if key != "url")
        found = _tokens(text)
        overlap = len(wanted & found)
        fuzzy = SequenceMatcher(None, " ".join(sorted(wanted)), " ".join(sorted(found))).ratio()
        if wanted and not overlap:
            continue
        ranked.append((overlap, fuzzy, -position, record))
    ranked.sort(key=lambda item: item[:3], reverse=True)
    return [item[3] for item in ranked]


def _rank_items(items, query):
    return _rank_records(items, query)


def _best_name(query, names):
    wanted = re.sub(r"[^a-z0-9]", "", " ".join(_tokens(query)))
    if not wanted:
        return None
    scored = []
    for name in names:
        clean = re.sub(r"[^a-z0-9]", "", name.lower())
        exactish = clean in wanted or wanted in clean
        score = 1.0 if exactish else SequenceMatcher(None, wanted, clean).ratio()
        scored.append((score, name))
    score, name = max(scored, default=(0, None))
    return name if score >= 0.55 else None


def _nearest_media_card(node):
    media = node.get("src") or " ".join(node.xpath(".//source/@src"))
    candidate = node
    chosen = node
    for _ in range(6):
        candidate = candidate.getparent()
        if candidate is None:
            break
        text = re.sub(r"\s+", " ", candidate.text_content()).strip()
        sibling_media = candidate.xpath(".//video|.//img")
        if text and len(text) <= 700 and len(sibling_media) == 1:
            chosen = candidate
        if len(sibling_media) > 1:
            break
    title = re.sub(r"\s+", " ", chosen.text_content()).strip()
    links = chosen.xpath(".//a[@href]/@href")
    return {"title": title[:500], "url": media, "page_url": links[0] if links else None}


def _caption_near_url(document, url):
    offset = document.find(url)
    if offset < 0:
        return None
    window = document[max(0, offset - 700):offset + 900]
    named = re.search(r'"(?:name|title|description)"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"',
                      window[window.find(url) + len(url):])
    if named:
        try:
            return json.loads(f'"{named.group(1)}"')[:500]
        except Exception:
            pass
    alt = re.search(r'(?:alt|title)=["\']([^"\']+)["\']', window, re.I)
    if alt:
        return unescape(alt.group(1)).strip()[:500]
    text = re.sub(r"<[^>]+>", " ", window)
    return unescape(re.sub(r"\s+", " ", text).strip())[:500] or None


def _asset_facts(path):
    """Return measured facts. Descriptions remain empty until a person or model inspects the asset."""
    suffix = os.path.splitext(path)[1].lower()
    facts = {"kind": "binary"}
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif"}:
        try:
            from PIL import Image
            with Image.open(path) as image:
                facts = {"kind": "image", "width": image.width, "height": image.height,
                         "format": image.format, "mode": image.mode}
                facts["quality"] = f"{image.width}x{image.height} source image"
        except Exception as error:
            facts = {"kind": "image", "probe_error": str(error)}
    elif suffix in {".mp4", ".webm", ".mov", ".m4v"}:
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,codec_name,r_frame_rate,bit_rate:format=duration",
                "-of", "json", path,
            ], check=True, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            stream = (data.get("streams") or [{}])[0]
            facts = {"kind": "video", "width": stream.get("width"),
                     "height": stream.get("height"), "codec": stream.get("codec_name"),
                     "frame_rate": stream.get("r_frame_rate"),
                     "duration_seconds": round(float(data.get("format", {}).get("duration", 0)), 3)}
            facts["quality"] = (f"{facts['width']}x{facts['height']}, {facts['duration_seconds']}s, "
                                f"{facts['codec']}")
        except Exception as error:
            facts = {"kind": "video", "probe_error": str(error)}
    elif suffix in {".glb", ".gltf"}:
        try:
            if suffix == ".glb":
                with open(path, "rb") as source:
                    header = source.read(20)
                    if len(header) < 20 or header[:4] != b"glTF":
                        raise ValueError("invalid GLB header")
                    chunk_length, chunk_type = struct.unpack("<II", header[12:20])
                    if chunk_type != 0x4E4F534A:
                        raise ValueError("GLB has no leading JSON chunk")
                    data = json.loads(source.read(chunk_length).decode("utf-8").rstrip(" \t\r\n\0"))
            else:
                with open(path, encoding="utf-8") as source:
                    data = json.load(source)
            facts = {"kind": "model", "scenes": len(data.get("scenes", [])),
                     "nodes": len(data.get("nodes", [])), "meshes": len(data.get("meshes", [])),
                     "materials": len(data.get("materials", [])),
                     "animations": len(data.get("animations", [])),
                     "cameras": len(data.get("cameras", []))}
            facts["quality"] = (f"{facts['meshes']} meshes, {facts['materials']} materials, "
                                f"{facts['animations']} animations")
        except Exception as error:
            facts = {"kind": "model", "probe_error": str(error)}
    elif suffix in {".hdr", ".exr", ".ktx", ".ktx2"}:
        facts = {"kind": "texture", "format": suffix[1:]}
    elif suffix in {".woff", ".woff2", ".ttf", ".otf"}:
        facts = {"kind": "font", "format": suffix[1:]}
    facts["bytes"] = os.path.getsize(path)
    return facts


def _save(urls, subdir, limit, metadata=None):
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    saved, seen, source_by_path = [], set(), {}
    existing_by_url, existing_by_hash = {}, {}
    for manifest_path in Path(OUT).rglob("_manifest.json"):
        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception:
            continue
        for item in manifest.get("items", []):
            prior = item.get("local_path")
            if not prior or not os.path.isfile(prior):
                continue
            if item.get("source_url"):
                existing_by_url[item["source_url"]] = prior
            if item.get("content_md5"):
                existing_by_hash[item["content_md5"]] = prior
    for u in urls:
        if len(saved) >= limit:
            break
        key = hashlib.md5(u.encode()).hexdigest()[:14]
        if key in seen:
            continue
        seen.add(key)
        if u in existing_by_url:
            p = existing_by_url[u]
            saved.append(p)
            source_by_path[p] = u
            continue
        ext = (re.search(r"\.(png|jpe?g|webp|avif|gif|mp4|webm|mov|m4v|glb|gltf|hdr|exr|ktx2?|woff2?|ttf|otf)(?:[?#]|$)",
                         u.lower()) or [None, "bin"])[1]
        p = os.path.join(d, f"{key}.{ext}")
        if os.path.exists(p):
            saved.append(p); source_by_path[p] = u; continue
        try:
            data = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
            if len(data) < 3000:                     # too small to be a real asset
                continue
            open(p, "wb").write(data)
            saved.append(p)
            source_by_path[p] = u
        except Exception:
            pass
    by_hash, records = dict(existing_by_hash), []
    for p in saved:
        h = hashlib.md5(Path(p).read_bytes()).hexdigest()
        duplicate_of = by_hash.get(h)
        if duplicate_of == p:
            duplicate_of = None
        if not duplicate_of:
            by_hash[h] = p
        item_metadata = (metadata or {}).get(source_by_path[p], {})
        records.append({
            "local_path": p,
            "source_url": source_by_path[p],
            "page_url": item_metadata.get("page_url"),
            "caption": item_metadata.get("caption"),
            "facts": _asset_facts(p),
            "content_md5": h,
            "duplicate_of": duplicate_of,
            "inspection_status": "pending",
            "inspection_output": None,
            "observed_description": None,
            "intended_job": None,
        })
    with open(os.path.join(d, "_manifest.json"), "w") as manifest:
        json.dump({"source": subdir, "items": records}, manifest, indent=2)
    return saved


def _write_candidates(subdir, items):
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "_candidates.json")
    with open(p, "w") as candidate_file:
        json.dump({"source": subdir, "items": items}, candidate_file, indent=2)
    print(f"\nCandidate manifest: {p}")
    return p


def _browser_fetcher(name):
    try:
        from scrapling import fetchers
        return getattr(fetchers, name)
    except ModuleNotFoundError as error:
        sys.exit("Scrapling's browser fetchers are incomplete. Run "
                 "`python -m pip install 'scrapling[fetchers]'`, then install the Chromium "
                 f"runtime. Missing module: {error.name}")


def dribbble(tag, limit):
    StealthyFetcher = _browser_fetcher("StealthyFetcher")
    query = tag.replace("-", " ")
    url = ("https://dribbble.com/search/shots/filters?category=web-design&q="
           + urllib.parse.quote(query))
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=90000)
    html = _require_page(page, url, 5000)
    shots = [u for u in re.findall(r"https://cdn\.dribbble\.com/(?:userupload|uploads)/[^\"'\s?]+", html)
             if re.search(r"\.(png|jpe?g|webp)$", u)]
    return _save(shots, f"dribbble-{tag}", limit)


def spa(which, query, limit):
    DynamicFetcher = _browser_fetcher("DynamicFetcher")
    url = SOURCES[which]
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=60000)
    html = _require_page(page, url)
    pat = (r"https?://[^\"'\s]+\.(?:mp4|webm)(?:\?[^\"'\s]+)?" if which in {"motion", "landinglove"}
           else r"https?://[^\"'\s]+\.(?:png|jpe?g|webp|avif)")
    items = []
    if which in {"motion", "landinglove"}:
        try:
            from lxml import html as lxml_html
            tree = lxml_html.fromstring(html)
            items = [_nearest_media_card(node) for node in tree.xpath("//video")]
        except Exception:
            items = []
    if not items:
        urls = sorted(set(re.findall(pat, html)))
        for media_url in urls:
            offset = html.find(media_url)
            nearby = re.sub(r"<[^>]+>", " ", html[max(0, offset - 1400):offset + 700])
            items.append({"title": re.sub(r"\s+", " ", nearby).strip()[:500], "url": media_url})
    ranked = _rank_items(items, query)
    if not ranked:
        sys.exit(f"{which} returned media, but none matched {query!r}. Change the query or source.")
    _write_candidates(f"{which}-{query.replace(' ', '-')}", ranked[:limit])
    metadata = {item["url"]: {"caption": item.get("title"), "page_url": item.get("page_url")}
                for item in ranked}
    return _save([item["url"] for item in ranked], f"{which}-{query.replace(' ', '-')}",
                 limit, metadata)


def codrops(query, limit):
    """Rank the Codrops GitHub catalogue locally. GitHub search misses many useful repo names."""
    try:
        data = _gh("https://api.github.com/orgs/codrops/repos?per_page=100&type=public&sort=updated")
    except Exception as e:
        sys.exit(f"codrops search failed: {e}")
    items = _rank_records(data if isinstance(data, list) else [], query)
    if not items:
        try:
            results = _gh_plain("https://tympanus.net/codrops/wp-json/wp/v2/search?search="
                                + urllib.parse.quote(query) + f"&per_page={min(limit, 20)}")
        except Exception as error:
            sys.exit(f"Codrops repository and article searches failed: {error}")
        candidates = [{"url": item.get("url"), "description": item.get("title"),
                       "kind": item.get("subtype")} for item in results if item.get("url")]
        if not candidates:
            sys.exit(f"nothing for '{query}' in the Codrops repository or article catalogues")
        _write_candidates(f"codrops-{query.replace(' ', '-')}", candidates)
        print(f"{len(candidates)} Codrops article candidate(s):\n")
        for item in candidates:
            print(f"  {item['description'][:90]}\n      {item['url']}")
        print("\nOpen a candidate, run its demo, and follow its source link before adapting it.")
        return []
    items = items[:limit]
    print(f"{len(items)} Codrops demo(s):\n")
    candidates = []
    for r in items:
        print(f"  {r['html_url']}")
        print(f"      {(r.get('description') or '').strip()[:110]}")
        candidates.append({"url": r["html_url"], "description": r.get("description"),
                           "stars": r.get("stargazers_count")})
    _write_candidates(f"codrops-{query.replace(' ', '-')}", candidates)
    print("\nClone a promising project, run it, and inspect its source and bundled assets.")
    return []


def magicui(query, limit):
    """Named open-source motion components. Return pages, not random screenshots, so the model can
    choose a technique and then inspect its implementation."""
    DynamicFetcher = _browser_fetcher("DynamicFetcher")
    url = SOURCES["magicui"]
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=60000)
    html = _require_page(page, url)
    try:
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        records = []
        seen = set()
        for link in tree.xpath("//a[@href]"):
            href = link.get("href", "")
            label = re.sub(r"\s+", " ", link.text_content()).strip()
            if not label or "/docs/components/" not in href or href in seen:
                continue
            seen.add(href)
            records.append({"name": label, "url": urllib.parse.urljoin(url, href)})
    except Exception as error:
        sys.exit(f"could not parse Magic UI component links: {error}")
    ranked = _rank_records(records, query)
    if not ranked:
        sys.exit(f"Magic UI has no named component matching {query!r}. Try motion, video, text, grid, particles, or beam.")
    chosen = ranked[:limit]
    print(f"{len(chosen)} Magic UI component candidate(s):\n")
    for item in chosen:
        print(f"  {item['name']:<28} {item['url']}")
    _write_candidates(f"magicui-{query.replace(' ', '-')}", chosen)
    print("\nOpen a selected page and read its source before adapting it.")
    return []


def polyhaven(query, limit):
    """Search Poly Haven HDRIs, textures, and 3D models."""
    kinds = {"hdris": "hdris", "textures": "textures", "models": "models"}
    out = []
    for kind in kinds:
        try:
            data = _gh_plain(f"https://api.polyhaven.com/assets?t={kind}")
        except Exception as e:
            print(f"  {kind}: failed ({e})"); continue
        hits = [(k, v) for k, v in data.items()
                if query.lower() in k.lower()
                or any(query.lower() in t.lower() for t in v.get("tags", []))
                or any(query.lower() in c.lower() for c in v.get("categories", []))]
        for k, v in hits[:limit]:
            out.append((kind, k, v.get("name", k)))
    if not out:
        sys.exit(f"nothing on Poly Haven for '{query}'. Try: studio, sky, metal, fabric, concrete.")
    print(f"{len(out)} asset(s) on Poly Haven:\n")
    candidates = []
    for kind, slug, name in out:
        print(f"  [{kind:<8}] {name}")
        print(f"             https://polyhaven.com/a/{slug}")
        print(f"             file: https://dl.polyhaven.org/file/ph-assets/{kind.capitalize()}"
              f"/hdr/2k/{slug}_2k.hdr" if kind == "hdris" else
              f"             browse the page for the resolution you want")
        candidates.append({"kind": kind, "slug": slug, "name": name,
                           "url": f"https://polyhaven.com/a/{slug}",
                           "files_api": f"https://api.polyhaven.com/files/{slug}"})
    _write_candidates(f"polyhaven-{query.replace(' ', '-')}", candidates)
    print("\nInspect the files API, fetch the right resolution, and render it before selection.")
    return []


def fontshare(query, limit):
    """Free quality typefaces, well outside the Google Fonts default set."""
    try:
        data = _gh_plain("https://api.fontshare.com/v2/fonts?limit=100")
    except Exception as e:
        sys.exit(f"fontshare failed: {e}")
    fonts = data.get("fonts", data.get("data", data if isinstance(data, list) else []))
    if query:
        fonts = _rank_records(fonts, query)
    fonts = fonts[:limit]
    if not fonts:
        sys.exit("nothing matched on Fontshare. Run with no query to list them all.")
    print(f"{len(fonts)} typeface(s) on Fontshare:\n")
    for f in fonts:
        name = f.get("name", "?")
        styles = len(f.get("styles", []) or [])
        print(f"  {name:<26} {styles} styles   https://www.fontshare.com/fonts/"
              f"{f.get('slug', name.lower().replace(' ', '-'))}")
    print("\nSelf-host these or use their CDN. They are not in the Google Fonts default set,")
    print("which is where Inter and Fraunces keep coming from.")
    return []


def _gh_plain(url):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=30).read())


RB_API = "https://api.github.com/repos/DavidHDev/react-bits/contents"
RB_CATS = ["Animations", "Backgrounds", "Components", "TextAnimations"]


def _gh(url):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url, headers={**UA, "Accept": "application/vnd.github+json"}),
        timeout=30).read())


def bits(name, limit):
    """React Bits. Scraping the website returned icons and logos, which is useless. Fetch the
    actual component source from GitHub instead: that is the thing worth
    having. No argument lists what exists; a name downloads that component's source."""
    if not name:
        print("React Bits components (MIT). Re-run with a name to download its source.\n")
        listed = 0
        for cat in RB_CATS:
            try:
                names = [x["name"] for x in _gh(f"{RB_API}/src/content/{cat}")]
            except Exception as e:
                print(f"  {cat}: failed ({e})"); continue
            listed += len(names)
            print(f"  {cat} ({len(names)}):")
            for i in range(0, len(names), 4):
                print("     " + "  ".join(f"{n:<22}" for n in names[i:i + 4]))
            print()
        if not listed:
            sys.exit("React Bits returned no component names. Treat the listing as failed and retry later.")
        print("Then: scrape_inspo.py bits <ComponentName>")
        return []

    all_names = []
    names_by_category = {}
    for cat in RB_CATS:
        try:
            names_by_category[cat] = [x["name"] for x in _gh(f"{RB_API}/src/content/{cat}")]
            all_names.extend(names_by_category[cat])
        except Exception:
            names_by_category[cat] = []
    matched = _best_name(name, all_names)
    if not matched:
        suggestions = sorted(all_names, key=lambda candidate: SequenceMatcher(
            None, name.lower(), candidate.lower()).ratio(), reverse=True)[:6]
        sys.exit(f"no close React Bits match for {name!r}. Closest: {', '.join(suggestions)}")
    name = matched
    d = os.path.join(OUT, "react-bits", name)
    os.makedirs(d, exist_ok=True)
    saved = []
    records = []
    for cat in RB_CATS:
        if name not in names_by_category.get(cat, []):
            continue
        try:
            files = _gh(f"{RB_API}/src/content/{cat}/{name}")
        except Exception:
            continue
        for f in files:
            if f["type"] != "file":
                continue
            src = urllib.request.urlopen(
                urllib.request.Request(f["download_url"], headers=UA), timeout=30).read()
            p = os.path.join(d, f["name"])
            open(p, "wb").write(src)
            saved.append(p)
            records.append({"local_path": p, "source_url": f.get("download_url"),
                            "page_url": f.get("html_url"), "caption": f"React Bits {name} source",
                            "facts": {"kind": "source", "bytes": len(src)},
                            "content_md5": hashlib.md5(src).hexdigest(), "duplicate_of": None,
                            "inspection_status": "pending", "inspection_output": None,
                            "observed_description": None, "intended_job": None})
        break
    if not saved:
        sys.exit(f"no React Bits component called '{name}'. Run `bits` with no argument to list them.")
    with open(os.path.join(d, "_manifest.json"), "w") as manifest:
        json.dump({"source": "react-bits", "component": name, "items": records}, manifest, indent=2)
    print(f"{len(saved)} source file(s) for {name}:\n")
    for p in saved:
        print("  ", p)
    print("\nRead the source, run the component, and adapt the behavior to the construction.")
    print("Do not hand-build something this already does well.")
    return []


# Video sources, both verified 2026-09-04 by live fetch. Each returns direct
# .mp4 URLs in plain server-rendered HTML: no JS rendering, no bot challenge.
# Coverr blends media.istockphoto.com (paid) into its free results, 102 of
# them on one "running" search, so its allow list is deliberately narrow.
VIDEO_SOURCES = {
    "mixkit": {
        "url":   "https://mixkit.co/free-stock-video/{q}/",
        "allow": r"https://assets\.mixkit\.co/videos/[^\"'\s]+\.mp4",
        "note":  "direct video files",
    },
    "coverr": {
        "url":   "https://coverr.co/s?q={q}",
        "allow": r"https://cdn\.coverr\.co/[^\"'\s]+\.mp4",
        "note":  "direct Coverr files; unrelated results are filtered out",
    },
}


def video(query, limit, which=None):
    """Real video you can put in a page, from more than one source so a single
    site going down or changing its markup does not take the capability with
    it. `motion` is separate: that pulls recordings of other people's sites,
    which is reference material rather than something to ship.

    These two are what happened to verify clean today. They are a starting
    point, not the whole internet. If a brief wants something neither of them
    has, go and find a better source, use it, and say which you used."""
    names = [which] if which in VIDEO_SOURCES else list(VIDEO_SOURCES)
    got, per = [], max(1, (limit + len(names) - 1) // len(names))

    for name in names:
        src = VIDEO_SOURCES[name]
        url = src["url"].format(q=urllib.parse.quote(query))
        try:
            html = urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")
        except Exception as e:
            print(f"  [{name}] fetch failed: {e}", file=sys.stderr)
            continue
        if len(html) < 5000:
            print(f"  [{name}] body only {len(html)} bytes, treating as a fail", file=sys.stderr)
            continue

        urls = re.findall(src["allow"], html)
        # prefer a 1080 rendition over the low-res preview of the same clip
        best, seen = [], set()
        for u in urls:
            stem = re.sub(r"-\d+\.mp4$", "", u)
            if stem in seen:
                continue
            hd = stem + "-1080.mp4"
            best.append(hd if hd in urls else u)
            seen.add(stem)

        metadata = {}
        for media_url in best:
            offset = html.find(media_url)
            metadata[media_url] = {"caption": _caption_near_url(html, media_url),
                                   "page_url": url}
        files = _save(best, f"{name}-{query.replace(' ', '-')}",
                      min(per, limit - len(got)), metadata)
        print(f"  [{name}] {len(files)} clip(s), {src['note']}", file=sys.stderr)
        got += files

    if not got:
        sys.exit(f"no clips for '{query}' from any source. Try a broader word, "
                 f"or go find a source these two do not cover.")
    files = got
    print(f"{len(files)} clip(s) downloaded:\n")
    for f in files:
        print("  ", f)
    print("\nWATCH THEM before choosing. To read one as motion without a player:")
    print("  ffmpeg -i clip.mp4 -vf \"select='eq(n\\,0)+eq(n\\,25)+eq(n\\,50)',scale=640:-1,tile=3x1\" -frames:v 1 strip.png")
    return files


def isorepublic(query, limit):
    """One wired source of people, action, and lifestyle photography.

    Poly Haven is environments and materials; Dribbble and motionsites are
    different material routes.

    Plain HTTP works, but ONLY with a browser User-Agent. Without one the search
    page returns a body with zero image URLs, which reads as "no results" rather
    than as the block it actually is."""
    url = f"https://isorepublic.com/?s={urllib.parse.quote(query)}"
    try:
        html = urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        sys.exit(f"isorepublic fetch failed: {e}")
    if len(html) < 5000:
        sys.exit(f"suspiciously small body from {url} ({len(html)} bytes) - do not treat as success")

    thumbs = re.findall(r"https://isorepublic\.com/wp-content/uploads/[^\"'\s]+\.jpe?g", html)
    # strip the -450x300 style thumbnail suffix to get the full-resolution original
    full = []
    for u in thumbs:
        f = re.sub(r"-\d+x\d+(\.jpe?g)$", r"\1", u)
        if f not in full:
            full.append(f)
    if not full:
        return []
    metadata = {}
    for media_url in full:
        offset = html.find(media_url)
        metadata[media_url] = {"caption": _caption_near_url(html, media_url),
                               "page_url": url}
    files = _save(full, f"isorepublic-{query.replace(' ', '-')}", limit, metadata)
    return files


def openverse(query, limit):
    """Photography from api.openverse.org. Second wired photo source, because
    isorepublic alone was a single point of failure: its markup changed once already and left
    `photo` returning nothing with no fallback. Also takes longer phrases better than isorepublic,
    which needs a bare noun."""
    url = ("https://api.openverse.org/v1/images/?q=" + urllib.parse.quote(query)
           + "&size=large&mature=false&page_size=" + str(max(limit, 8)))
    try:
        data = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=30).read())
    except Exception as e:
        print(f"openverse fetch failed: {e}")
        return []
    results = [r for r in data.get("results", []) if r.get("url")]
    urls = [r["url"] for r in results]
    if not urls:
        return []
    metadata = {r["url"]: {"caption": r.get("title"), "page_url": r.get("foreign_landing_url")}
                for r in results}
    return _save(urls, f"openverse-{query.replace(' ', '-')}", limit, metadata)


def photo(query, limit):
    """Search photography. Tries isorepublic first (a bare noun
    works best there), then Openverse (larger index, but its search is an AND over every word, so
    a long phrase returns nothing there too -- retried on the last one or two words before giving
    up). Sources rot -- if all of that comes back empty, say so and go find a third rather than
    shipping nothing silently."""
    words = query.split()
    tries = [query]
    if len(words) > 2:
        tries.append(" ".join(words[-2:]))
    if len(words) > 1:
        tries.append(words[-1])
    files, src = [], None
    for q in tries:
        files = isorepublic(q, limit)
        if files:
            src = f"isorepublic ({q!r})"
            break
        files = openverse(q, limit)
        if files:
            src = f"openverse ({q!r})"
            break
    if not files:
        sys.exit(f"no photos found for {query!r} (tried {tries}) from isorepublic or openverse. "
                 f"Find a different source and say which.")
    print(f"{len(files)} photo(s) downloaded from {src}:\n")
    for f in files:
        print("  ", f)
    print("\nNOW OPEN THEM AND LOOK. Record which ones serve the piece and why.")
    print("Keep the complete research folder so the user can inspect every downloaded candidate.")
    return files


def mobbin(tag, limit):
    """Real shipped product UI. Mobbin is a JS app and gates deep pages behind login;
    the public browse still renders enough screens to be worth looking at."""
    StealthyFetcher = _browser_fetcher("StealthyFetcher")
    url = f"https://mobbin.com/search/apps?filter=screenText%3D{tag}"
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=90000)
    html = page.html_content or ""
    if len(html) < 5000:
        sys.exit(f"empty body from {url} - do not treat as success")
    shots = sorted(set(re.findall(r"https://[^\"'\s]*mobbin[^\"'\s]*\.(?:png|jpe?g|webp)", html)))
    if not shots:
        sys.exit("mobbin returned no screens (likely login-gated). Use dribbble/t21 instead, "
                 "and say in your report that mobbin was unavailable.")
    return _save(shots, f"mobbin-{tag}", limit)


def t21(query, limit):
    """21st.dev named component pages. Return candidates instead of thousands of unrelated CDN files."""
    DynamicFetcher = _browser_fetcher("DynamicFetcher")
    url = f"https://21st.dev/community/components/s/{urllib.parse.quote(query)}"
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=60000)
    html = _require_page(page, url)
    try:
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        items, seen = [], set()
        for link in tree.xpath("//a[@href]"):
            href = link.get("href", "")
            title = re.sub(r"\s+", " ", link.text_content()).strip()
            if "/community/components/" not in href or not title or href in seen:
                continue
            seen.add(href)
            items.append({"title": title[:500], "page_url": urllib.parse.urljoin(url, href)})
    except Exception as error:
        sys.exit(f"could not parse 21st.dev component links: {error}")
    ranked = _rank_records(items, query)
    if not ranked:
        sys.exit(f"21st.dev returned no named components for {query!r}")
    _write_candidates(f"21st-{query}", ranked[:limit])
    print(f"{min(limit, len(ranked))} named 21st.dev candidate(s):\n")
    for item in ranked[:limit]:
        print(f"  {item['title'][:70]:<72} {item['page_url']}")
    print("\nOpen the chosen page and inspect its preview and source before adapting it.")
    return []


def github3d(query, limit):
    """Open-source 3D / WebGL / shader work. Prints repos to read rather than images to look at,
    because the value here is the source, not a thumbnail."""
    searches = [f"{query} in:name,description", f"{query} three.js in:name,description",
                f"{query} webgl in:name,description"]
    items, seen = [], set()
    for search in searches:
        try:
            data = _gh("https://api.github.com/search/repositories?q=" + urllib.parse.quote(search)
                       + f"&sort=stars&per_page={min(max(limit * 3, 10), 30)}")
        except Exception:
            continue
        for item in data.get("items", []):
            if item.get("html_url") not in seen:
                seen.add(item.get("html_url")); items.append(item)
        if len(items) >= limit:
            break
    if not items:
        sys.exit("GitHub returned nothing after broad 3D, Three.js, and WebGL searches. Change the query.")
    wanted = _tokens(query)
    def relevance(item):
        text = " ".join([item.get("name", ""), item.get("description") or "",
                         " ".join(item.get("topics") or [])]).lower()
        found = _tokens(text)
        overlap = len(wanted & found)
        visual = sum(term in text for term in ("three.js", "threejs", "webgl", "shader", "glsl", "3d"))
        return visual, overlap, item.get("stargazers_count", 0)
    items = sorted(items, key=relevance, reverse=True)[:limit]
    print(f"{len(items)} repository candidate(s), relevance first:\n")
    candidates = []
    for r in items:
        print(f"  {r['stargazers_count']:>7}  {r['html_url']}")
        print(f"           {(r.get('description') or '').strip()[:110]}")
        candidates.append({"url": r["html_url"], "description": r.get("description"),
                           "stars": r.get("stargazers_count")})
    _write_candidates(f"github3d-{query.replace(' ', '-')}", candidates)
    print("\nOpen promising demos, then clone the best candidate and inspect its complete inventory.")
    return []


ASSET_KINDS = {
    "source": {".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".glsl", ".vert", ".frag", ".wgsl"},
    "image": {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"},
    "video": {".mp4", ".webm", ".mov", ".m4v"},
    "model": {".glb", ".gltf", ".obj", ".fbx", ".usdz"},
    "texture": {".hdr", ".exr", ".ktx", ".ktx2"},
    "audio": {".mp3", ".wav", ".ogg", ".m4a"},
    "font": {".woff", ".woff2", ".ttf", ".otf"},
    "data": {".json", ".csv"},
}


def _repository_inventory(destination):
    records = []
    for root, dirs, names in os.walk(destination):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "dist", "build", ".next"}]
        for filename in names:
            path = os.path.join(root, filename)
            suffix = os.path.splitext(filename)[1].lower()
            kind = next((name for name, extensions in ASSET_KINDS.items() if suffix in extensions), None)
            if not kind and filename.lower() not in {"readme", "readme.md", "package.json"}:
                continue
            record = {"path": os.path.relpath(path, destination), "kind": kind or "documentation",
                      "bytes": os.path.getsize(path)}
            if kind in {"image", "video", "model", "texture", "font"}:
                record["facts"] = _asset_facts(path)
                record["inspection_status"] = "pending"
                record["observed_description"] = None
                record["intended_job"] = None
            records.append(record)
    records.sort(key=lambda item: (item["kind"], -item["bytes"], item["path"]))
    return records


def repo(url):
    match = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?", url)
    if not match:
        sys.exit("repo needs a full https://github.com/owner/name URL")
    owner, name = match.groups()
    destination = os.path.join(OUT, "repos", f"{owner}-{name}")
    if not os.path.exists(destination):
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", url, destination],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
        if result.returncode:
            sys.exit(f"clone failed ({result.returncode}): {result.stdout[-2000:]}")
    records = _repository_inventory(destination)
    inventory_path = os.path.join(destination, "_asset_inventory.json")
    with open(inventory_path, "w") as inventory:
        json.dump({"repository": url, "root": destination, "items": records}, inventory, indent=2)
    print(f"Selected repository downloaded to:\n  {destination}")
    print(f"Inventory: {inventory_path}")
    for kind in ASSET_KINDS:
        matches = [record for record in records if record["kind"] == kind]
        if matches:
            print(f"\n{kind} ({len(matches)}):")
            for record in matches[:12]:
                print(f"  {record['bytes']:>10}  {record['path']}")
    print("\nRead the entry source and inspect every relevant bundled asset before adapting the project.")
    return destination


def fetch(url):
    if not re.match(r"^https://", url):
        sys.exit("fetch needs a direct HTTPS asset URL")
    files = _save([url], "selected-assets", 1)
    if not files:
        sys.exit("the URL did not return a downloadable asset larger than 3 KB")
    print("Selected asset downloaded to:")
    print("  ", files[0])
    print("Inspect it before using it and record what the file actually contains.")
    return files[0]


def palettes(folder):
    """Measure a folder of images into palettes that pass the design-craft colour law."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "measure_palette.py"))
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
    import numpy as np
    from PIL import Image

    kept, rejected = [], 0
    for fn in sorted(os.listdir(folder)):
        p = os.path.join(folder, fn)
        try:
            im = Image.open(p).convert("RGB"); im.thumbnail((300, 300))
            a = np.array(im)
            h, s, v = mp.rgb2hsv(a)
            m = (s > 0.18) & (v > 0.08) & (v < 0.96)
            if m.sum() < 50:
                rejected += 1; continue
            sp = mp.weighted_hue_spread(h[m], s[m])
            med = float(np.median(s[m]) * 100)
            if not (sp >= mp.MIN_SPREAD and mp.CHROMA_LO <= med <= mp.CHROMA_HI):
                rejected += 1; continue
            flat = a.reshape(-1, 3)
            q = (flat // 24 * 24)
            uniq, cnt = np.unique(q, axis=0, return_counts=True)
            top = uniq[np.argsort(-cnt)[:6]]
            kept.append({"src": fn, "hue_spread": round(sp, 1), "median_chroma": round(med, 1),
                         "palette": ["#%02x%02x%02x" % tuple(int(x) for x in c) for c in top]})
        except Exception:
            rejected += 1
    kept.sort(key=lambda r: -r["hue_spread"])
    print(json.dumps(kept, indent=1))
    print(f"\n# kept {len(kept)}, rejected {rejected} for failing the colour law", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    limit = 24
    if "--n" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--n") + 1])

    if cmd == "dribbble":
        terms = [a for a in sys.argv[2:] if not a.startswith("--")
                 and a != str(limit)]
        if not terms:
            sys.exit("need at least one tag. Give several around the subject, not just the literal "
                     "brief word: 'fitness tracker dashboard' running swimming strength-training")
        files = []
        for t in terms:
            try:
                got = dribbble(t.replace(" ", "-"), max(2, limit // len(terms)))
                print(f"  [{t}] {len(got)} file(s)", file=sys.stderr)
                files += got
            except SystemExit as e:
                print(f"  [{t}] failed: {e}", file=sys.stderr)
    elif cmd == "mobbin":
        if len(sys.argv) < 3:
            sys.exit("need a tag, e.g. onboarding / fitness / checkout")
        files = mobbin(sys.argv[2], limit)
    elif cmd == "t21":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. hero / pricing / card")
        return t21(sys.argv[2], limit) and None
    elif cmd == "github3d":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. particles / terrain / shader")
        return github3d(sys.argv[2], limit) and None
    elif cmd == "repo":
        if len(sys.argv) < 3:
            sys.exit("need a full GitHub repository URL")
        return repo(sys.argv[2]) and None
    elif cmd == "fetch":
        if len(sys.argv) < 3:
            sys.exit("need a direct HTTPS asset URL")
        return fetch(sys.argv[2]) and None
    elif cmd == "bits":
        args = [a for a in sys.argv[2:] if not a.startswith("--") and a != str(limit)]
        return bits(args[0] if args else None, limit) and None
    elif cmd == "video":
        if len(sys.argv) < 3:
            sys.exit("need a query. Optional second arg picks one source: "
                     + " / ".join(VIDEO_SOURCES))
        pick = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
        files = video(sys.argv[2], limit, pick)
        return None
    elif cmd == "photo":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. running / gym / swimming / cycling")
        files = photo(sys.argv[2], limit)
        return None
    elif cmd == "codrops":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. hover / scroll / grid / distortion / particles / text")
        return codrops(sys.argv[2], limit) and None
    elif cmd == "magicui":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. video / particles / beam / text / grid")
        return magicui(sys.argv[2], limit) and None
    elif cmd == "polyhaven":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. studio / sky / metal / fabric / concrete")
        return polyhaven(sys.argv[2], limit) and None
    elif cmd == "fontshare":
        args = [a for a in sys.argv[2:] if not a.startswith("--") and a != str(limit)]
        return fontshare(args[0] if args else None, limit) and None
    elif cmd in ("motion", "landing", "landinglove"):
        query = " ".join(a for a in sys.argv[2:] if not a.startswith("--") and a != str(limit))
        if not query:
            sys.exit(f"need a query for {cmd}; the gallery order is not research")
        files = spa(cmd, query, limit)
    elif cmd == "palettes":
        return palettes(sys.argv[2])
    else:
        sys.exit(__doc__)

    if not files:
        sys.exit(f"{cmd} returned no downloadable files. Change the query or source.")
    print(f"{len(files)} file(s) downloaded:\n")
    for f in files:
        print("  ", f)
    print("\nNOW READ THESE FILES. Judge crop, light, subject and mood on the pixels.")
    print("Record the strongest candidates and their jobs in the build.")
    print("Keep the complete research folder so the user can inspect every downloaded candidate.")


if __name__ == "__main__":
    main()
