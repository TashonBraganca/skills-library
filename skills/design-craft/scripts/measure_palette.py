#!/usr/bin/env python3
"""Measure a rendered page against the design-craft colour law. Exits non-zero on failure.

    measure_palette.py <url|html-file> [--json] [--shots N]

Renders the page (Playwright if available, else treats the arg as an image), samples several
scroll positions, and measures area-weighted hue spread, median chroma, and text/ground contrast
over real pixels. Counting CSS hex strings gives the wrong answer -- that approach was tested and
discarded, because hex frequency does not reflect how much of the screen a colour occupies.

Thresholds are empirical: derived from ten generated pages scored by a human, area-weighted.
    hue spread   >= 17 deg   (liked 17.6-41.5 / rejected 3.1-10.3)
    median chroma  30-53 %   (liked 33-51 / rejected 56-87)

Reproduces all 9 scored human verdicts. NOTE: fitted on those same 9 points, so it is a fitted
rule and not yet an out-of-sample validated predictor. Treat a PASS as "inside the band the
person liked", not as proof the design is good.

Readability is deliberately NOT gated here. Pixel-area contrast was tried and rejected: on a dark
page the two largest areas are both near-black ground shades and body text is too small an area to
register, so it scored ~1.2:1 on every dark page whether readable or not -- and it wrongly failed
three pages the reviewer liked. Readability needs the DOM: use check_contrast.py.
"""
import sys, os, math, json, tempfile, subprocess

MIN_SPREAD = 17.0
CHROMA_LO, CHROMA_HI = 30.0, 53.0
MIN_CONTRAST = 4.5

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("needs pillow + numpy:  pip3 install --user --break-system-packages pillow numpy")


def rgb2hsv(a):
    a = a.astype(np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    v = mx
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    h = np.zeros_like(mx)
    m = d > 1e-9
    i = (mx == r) & m; h[i] = ((g - b)[i] / d[i]) % 6
    i = (mx == g) & m; h[i] = ((b - r)[i] / d[i]) + 2
    i = (mx == b) & m; h[i] = ((r - g)[i] / d[i]) + 4
    return (h / 6.0) % 1.0, s, v


def weighted_hue_spread(h, w):
    """Circular standard deviation of hue, weighted by saturation. Degrees."""
    if w.sum() < 1:
        return 0.0
    a = h * 2 * np.pi
    S = (np.sin(a) * w).sum() / w.sum()
    C = (np.cos(a) * w).sum() / w.sum()
    R = math.hypot(S, C)
    return math.degrees(math.sqrt(max(0.0, -2 * math.log(max(R, 1e-9)))))


def _lin(x):
    x /= 255.0
    return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4


def contrast(c1, c2):
    l1 = 0.2126 * _lin(c1[0]) + 0.7152 * _lin(c1[1]) + 0.0722 * _lin(c1[2])
    l2 = 0.2126 * _lin(c2[0]) + 0.7152 * _lin(c2[1]) + 0.0722 * _lin(c2[2])
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def render(target, n_shots=3):
    """Screenshot a url/file at several scroll positions. Returns list of PNG paths."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    url = target if target.startswith("http") else "file://" + os.path.abspath(target)
    out = []
    tmp = tempfile.mkdtemp(prefix="dc-shots-")
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb", "--hide-scrollbars"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(url, wait_until="load", timeout=60000)
        pg.wait_for_timeout(3500)
        H = pg.evaluate("document.body.scrollHeight")
        for i in range(n_shots):
            frac = 0.0 if n_shots == 1 else (i / max(n_shots - 1, 1)) * 0.8
            pg.evaluate(f"window.scrollTo(0,{int(H * frac)})")
            pg.wait_for_timeout(1600)
            f = os.path.join(tmp, f"s{i}.png")
            pg.screenshot(path=f)
            out.append(f)
        b.close()
    return out


def dominant_pair_contrast(a):
    """Contrast between the two colours that occupy the most screen area.

    Measuring darkest-vs-lightest pixel is useless -- a single white pixel makes any page pass.
    That was tested: an page a reviewer described only as "can't read shit" scored 20.6:1 that way.
    Two dominant areas close in luminance is what actually reads as muddy and unreadable.
    """
    q = (a // 24 * 24).reshape(-1, 3)                    # coarse quantise
    uniq, cnt = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-cnt)
    top = uniq[order[:8]]
    weights = cnt[order[:8]] / cnt.sum()
    # dominant ground = biggest area; partner = the highest-area colour with usable contrast
    ground = top[0]
    best = 0.0
    for c, w in zip(top[1:], weights[1:]):
        if w < 0.01:
            continue
        best = max(best, contrast(ground, c))
    return best, ground


def measure(paths):
    Hs, Ws, total = [], [], 0
    pair_contrasts = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail((320, 320))
        a = np.array(im)
        h, s, v = rgb2hsv(a)
        mask = (s > 0.18) & (v > 0.08) & (v < 0.96)
        total += h.size
        Hs.append(h[mask]); Ws.append(s[mask])
        c, _ = dominant_pair_contrast(a)
        pair_contrasts.append(c)
    H = np.concatenate(Hs) if Hs else np.array([])
    W = np.concatenate(Ws) if Ws else np.array([])
    return {
        "hue_spread": round(weighted_hue_spread(H, W), 1) if len(H) else 0.0,
        "median_chroma": round(float(np.median(W) * 100), 1) if len(W) else 0.0,
        "chromatic_pixels_pct": round(100 * len(H) / max(total, 1), 1),
        "dominant_contrast": round(float(np.median(pair_contrasts)), 2) if pair_contrasts else 0.0,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        sys.exit(__doc__)
    target = args[0]
    n = 3
    if "--shots" in sys.argv:
        n = int(sys.argv[sys.argv.index("--shots") + 1])

    if target.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        paths = [target]
    else:
        paths = render(target, n)
        if paths is None:
            sys.exit("playwright not available - pass a screenshot image instead, or install it")

    m = measure(paths)
    fails = []
    if m["hue_spread"] < MIN_SPREAD:
        fails.append(f"hue spread {m['hue_spread']} deg < {MIN_SPREAD} "
                     f"(one hue is tinting everything - add a second, genuinely different hue family)")
    if not (CHROMA_LO <= m["median_chroma"] <= CHROMA_HI):
        d = "too saturated - reads poppy" if m["median_chroma"] > CHROMA_HI else "too desaturated - reads dead"
        fails.append(f"median chroma {m['median_chroma']}% outside {CHROMA_LO}-{CHROMA_HI}% ({d})")

    if as_json:
        print(json.dumps({**m, "pass": not fails, "failures": fails}, indent=1))
    else:
        print(f"hue spread      {m['hue_spread']} deg   (need >= {MIN_SPREAD})")
        print(f"median chroma   {m['median_chroma']}%    (need {CHROMA_LO}-{CHROMA_HI})")
        print(f"dominant contrast {m['dominant_contrast']}:1  (informational - see check_contrast.py)")
        print(f"chromatic area  {m['chromatic_pixels_pct']}%")
        print()
        if fails:
            print("FAIL")
            for f in fails:
                print("  -", f)
        else:
            print("PASS - palette is inside the measured band")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
