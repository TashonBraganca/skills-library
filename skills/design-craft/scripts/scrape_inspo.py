#!/usr/bin/env python3
"""Pull real design references and assets, then hand them to you as local files to LOOK at.

    scrape_inspo.py dribbble <tag> [--n 24]      # direction: what good looks like now
    scrape_inspo.py motion                        # real .mp4 motion assets
    scrape_inspo.py landing                       # landing-page layout references
    scrape_inspo.py palettes <dir>                # measure a folder of images -> palette JSON

Downloads to ./inspo/<source>/ and prints the paths. **You must then read the image files
yourself.** That step is the entire point: text search returns captions, and choosing a
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
import sys, os, re, json, hashlib, urllib.request

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
    saved, seen = [], set()
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
            saved.append(p); continue
        try:
            data = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
            if len(data) < 3000:                     # too small to be a real asset
                continue
            open(p, "wb").write(data)
            saved.append(p)
        except Exception:
            pass
    # drop byte-identical duplicates
    by_hash, dedup = {}, []
    for p in saved:
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        if h in by_hash:
            os.remove(p); continue
        by_hash[h] = p; dedup.append(p)
    return dedup


def dribbble(tag, limit):
    from scrapling.fetchers import StealthyFetcher
    url = f"https://dribbble.com/tags/{tag}"
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=90000)
    html = page.html_content or ""
    if len(html) < 5000 or re.search(r"just a moment|checking your browser", html, re.I):
        sys.exit(f"blocked or empty body from {url} ({len(html)} bytes) - do not treat as success")
    shots = [u for u in re.findall(r"https://cdn\.dribbble\.com/(?:userupload|uploads)/[^\"'\s?]+", html)
             if re.search(r"\.(png|jpe?g|webp)$", u)]
    return _save(shots, f"dribbble-{tag}", limit)


def spa(which, limit):
    from scrapling.fetchers import DynamicFetcher
    url = SOURCES[which]
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=60000)
    html = page.html_content or ""
    if len(html) < 3000:
        sys.exit(f"empty body from {url} - JS did not render, do not treat as success")
    pat = (r"https?://[^\"'\s]+\.(?:mp4|webm)" if which == "motion"
           else r"https?://[^\"'\s]+\.(?:png|jpe?g|webp|avif)")
    return _save(sorted(set(re.findall(pat, html))), which, limit)


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
        if len(sys.argv) < 3:
            sys.exit("need a tag, e.g. minimal / editorial / typography / dashboard")
        files = dribbble(sys.argv[2], limit)
    elif cmd in ("motion", "landing", "bits"):
        files = spa(cmd, limit)
    elif cmd == "palettes":
        return palettes(sys.argv[2])
    else:
        sys.exit(__doc__)

    print(f"{len(files)} file(s) downloaded:\n")
    for f in files:
        print("  ", f)
    print("\nNOW READ THESE FILES. Judge crop, light, subject and mood on the pixels.")
    print("Then keep the two or three that genuinely serve the piece and delete the rest.")


if __name__ == "__main__":
    main()
