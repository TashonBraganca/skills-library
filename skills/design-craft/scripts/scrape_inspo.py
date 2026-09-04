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

Licensing: Dribbble is DIRECTION, not stock. Study composition, palette and type from it; do not
redistribute another designer's work as your asset. Embed only CC0/CC-BY material you have
verified, and keep the attribution.
"""
import sys, os, re, json, hashlib, subprocess, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
OUT = os.path.abspath("./inspo")

SOURCES = {
    "motion":  "https://motionsites.ai/",
    "landing": "https://www.landinghero.ai/library",
    "bits":    "https://reactbits.dev/",
}


def _save(urls, subdir, limit):
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    saved, seen, source_by_path = [], set(), {}
    for u in urls:
        if len(saved) >= limit:
            break
        key = hashlib.md5(u.encode()).hexdigest()[:14]
        if key in seen:
            continue
        seen.add(key)
        ext = (re.search(r"\.(png|jpe?g|webp|avif|mp4|webm)", u.lower()) or [None, "img"])[1]
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
    by_hash, records = {}, []
    for p in saved:
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        duplicate_of = by_hash.get(h)
        if not duplicate_of:
            by_hash[h] = p
        records.append({
            "local_path": p,
            "source_url": source_by_path[p],
            "bytes": os.path.getsize(p),
            "content_md5": h,
            "duplicate_of": duplicate_of,
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
    url = f"https://dribbble.com/tags/{tag}"
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=90000)
    html = page.html_content or ""
    if len(html) < 5000 or re.search(r"just a moment|checking your browser", html, re.I):
        sys.exit(f"blocked or empty body from {url} ({len(html)} bytes) - do not treat as success")
    shots = [u for u in re.findall(r"https://cdn\.dribbble\.com/(?:userupload|uploads)/[^\"'\s?]+", html)
             if re.search(r"\.(png|jpe?g|webp)$", u)]
    return _save(shots, f"dribbble-{tag}", limit)


def spa(which, limit):
    DynamicFetcher = _browser_fetcher("DynamicFetcher")
    url = SOURCES[which]
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=60000)
    html = page.html_content or ""
    if len(html) < 3000:
        sys.exit(f"empty body from {url} - JS did not render, do not treat as success")
    pat = (r"https?://[^\"'\s]+\.(?:mp4|webm)" if which == "motion"
           else r"https?://[^\"'\s]+\.(?:png|jpe?g|webp|avif)")
    return _save(sorted(set(re.findall(pat, html))), which, limit)


def codrops(query, limit):
    """Codrops demos. The best source of unusual, genuinely non-generic web effects, and every
    article ships a working MIT repo. Prints repos to read, because the value is the source."""
    q = urllib.parse.quote(f"{query} user:codrops")
    try:
        data = _gh(f"https://api.github.com/search/repositories?q={q}&sort=updated"
                   f"&per_page={min(limit, 20)}")
    except Exception as e:
        sys.exit(f"codrops search failed: {e}")
    items = data.get("items", [])
    if not items:
        sys.exit(f"nothing for '{query}' in Codrops. Widen it, or browse https://tympanus.net/codrops/")
    print(f"{len(items)} Codrops demo(s):\n")
    candidates = []
    for r in items:
        print(f"  {r['html_url']}")
        print(f"      {(r.get('description') or '').strip()[:110]}")
        print(f"      licence: {(r.get('license') or {}).get('spdx_id', 'check the repo')}")
        candidates.append({"url": r["html_url"], "description": r.get("description"),
                           "license": (r.get("license") or {}).get("spdx_id")})
    _write_candidates(f"codrops-{query.replace(' ', '-')}", candidates)
    print("\nCLONE OR READ THE SOURCE of the one that fits. Codrops demos are MIT unless the repo")
    print("says otherwise. Adapt the technique, keep the credit.")
    return []


def polyhaven(query, limit):
    """CC0 HDRIs, textures and 3D models. Public domain, so no attribution burden, and the
    quality is far above the stock-photo sites."""
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
    print(f"{len(out)} CC0 asset(s) on Poly Haven (public domain, no attribution required):\n")
    candidates = []
    for kind, slug, name in out:
        print(f"  [{kind:<8}] {name}")
        print(f"             https://polyhaven.com/a/{slug}")
        print(f"             file: https://dl.polyhaven.org/file/ph-assets/{kind.capitalize()}"
              f"/hdr/2k/{slug}_2k.hdr" if kind == "hdris" else
              f"             browse the page for the resolution you want")
        candidates.append({"kind": kind, "slug": slug, "name": name,
                           "url": f"https://polyhaven.com/a/{slug}", "license": "CC0"})
    _write_candidates(f"polyhaven-{query.replace(' ', '-')}", candidates)
    print("\nCC0: use freely, no credit needed. Verify the file URL returns 200 before shipping it.")
    return []


def fontshare(query, limit):
    """Free quality typefaces, well outside the Google Fonts default set."""
    try:
        data = _gh_plain("https://api.fontshare.com/v2/fonts?limit=100")
    except Exception as e:
        sys.exit(f"fontshare failed: {e}")
    fonts = data.get("fonts", data.get("data", data if isinstance(data, list) else []))
    if query:
        fonts = [f for f in fonts if query.lower() in json.dumps(f).lower()]
    fonts = fonts[:limit]
    if not fonts:
        sys.exit("nothing matched on Fontshare. Run with no query to list them all.")
    print(f"{len(fonts)} typeface(s) on Fontshare (free for commercial use):\n")
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
    """React Bits. Scraping the website returned icons and logos, which is useless. The components
    are MIT-licensed source on GitHub, so fetch the actual code instead: that is the thing worth
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

    d = os.path.join(OUT, "react-bits", name)
    os.makedirs(d, exist_ok=True)
    saved = []
    for cat in RB_CATS:
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
        break
    if not saved:
        sys.exit(f"no React Bits component called '{name}'. Run `bits` with no argument to list them.")
    print(f"{len(saved)} source file(s) for {name}:\n")
    for p in saved:
        print("  ", p)
    print("\nNOW READ THE SOURCE. It is MIT licensed: use it, adapt it, keep the attribution.")
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
        "note":  "free for commercial use, no credit required",
    },
    "coverr": {
        "url":   "https://coverr.co/s?q={q}",
        "allow": r"https://cdn\.coverr\.co/[^\"'\s]+\.mp4",
        "note":  "free for commercial use; istockphoto results are filtered out",
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
    got, per = [], max(2, limit // len(names))

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

        files = _save(best, f"{name}-{query.replace(' ', '-')}", per)
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
    print("Free for commercial use, no credit required. Do not resell as stock.")
    return files


def isorepublic(query, limit):
    """Real photography, CC0, free for commercial use with no attribution required.
    Verified 2026-09-04 at https://isorepublic.com/license/ in their own words:
    "free to use for personal and commercial projects" and "You can use a CC0
    licensed photo or video without purchase, permission, or giving attribution
    to the creator of the work." The one restriction: you may not pass the work
    off as your own or resell it as stock.

    This is the ONLY wired source of real people/action/lifestyle photography.
    Poly Haven is environments and materials; Dribbble and motionsites are
    direction only and must never be shipped as assets. Unsplash, Pexels and
    Picsum are banned on sight: overused to the point of being a tell.

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
    files = _save(full, f"isorepublic-{query.replace(' ', '-')}", limit)
    return files


def openverse(query, limit):
    """Real photography, CC0/public-domain, from api.openverse.org (Openverse, the CC/WordPress
    search index over hundreds of open collections). Second wired photo source, because
    isorepublic alone was a single point of failure: its markup changed once already and left
    `photo` returning nothing with no fallback. Also takes longer phrases better than isorepublic,
    which needs a bare noun."""
    url = ("https://api.openverse.org/v1/images/?q=" + urllib.parse.quote(query)
           + "&license=cc0,pdm&size=large&mature=false&page_size=" + str(max(limit, 8)))
    try:
        data = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=30).read())
    except Exception as e:
        print(f"openverse fetch failed: {e}")
        return []
    urls = [r["url"] for r in data.get("results", []) if r.get("url")]
    if not urls:
        return []
    return _save(urls, f"openverse-{query.replace(' ', '-')}", limit)


def photo(query, limit):
    """Real photography you can ship, CC0, no credit needed. Tries isorepublic first (a bare noun
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
    print("CC0: safe to ship, no credit required. Do not claim authorship, do not resell as stock.")
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
    """21st.dev component previews."""
    DynamicFetcher = _browser_fetcher("DynamicFetcher")
    url = f"https://21st.dev/s/{query}"
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=60000)
    html = page.html_content or ""
    if len(html) < 3000:
        sys.exit(f"empty body from {url} - JS did not render, do not treat as success")
    shots = sorted(set(re.findall(r"https?://[^\"'\s]+\.(?:png|jpe?g|webp|avif|mp4)", html)))
    return _save(shots, f"21st-{query}", limit)


def github3d(query, limit):
    """Open-source 3D / WebGL / shader work. Prints repos to read rather than images to look at,
    because the value here is the source, not a thumbnail."""
    q = urllib.parse.quote(f"{query} in:name,description topic:webgl stars:>100")
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&per_page={min(limit, 20)}"
    try:
        data = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers={**UA, "Accept": "application/vnd.github+json"}),
            timeout=30).read())
    except Exception as e:
        sys.exit(f"github search failed: {e}")
    items = data.get("items", [])
    if not items:
        sys.exit("github search returned nothing - widen the query")
    print(f"{len(items)} repo(s), most-starred first:\n")
    candidates = []
    for r in items:
        print(f"  {r['stargazers_count']:>7}  {r['html_url']}")
        print(f"           {(r.get('description') or '').strip()[:110]}")
        print(f"           licence: {(r.get('license') or {}).get('spdx_id', 'NONE')}")
        candidates.append({"url": r["html_url"], "description": r.get("description"),
                           "stars": r.get("stargazers_count"),
                           "license": (r.get("license") or {}).get("spdx_id")})
    _write_candidates(f"github3d-{query.replace(' ', '-')}", candidates)
    print("\nNOW OPEN THE PROMISING ONES. Read the source, run the demo if there is one.")
    print("Check the licence before you take anything, and keep the attribution.")
    return []


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
    files = []
    for root, dirs, names in os.walk(destination):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "dist", "build"}]
        for filename in names:
            path = os.path.join(root, filename)
            if os.path.getsize(path) <= 250_000 and re.search(
                    r"(^README|^LICENSE|package\.json$|\.(?:js|jsx|ts|tsx|css|glsl|vert|frag)$)",
                    filename, re.I):
                files.append(path)
    print(f"Selected repository downloaded to:\n  {destination}")
    print("\nRead the licence, README, and relevant source before adapting it.")
    for path in files[:80]:
        print("  ", path)
    return destination


def fetch(url):
    if not re.match(r"^https://", url):
        sys.exit("fetch needs a direct HTTPS asset URL")
    files = _save([url], "selected-assets", 1)
    if not files:
        sys.exit("the URL did not return a downloadable asset larger than 3 KB")
    print("Selected asset downloaded to:")
    print("  ", files[0])
    print("Inspect it before using it and keep its licence or attribution with the project.")
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
        files = t21(sys.argv[2], limit)
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
    elif cmd == "polyhaven":
        if len(sys.argv) < 3:
            sys.exit("need a query, e.g. studio / sky / metal / fabric / concrete")
        return polyhaven(sys.argv[2], limit) and None
    elif cmd == "fontshare":
        args = [a for a in sys.argv[2:] if not a.startswith("--") and a != str(limit)]
        return fontshare(args[0] if args else None, limit) and None
    elif cmd in ("motion", "landing"):
        files = spa(cmd, limit)
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
