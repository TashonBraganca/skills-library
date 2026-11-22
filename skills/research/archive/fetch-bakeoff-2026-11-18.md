# Fetch bake-off, 2026-11-18

Which fetcher returns real page text? 15 real URLs, 5 fetchers, one run each, from one Mac on one home IP.
Script: `scripts/bakeoff.py`. Raw data: `fetch-bakeoff-2026-11-18.json`.

## How a cell is scored

- **OK** means two checks passed. (1) The validity check in `scripts/fetch.py`: HTTP 2xx, at least 500 characters of text, and no CAPTCHA, login, challenge or "enable JavaScript" wall. (2) The text contains a configured token. The historical success label means the response passed a heuristic and contained that token. Generic tokens (for example "points", "Symbol", "Scrapling") can match navigation or a stub. The run did not verify full extraction or claim-bearing content. Tokens are listed in `bakeoff.py` (for example "noob trap" for the Reddit thread, "Representation Engineering" for the arXiv paper).
- **stub** means the validity check passed but the token was missing. The fetcher got a page, not the content. Counting these as wins would have inflated Scrapling's Reddit result and Crawl4AI's YouTube and hn.algolia results.
- **FAIL** gives the reason. `c` is characters of clean text, `s` is seconds for the whole call, including browser start.
- Characters are not comparable across fetchers. Jina and Crawl4AI keep navigation and footers. `fetch.py` strips them and prefers `<article>` or `<main>`. Compare success, not size.
- The last column runs `fetch.py` as shipped: special routes first (X through fxtwitter, Reddit through `reddit.py`, YouTube through `youtube.py`), then the chain scrapling, jina, stealthy, urllib.

## Results

