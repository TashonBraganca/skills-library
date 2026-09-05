#!/usr/bin/env python3
"""Read-only smoke test for rendered design reference sources."""
import re
import sys

from lxml import html as lxml_html
from scrapling.fetchers import DynamicFetcher


SOURCES = {
    "landinglove": "https://www.landing.love/",
    "magicui": "https://magicui.design/docs/components",
    "landinghero": "https://www.landinghero.ai/library",
    "motion": "https://motionsites.ai/",
    "t21": "https://21st.dev/community/components/s/hero",
}


selected = dict(SOURCES)
if len(sys.argv) > 1:
    unknown = [name for name in sys.argv[1:] if name not in SOURCES]
    if unknown:
        raise SystemExit(f"unknown source: {', '.join(unknown)}")
    selected = {name: SOURCES[name] for name in sys.argv[1:]}

failures = []
for name, url in selected.items():
    try:
        page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=90000)
        body = page.html_content or ""
    except Exception as error:
        failures.append(f"{name}: fetch failed: {error}")
        print(f"{name}: FAIL fetch error")
        continue
    videos = re.findall(r'https?://[^"\' ]+\.(?:mp4|webm)', body)
    images = re.findall(r'https?://[^"\' ]+\.(?:png|jpe?g|webp|avif)', body)
    text = re.sub(r"\s+", " ", lxml_html.fromstring(body).text_content()).strip()
    print(f"{name}: status={page.status} bytes={len(body)} videos={len(videos)} images={len(images)}")
    print(f"  {text[:320]}")
    if page.status != 200:
        failures.append(f"{name}: HTTP {page.status}")
    if len(body) < 3000 or len(text) < 120:
        failures.append(f"{name}: empty or blocked response")
    if name in {"landinglove", "motion"} and not videos:
        failures.append(f"{name}: no video media found")
    if name in {"magicui", "landinghero", "t21"} and not (images or "component" in text.lower()):
        failures.append(f"{name}: no component or visual evidence found")
    tree = lxml_html.fromstring(body)
    if name in {"landinglove", "motion", "t21"}:
        for node in tree.xpath("//video")[:2]:
            media = node.get("src") or " ".join(node.xpath(".//source/@src"))
            parent = node
            for depth in range(1, 7):
                parent = parent.getparent() if parent is not None else None
                label = re.sub(r"\s+", " ", parent.text_content()).strip()[:180] if parent is not None else ""
                hrefs = parent.xpath(".//a[@href]/@href") if parent is not None else []
                print(f"  video ancestor {depth}: {label!r} href={hrefs[:2]} media={media[:90]}")
    if name == "magicui":
        shown = 0
        for link in tree.xpath("//a[@href]"):
            label = re.sub(r"\s+", " ", link.text_content()).strip()
            if label and any(word in label.lower() for word in ("video", "particle", "beam", "grid", "text")):
                print(f"  component: {label[:100]!r} {link.get('href')}")
                shown += 1
                if shown == 8:
                    break

if failures:
    print("\nFAILED:", file=sys.stderr)
    for failure in failures:
        print(f"  {failure}", file=sys.stderr)
    raise SystemExit(1)
