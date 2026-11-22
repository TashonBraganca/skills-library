# Platform notes

Free tools only. Route notes were last checked on 2026-11-18 from the owner's Mac. Each entry says what worked, what did not, and how to tell when it breaks.

## X (Twitter)

X has no free official search. These routes exist, ranked by usefulness.

1. **FixTweet API search.** `python3 $S/social.py x search "term" --since 90d --feed latest`. Add `--min-faves` only for a separate ranked pass.
   Calls `https://api.fxtwitter.com/2/search`. Returned real, dated posts and honored X operators (`since:`, `min_faves:`, `from:`).
   Cross-check: post dates agree with the date encoded in each status id. It is a volunteer service and unofficial. It can disappear or throttle. It returns 20 posts per page.
   Its profile timeline route (`/2/profile/<user>/statuses`) returned truncated JSON, so use `--from user` search.
2. **One post.** `fetch.py https://x.com/user/status/ID` reads one X status and its quoted text. Use `social.py x post URL` for the returned author-thread sample. Replies from other users require separate evidence.
3. **Search engine with `site:x.com`.** `python3 $S/websearch.py "site:x.com \"sparse autoencoder\" criticism"`. Finds a small slice of posts. Dates come from the status id. Good as a second sample.
4. **Direct page fetch.** `x.com/...` returns an app shell or login wall. Do not count it as a read. `fetch.py` rejects walls.
5. **Bluesky.** Many ML researchers also post there: `social.py bluesky`. Use it as a second sample, not a substitute.

Say plainly in every report: X coverage is thin. The API samples posts, it does not count them. Replies and long threads are mostly missing. Loud accounts dominate. Never claim "X thinks".

## Reddit

Reddit blocks scripts: HTTP 403 for browser-like clients, a login page on old.reddit.com, and a hook blocks WebFetch. Try one short Arctic Shift title query or a known thread ID (`reddit.py`). On repeated failure, use search-engine domain discovery (`websearch.py "site:reddit.com ..."`) and retry known IDs if lookups respond. Record posts and comments separately as reached or unavailable. Move to another relevant venue when blocked.
Quirks: `title=` search works; `query=` full text times out. With `after=` and `sort=desc` some queries answer HTTP 422 "Timeout" for minutes; the script makes at most two bounded requests per term, then reports the failure. Posts lag live Reddit. Thread URL format: `https://www.reddit.com/r/<sub>/comments/<id>`.

## Hacker News

Algolia API, no key, fast. Quoted phrases need `advancedSyntax`, which `hn.py` sets. `search_by_date` sorts by newest. Comments carry the objections, so run `--kind comment` too.

## YouTube

Search reads the results page (`ytInitialData`). Transcripts and comments use yt-dlp (installed 2026-11-19). Otherwise they use the Android player endpoint, which returned manual and auto captions today. The old web caption URLs return empty bodies, so do not rewrite the script to use them. If the Android route breaks: `brew install yt-dlp`.
Auto captions have no punctuation and garble proper nouns.

## Bluesky

`https://api.bsky.app/xrpc/app.bsky.feed.searchPosts` answers. `public.api.bsky.app` returns HTTP 403 for search. Parameters: `q`, `sort` (top or latest), `since`, `lang`, `limit` up to 100.

## Stack Exchange

`https://api.stackexchange.com/2.3/search/advanced`, about 300 anonymous requests a day per IP (the script logs the remaining quota). Stack Overflow's newest `vllm` question was from November 2025 when checked, so new-tool questions are rare there.

## Lobsters

`lobste.rs/search` is behind an Anubis bot check. Tag, newest and hottest JSON feeds work (`/t/ai.json`, `/newest.json`, `/hottest.json`) and so does `/s/<id>.json` for comments.

## dev.to

`https://dev.to/api/articles?tag=...&top=30` works. The site search endpoint returned empty results, so `social.py devto` filters a tag.

## Product Hunt

`https://www.producthunt.com/feed` (Atom) lists the newest launches. There is no free search or review API. Use a `site:producthunt.com` web search and read the page with `fetch.py`.

## GitHub

Check `gh auth status` before relying on CLI search. Open the original repo issue, discussion, or release page through the harness when CLI access fails. Check bodies, replies, timestamps, and linked fixes. Discussions need `gh api graphql`. Issue search, code search and repo search work. Search limit: 30 calls a minute.

## Web search

`websearch.py` tries Brave and falls back to Yahoo. Brave returned 429 in the 2026-11-18 test. Yahoo returned hits but applies no server filter beyond 31 days. Verify dates on the opened sources. If a date-sensitive claim remains unresolved, switch to an independent discovery route. Google returns a JavaScript page, DuckDuckGo a bot check, and Mojeek and Ecosia block scripts.

## Platform map and commands

`S=~/.skills-library/skills/research/scripts`. Blind spots are what the tool cannot see. Record the effective cutoff and sample limits for each route you use.