| # | page | Scrapling Fetcher | Scrapling StealthyFetcher | Jina Reader | plain urllib | Crawl4AI 0.9.5 | fetch.py default |
|---|---|---|---|---|---|---|---|
| 1 | JS-heavy SPA (`spa-hn-algolia`) | FAIL empty body 0.9s | OK 5,546c 6.4s | OK 16,020c 7.4s | FAIL empty body 0.8s | stub 837c 2.0s | OK 16,020c 2.4s via jina |
| 2 | JS-heavy SPA (`spa-tradingview`) | OK 12,683c 0.3s | OK 12,914c 4.4s | OK 61,998c 2.5s | OK 12,683c 0.3s | OK 62,375c 1.6s | OK 12,683c 0.4s via scrapling |
| 3 | Cloudflare test page (`cf-nowsecure`) | FAIL too short (129 chars) 18.7s | FAIL hard timeout after 105s 105.0s | FAIL too short (60 chars) 2.7s | FAIL too short (129 chars) 0.9s | FAIL too short (57 chars) 8.5s | FAIL 63.6s |
| 4 | Cloudflare-protected (`cf-g2`) | FAIL HTTP 403 0.3s | FAIL HTTP 403 3.5s | FAIL empty body 15.5s | FAIL HTTP 403 0.2s | FAIL Blocked by anti-bot protection: DataDo 1.3s | FAIL 18.6s |
| 5 | arXiv HTML paper (`arxiv-html`) | OK 167,033c 0.6s | OK 167,033c 6.8s | FAIL too short (25 chars) 3.2s | OK 167,033c 0.4s | OK 231,163c 5.1s | OK 167,033c 0.6s via scrapling |
| 6 | Medium post (`medium`) | OK 5,105c 1.0s | OK 5,224c 4.3s | FAIL HTTP 403 0.6s | FAIL HTTP 403 0.4s | OK 13,766c 2.1s | OK 5,105c 1.2s via scrapling |
| 7 | Substack post (`substack`) | OK 12,890c 0.3s | OK 13,110c 3.6s | OK 26,198c 3.5s | OK 12,890c 0.2s | OK 23,621c 1.2s | OK 12,890c 0.3s via scrapling |
| 8 | GitHub README (`github-readme`) | OK 21,940c 1.1s | OK 21,940c 7.8s | FAIL HTTP 403 0.4s | OK 21,940c 1.0s | OK 69,841c 1.8s | OK 21,940c 0.5s via scrapling |
| 9 | docs site (`docs-uv`) | OK 8,057c 0.3s | OK 8,057c 2.3s | OK 19,139c 1.9s | OK 8,057c 0.2s | OK 28,388c 1.2s | OK 8,057c 0.3s via scrapling |
| 10 | Reddit thread (`reddit-thread`) | stub 1,252c 0.9s | FAIL HTTP 403 1.8s | FAIL Title:   URL Source: https://www.reddi 1.9s | FAIL empty body 0.2s | stub 5,590c 1.3s | OK 4,708c 10.5s via reddit.py (Arctic Shift) |
| 11 | X post (`x-post`) | OK 3,966c 1.0s | OK 3,828c 48.7s | OK 12,969c 4.6s | OK 3,966c 0.8s | OK 12,892c 1.5s | OK 164c 0.8s via fxtwitter |
| 12 | YouTube page (`youtube`) | FAIL too short (136 chars) 0.8s | OK 12,219c 5.7s | FAIL Title: The Science of Neural Networks  6.5s | FAIL too short (136 chars) 0.8s | stub 857c 1.8s | OK 60,420c 1.8s via youtube.py |
| 13 | news site (`news-guardian`) | OK 1,949c 0.6s | OK 1,949c 2.8s | OK 23,503c 6.6s | OK 1,949c 0.4s | OK 18,431c 1.1s | OK 1,949c 0.6s via scrapling |
| 14 | forum (Discourse) (`forum-pytorch`) | FAIL too short (37 chars) 1.5s | OK 3,284c 59.3s | OK 10,098c 16.0s | FAIL too short (37 chars) 1.4s | OK 10,032c 11.1s | OK 10,098c 17.3s via jina |
| 15 | PDF (`pdf-attention`) | FAIL PDF body, not text (use jina, or insta 1.2s | FAIL empty body 2.4s | OK 40,580c 2.2s | FAIL PDF body, not text (use jina, or insta 1.0s | FAIL Unexpected error in _crawl_web at line 0.6s | OK 40,580c 3.0s via jina |

| fetcher | real content | valid but stub | failed | median seconds (all 15) | median seconds (successes) |
|---|---|---|---|---|---|
| Scrapling Fetcher | 8 | 1 | 6 | 0.9 | 0.6 |
| Scrapling StealthyFetcher | 11 | 0 | 4 | 4.4 | 5.7 |
| Jina Reader | 8 | 0 | 7 | 3.2 | 4.0 |
| plain urllib | 7 | 0 | 8 | 0.4 | 0.4 |
| Crawl4AI 0.9.5 | 9 | 3 | 3 | 1.6 | 1.6 |
| fetch.py default chain (with routes) | 13 | 0 | 2 | 1.2 | 0.8 |

## What the data says

- **Plain Scrapling `Fetcher` is the right first try.** It succeeded on 8 of 15, in a median 0.6 s. In this run, Scrapling failed on the sampled HN SPA, Discourse thread, PDF, and two bot-protected pages.
- **Jina Reader rescues what Scrapling cannot render**: the hn.algolia SPA, the Discourse forum and the PDF. It returns 403 for GitHub, 403 for Medium, and failed on arXiv HTML and on Reddit and YouTube pages.
- **StealthyFetcher (headless browser) had the best raw coverage, 11 of 15, but is slow.** Median 5.7 s on successes. Two calls took 48 s and 59 s because it waits for network idle, and one hit a 105 s hard timeout on the Cloudflare test page. Use it third.
- **Plain urllib added nothing** beyond Scrapling in this run. Medium returned 403 to it here and 200 in an earlier partial run, so results for protected sites vary between runs. It stays last as a no-dependency fallback.
- **Both bot-protected pages failed on every fetcher**: nowsecure.nl (Cloudflare challenge) and g2.com (DataDome captcha, HTTP 403). Do not expect these to work. Report the failure and use another source.
- **Reddit, X and YouTube need their own routes.** Scrapling returned a 1,252-character stub for the Reddit thread. YouTube pages need the transcript route. X status pages did render through Scrapling today (3,966 characters including the post), but they give no reply counts or dates in a clean form, so `fetch.py` uses fxtwitter first.
- **Default `fetch.py`: 13 of 15 real, median 0.8 s on successes.** The two misses are the Cloudflare and DataDome pages.

## Default chain

1. Special routes: X status to fxtwitter, Reddit thread to `reddit.py`, YouTube to `youtube.py`.
2. `scrapling` (Fetcher): fast, no browser.
3. `jina` (Jina Reader, sent with `X-No-Cache: true`, because Jina otherwise serves cached snapshots and the owner needs fresh pages): JS rendering and PDFs.
4. `stealthy` (Scrapling StealthyFetcher): last resort for pages that need a real browser.
5. `urllib`: plain HTTP fallback.

Generic routes apply a text heuristic. Specialized routes (X, Reddit, YouTube) have their own acceptance criteria, and a failed specialized route no longer falls back to a generic page. Open the exact passage or reply before relying on any returned text. If all routes fail, `fetch.py` exits 2 and lists each reason.

## Crawl4AI

Run without a global install. Steps used:

```
uv venv /tmp/c4a --python 3.12
VIRTUAL_ENV=/tmp/c4a uv pip install crawl4ai            # version 0.9.5, venv is 640 MB
PLAYWRIGHT_BROWSERS_PATH=/tmp/c4a-pw /tmp/c4a/bin/playwright install chromium-headless-shell   # about 100 MB
```

Crawl4AI wanted Playwright's Chromium build 1255. A first attempt with `patchright install chromium` (build 1248) failed with "Executable doesn't exist", so the browser must come from `playwright install`.
It worked: 9 of 15 real, 3 stubs, 3 failures, median 1.6 s. It was the only fetcher besides Scrapling and StealthyFetcher to get Medium, and it returned the Discourse forum in 11 s. It returned the Reddit and YouTube pages as stubs, failed the PDF ("Unexpected error in _crawl_web") and was blocked by DataDome on g2.com.
Crawl4AI was not selected for the default chain in this run. The commands above use a temporary venv and browser directory. Not adopted as a default. It costs about 740 MB of disk and a second Python environment, and it did not beat Scrapling plus Jina plus StealthyFetcher on any page they all reached. It stays an option for a page that StealthyFetcher cannot render.

## Limits of this test

- n = 1 run per cell, one IP, one afternoon. Rate limits and bot scores move. Medium gave urllib a 200 in an earlier partial run and a 403 in this one.
- The token check proves the page text contains the expected words. It does not prove the extraction is complete.
- 15 pages sample the web. They do not rank fetchers in general.
- This run used `bakeoff.py` before a later edit that kills the whole browser process group on timeout. These timings predate the current deadline and process cleanup; current latency was not measured.
