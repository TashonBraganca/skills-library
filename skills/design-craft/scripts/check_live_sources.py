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
    selected = {name: SOURCES[name] for name in sys.argv[1:]}

for name, url in selected.items():
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=90000)
    body = page.html_content or ""
    videos = re.findall(r'https?://[^"\' ]+\.(?:mp4|webm)', body)
    images = re.findall(r'https?://[^"\' ]+\.(?:png|jpe?g|webp|avif)', body)
    text = re.sub(r"\s+", " ", lxml_html.fromstring(body).text_content()).strip()
    print(f"{name}: status={page.status} bytes={len(body)} videos={len(videos)} images={len(images)}")
    print(f"  {text[:320]}")
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
