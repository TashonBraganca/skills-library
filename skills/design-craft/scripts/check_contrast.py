#!/usr/bin/env python3
"""Check every visible text element against its effective background. Exits non-zero on failure.

    check_contrast.py <url|html-file> [--json] [--min 4.5]

Walks the live DOM, reads each text element's computed colour and the first non-transparent
background behind it, and computes the WCAG ratio. Large text (>= 24px, or >= 18.66px bold) is
held to 3:1 per WCAG AA; everything else to 4.5:1.

Why the DOM and not pixels: pixel-area contrast was tried first and failed badly. On a dark page
the two largest colour areas are both near-black ground shades, and body text is far too small an
area to register -- it scored ~1.2:1 on every dark page whether readable or not, and wrongly
failed three pages a reviewer liked. Text contrast is a property of elements, not of area.
"""
import sys, os, json

JS = r"""
() => {
  const lum = (c) => {
    const f = (x) => { x /= 255; return x <= 0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4); };
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]);
  };
  const ratio = (a, b) => {
    const [hi, lo] = [lum(a), lum(b)].sort((x,y) => y-x);
    return (hi + 0.05) / (lo + 0.05);
  };
  const parse = (s) => {
    const m = s && s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(Number);
    return { rgb: [p[0], p[1], p[2]], a: p.length > 3 ? p[3] : 1 };
  };
  // first ancestor with a non-transparent background
  const groundOf = (el) => {
    let n = el;
    while (n && n !== document.documentElement) {
      const bg = parse(getComputedStyle(n).backgroundColor);
      if (bg && bg.a > 0.5) return bg.rgb;
      n = n.parentElement;
    }
    const rb = parse(getComputedStyle(document.body).backgroundColor);
    return rb && rb.a > 0.5 ? rb.rgb : [0, 0, 0];
  };
  const out = [];
  const els = document.querySelectorAll('p,h1,h2,h3,h4,h5,h6,span,a,li,td,th,label,button,small,strong,em,figcaption,blockquote');
  for (const el of els) {
    // only elements with their own directly-rendered text
    const own = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3)
      .map(n => n.textContent.trim())
      .join(' ')
      .trim();
    if (own.length < 3) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const op = parseFloat(cs.opacity);
    if (!isNaN(op) && op < 0.15) continue;          // effectively invisible, not a contrast bug
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    const fg = parse(cs.color);
    if (!fg) continue;
    const px = parseFloat(cs.fontSize) || 16;
    const bold = (parseInt(cs.fontWeight, 10) || 400) >= 700;
    const large = px >= 24 || (px >= 18.66 && bold);
    const cr = ratio(fg.rgb, groundOf(el));
    out.push({
      tag: el.tagName.toLowerCase(),
      cls: (el.className && String(el.className).slice(0, 40)) || '',
      text: own.slice(0, 48),
      px: Math.round(px), large, ratio: Math.round(cr * 100) / 100
    });
  }
  return out;
}
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    target = args[0]
    as_json = "--json" in sys.argv
    floor = 4.5
    if "--min" in sys.argv:
        floor = float(sys.argv[sys.argv.index("--min") + 1])

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("needs playwright:  pip3 install --user --break-system-packages playwright "
                 "&& python3 -m playwright install chromium")

    url = target if target.startswith("http") else "file://" + os.path.abspath(target)
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(url, wait_until="load", timeout=60000)
        pg.wait_for_timeout(3000)
        H = pg.evaluate("document.body.scrollHeight")
        seen = set()
        for frac in (0.0, 0.35, 0.7):                 # reveal-on-scroll content must be measured too
            pg.evaluate(f"window.scrollTo(0,{int(H * frac)})")
            pg.wait_for_timeout(1400)
            for r in pg.evaluate(JS):
                k = (r["tag"], r["cls"], r["text"])
                if k in seen:
                    continue
                seen.add(k)
                rows.append(r)
        b.close()

    fails = [r for r in rows if r["ratio"] < (3.0 if r["large"] else floor)]
    fails.sort(key=lambda r: r["ratio"])

    if as_json:
        print(json.dumps({"checked": len(rows), "failures": fails, "pass": not fails}, indent=1))
    else:
        print(f"checked {len(rows)} text elements against their effective background\n")
        if not fails:
            print(f"PASS - every element meets its WCAG AA floor "
                  f"({floor}:1 normal, 3:1 large)")
        else:
            print(f"FAIL - {len(fails)} element(s) below the floor:\n")
            for r in fails[:25]:
                need = 3.0 if r["large"] else floor
                print(f"  {r['ratio']:>5}:1 (need {need})  <{r['tag']}> {r['px']}px"
                      f"{' large' if r['large'] else ''}  .{r['cls'][:24]}  \"{r['text'][:36]}\"")
            if len(fails) > 25:
                print(f"  ... and {len(fails) - 25} more")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