| Platform | Command | Good for | Blind spots |
|---|---|---|---|
| GitHub issues | `gh search issues "text" --repo owner/name --label bug --json title,url,state,commentsCount` | Real defects, maintainer replies, linked fixes | Skews to problems. Counts include PRs. |
| GitHub Discussions | `gh api graphql -f query='query{search(query:"text", type:DISCUSSION, first:10){nodes{... on Discussion{title url createdAt upvoteCount repository{nameWithOwner}}}}}'` | Maintainer answers, user setups, feature debates | Only repos with Discussions on. Word match. |
| Release notes | `gh release list -R owner/name --limit 5`, then open the release page | What changed, known issues | Terse. Version matters. |
| Reddit | `python3 $S/reddit.py search "term" -s Sub1,Sub2 --since 6m --by date` then `reddit.py thread <id>` | Practitioner failure reports, "should I switch" threads | Title match only. Archive lags by hours to days. Slow, sometimes times out. Removed posts have no text. `thread` exits 3 when comments are partial. |
| Reddit discovery and browsing | `reddit.py subs <prefix>`; `reddit.py top -s Sub --since 90d --by date --pages 5` | Which communities exist; everything posted in a window | Prefix match only. `top` prints its stop reason; `page_cap` means raise `--pages`. |
| Reddit comments | `reddit.py comments "phrase" -s Sub --since 6m --by date --pages 4` | Failure reports and objections that titles miss | Pages of 25 (larger pages time out). Large subreddits often stop early with exit 3: say so. |
| LessWrong, Alignment Forum | `social.py lesswrong "term" --since 12m` (`--comments`, `--af`, `--by score`) | Alignment and interpretability write-ups, comment-level objections | Text search over posts or comments. Cross-posts from lab blogs appear as link posts: open the original. Karma is a proxy. |
| Discourse forums | `social.py discourse discuss.huggingface.co "term"` (also discuss.pytorch.org, community.openai.com, forum.cursor.com) | Maintainer answers, setup problems | Blurbs only: open the topic. Some hosts rate-limit or need login. |
| Hugging Face discussions | `social.py hfdiscuss owner/repo` (`--type datasets`, `--grep`) | Tokenizer, template and checkpoint regressions reported against a model card | First page of the API. A PR's diff and the published revision decide whether a fix landed. |
| App Store reviews | `social.py appreviews <app id> --country us --max-rating 2 --pages 3` (the buyer's storefront) | What users of an incumbent app complain about | Self-selected sample. Newest first, about 50 per page, up to 10 pages. |
| YouTube comments | `youtube.py comments <id> --sort new --limit 100` | Audience reaction, counterexamples to a talk or demo | Needs yt-dlp (installed). A video's comments are one selected audience. |
| X | `python3 $S/social.py x search "term" --since 90d --feed latest` | Researcher announcements, quick reactions | Unofficial FixTweet API. 20 posts per page. Opaque ranking. Rows carry `coverage_partial`. |
| Hacker News | `python3 $S/hn.py search '"phrase"' --since 12m` (add `--page N`, `--kind comment`) then `hn.py thread <id>` | Developer reaction, expert comments | US software skew. Quote phrases. Low-point posts hold good comments. |
| YouTube | `python3 $S/youtube.py search "term" --since 12m` then `youtube.py transcript <id>` | Demos, talks, long reviews | Auto captions garble names and numbers. Upload filter is a coarse bucket. A transcript supports the speaker's statements only. |
| Bluesky | `python3 $S/social.py bluesky "term" --since 90d --sort latest` | Researchers who left X, short takes | Small audience. Text match only. |
| Stack Overflow | `python3 $S/social.py stackoverflow "term" --since "" --sort votes` | Reproducible errors and fixes | Volume has collapsed. Answers go stale. Other sites: `--site ai.stackexchange.com`. |
| Lobsters | `python3 $S/social.py lobsters --tag ai --pages 3 --grep "regex"` | Small, moderated programmer discussion | No free search. Filters tag feeds, so recent items only. |
| dev.to | `python3 $S/social.py devto --tag llm --top 30 --grep "regex"` | Tutorials, hands-on write-ups | Tag-and-filter only. Many SEO or AI-written posts. |
| Product Hunt | `python3 $S/websearch.py "site:producthunt.com TERM"` | Launch-day buzz | Marketing. No review API. |
| Blogs, Substack, Medium | `python3 $S/websearch.py "\"why I switched from\" X" --since 12m` then `python3 $S/fetch.py <url>` | Reasoned experience reports, post-mortems | Stale and SEO results. Check the page date. |
| Any page | `python3 $S/fetch.py <url>` | One page as clean text | Bot-protected sites may stay blocked. A failed X, Reddit or YouTube route does not fall back to a generic page (`--no-route` forces it). |

Search by community: ML research (X, Bluesky, LessWrong and Alignment Forum, r/MachineLearning, HN, YouTube). Developer tools (repo issues and discussions first, then tool subreddits, HN, Lobsters, blogs). Products (Reddit, YouTube, blogs, Product Hunt).

## Query habits

- Run each option through praise, failure and comparison queries (`research/references/query-plan.md`).
- Use names and synonyms: the product name, its old name, its repo name, common misspellings.
- Subreddits: one general, one tool-specific, one skeptical. List them in the brief.
- Run a recent-first pass without an engagement floor. If popularity matters, run a separate ranked pass.
- If the latest hit predates the release in question, run one query on the release name, error text or version on the most relevant route. If that fails, log the version and the coverage gap. Keep replacement venues distinct.
