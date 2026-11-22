# Source map

Which source owns which claim, how to query it, and where it is blind.
`S=~/.skills-library/skills/research/scripts`.

## Which command for which claim

| Claim type | Source | Command |
|---|---|---|
| Lab release, report, model card | Owner pages | `websearch.py 'site:<owner> "name"'` then `fetch.py` (see Owner route below) |
| What a paper says, and whether it holds | arXiv, Semantic Scholar, OpenAlex | `papers.py search "q" --since 12m --code` then `papers.py fulltext <id>` |
| A known paper by title or id | Semantic Scholar, arXiv, OpenAlex | `papers.py lookup "<title or id>"` (no date window) |
| Who built on or tested a paper | Semantic Scholar graph | `papers.py cites <id> --grep "..."`, `papers.py refs <id>`, `papers.py similar <id>` |
| Reviewer objections | OpenReview | `papers.py reviews "<title>"`, then `fetch.py <forum url>` |
| New papers getting attention | Hugging Face papers | `papers.py hf "q"`, `papers.py hf --daily` |
| A researcher's latest work | Semantic Scholar authors | `papers.py author "<name>" --since 90d` |
| Alignment and interp write-ups, objections | LessWrong, Alignment Forum | `social.py lesswrong "q" --since 12m` (`--comments`, `--af`) |
| Maintainer answers on forums | Discourse (HF, PyTorch, OpenAI, Cursor) | `social.py discourse <host> "q"` |
| Model or dataset regressions | Hugging Face discussions | `social.py hfdiscuss <owner/repo>` |
| Links on an owner page (report, card, code) | The page | `fetch.py <url> --links 'arxiv|github|huggingface'` |
| Models, datasets, Spaces on the Hub; files in a repo | Hugging Face MCP (read-only, installed) | `hub_repo_search`, `hub_repo_details`, `hf_fs` tools |
| How a public repo's code works | DeepWiki MCP (installed) | `ask_wiki_question`, `read_wiki_structure`; its wiki can lag releases, so confirm against the tagged source |
| Software behavior, bugs, maintenance | GitHub | `gh search ...`, `gh api` (see GitHub) |
| What practitioners hit | Reddit | `reddit.py search "q" -s Sub1,Sub2 --since 6m --by date` |
| Developer reaction | Hacker News | `hn.py search '"phrase"' --since 12m` |
| Expert takes | X | `social.py x search "q" --since 90d --feed latest` |
| Talks, walkthroughs | YouTube | `youtube.py search "q"` then `youtube.py transcript <id>`; audience reaction: `youtube.py comments <id>` |
| Official behavior, limits, versions | Docs, changelogs | `fetch.py <url>` |
| Opinion with reasoning | Blogs | `websearch.py "q"` then `fetch.py` |
| Reproducible errors | Stack Overflow | `social.py stackoverflow "q"` |
| Versions, dates | PyPI, npm | `curl -s https://pypi.org/pypi/<pkg>/json` |

Do not use WebFetch on Reddit, X or YouTube (a hook blocks it). WebSearch is fine for discovery only.
`fetch.py` tries Scrapling, Jina Reader, a headless browser, then plain HTTP, and rejects block pages. `--chain firecrawl` uses Firecrawl Local (installed, cloud off): fastest on static pages and PDFs, but in the 2026-11-19 bake-off (15 pages) it recovered nothing the default chain missed and passed one fake YouTube page, so it is opt-in only. A failed X, Reddit or YouTube route stops there. A failed fetch is not a null result.

## Papers

Owns: what a paper claims, method, results, citations, code links.

```
python3 $S/papers.py search "sparse autoencoders" --since 12m --limit 15 --code
python3 $S/papers.py search "reward hacking" --since 2026-01-01 --sort citations --abstract-chars 200
python3 $S/papers.py fulltext 2310.01405                      # section table
python3 $S/papers.py fulltext 2310.01405 --section method --max-chars 6000
```

- Searches arXiv, Semantic Scholar and OpenAlex in parallel, merges by arXiv id, DOI, then title.
- Semantic Scholar relevance search may throttle. The current bulk fallback is date-ranked with no relevance rank, so run independent discovery (arXiv and OpenAlex date passes, owner pages) and inspect recent results per index before merging. Read stderr alongside the JSONL.
- Citation counts lag. A paper from last month shows 0 to 5. Do not rank new work by citations.
- `--code` asks Hugging Face papers for a GitHub repo. A missing link means "not linked there", not "no code".
- arXiv `fulltext` tries HTML (the exact version you give, such as `2310.01405v3`), then local `pdftotext` if available, then Jina on the PDF. For other hosts, open the owner's HTML or PDF directly. Inspect the original page for decisive plots, footnotes, or table cells. Equations come out as LaTeX alt text.
- Not covered: lab releases and papers outside arXiv. Search OpenReview, ACL Anthology, or the publisher proceedings directly. For lab and industry releases, use the owner route below.

### Owner route: lab and industry releases

`papers.py` indexes arXiv, Semantic Scholar and OpenAlex. It will not surface a lab announcement, a technical report hosted as a PDF, or a model card. Search the project name and its aliases on the owner's own pages, then open the linked report, card, code and checkpoints. Example: `Gemma Scope 2` is found from the words alone with `websearch.py 'site:deepmind.google "Gemma Scope 2"'`. The announcement links the technical report and the Hugging Face card.

Site-restricted discovery (put `site:` in the query, in quotes around the project name):

| Site | Finds |
|---|---|
| deepmind.google | Google DeepMind announcements and blog posts |
| anthropic.com | Anthropic research posts, system cards, policies |
| openai.com | OpenAI research, system cards, release notes |
| transformer-circuits.pub | Anthropic interpretability papers and updates |
| alignmentforum.org, lesswrong.com | Alignment and interpretability write-ups, comment-level objections |
| huggingface.co | Model, dataset and paper cards, org pages |
| github.com | Repos, issues, discussions, releases |
| openreview.net | Conference submissions and reviews |
| aclanthology.org | ACL-family papers |

```
python3 $S/websearch.py 'site:deepmind.google "Gemma Scope 2"' --format jsonl
python3 $S/fetch.py https://deepmind.google/blog/<slug>/        # then follow report and card links
```

`fetch.py` page text drops link targets. List them with `fetch.py <announcement-url> --links 'huggingface|storage.googleapis|github|arxiv|neuronpedia'`. JavaScript-rendered pages return no links (exit 2): open those in a browser.

For a benchmark, search its name with "leaderboard" and open the owner's methodology, version and submission rules. Record the effective date window, because `websearch.py` rounds `--since` to coarse buckets.
- Workshop and preprint status is not shown. Check the venue field and the paper's own header.

## GitHub

Owns: real behavior, bugs, maintenance, who uses it, what the authors intend. An issue owns the report only: read the maintainer diagnosis and linked patch, then check the first release containing the fix against the version in question. A closed issue alone is not a shipped fix.

Check `gh auth status` first. Core commands (`gh` must be logged in):

```
gh search repos "topic words" --updated ">2026-05-01" --sort stars --limit 10 --json fullName,stargazersCount,pushedAt,description
gh search issues "error text" --repo owner/name --created ">2026-01-01" --json title,url,state,commentsCount
gh search issues "doesn't work" --label bug --sort reactions --limit 10 --json title,url,repository,state
gh search code "SymbolName" --language python --limit 10 --json repository,path,url
gh api repos/owner/name --jq '{stars:.stargazers_count,pushed:.pushed_at,open_issues:.open_issues_count,archived:.archived,license:.license.spdx_id}'
gh release list -R owner/name --limit 5
gh api graphql -f query='query{search(query:"text", type:DISCUSSION, first:10){nodes{... on Discussion{title url createdAt upvoteCount repository{nameWithOwner}}}}}'
```

Stars measure popularity. Check `pushed`, open issues, last release, and who maintains it. Search issue bodies, maintainer discussions, versioned docs and release notes, not only community venues. Extra:

```
gh api repos/OWNER/REPO/contributors --jq '.[0:5][] | "\(.login) \(.contributions)"'
gh api "repos/OWNER/REPO/commits?per_page=5" --jq '.[] | "\(.commit.author.date[:10]) \(.commit.message|split("\n")[0])"'
gh search issues "keyword" --repo OWNER/REPO --state open --sort comments --limit 10 --json title,url,commentsCount
gh api repos/OWNER/REPO/readme --jq .content | base64 -d
```

- Blind spots: issue counts include pull requests. Stars include bots and hype. A quiet repo may be stable or dead: check the last release and the last commit.
- `gh search repos` needs words that all appear. Use fewer words. Add `--updated ">DATE"` to cut dead repos.
- Use the active API response for throttling decisions.

## Reddit

Owns: failure reports from real use, "why I switched", tool sentiment among practitioners.

```
python3 $S/reddit.py search "superpowers" -s ClaudeAI,ClaudeCode --since 6m --by date
python3 $S/reddit.py search '"claude code"|cursor' -s ClaudeAI --since 30d --by date
python3 $S/reddit.py thread 1w0irg8 --limit 15
```

- Uses the Arctic Shift archive. Reddit itself blocks scripts and WebFetch is blocked by a hook.
- Title match only by default. A post that mentions the tool only in the body is missed. `--fulltext` tries body search but often times out.
- The server returns HTTP 422 "Timeout" on busy queries. The script retries other variants and waits 6 to 8 seconds between calls. A 4-subreddit search takes about a minute. If a call still fails, the output says "Incomplete".
- Probe one short term in one subreddit. On repeated timeout or a rate limit, stop the batch. Use indexed Reddit discovery (`websearch.py "site:reddit.com ..."`) and thread ID lookups if those respond, then search the relevant repository, HN, or forum for the underlying practitioner question. Report the missing Reddit coverage.
- A thread read exits 3 and prints PARTIAL when comments failed to load. A partial thread is not the full thread.
- The archive lags live Reddit by hours to days. Very new threads may be missing.
- Subreddit lists matter. Pick the 3 to 5 that hold the topic. Include a general one and a skeptical one.

## Hacker News

Owns: developer reaction to launches, papers and tools; long expert comments.

```
python3 $S/hn.py search '"mechanistic interpretability"' --since 12m --min-points 20
python3 $S/hn.py search "uv poetry" --kind comment --since 6m
python3 $S/hn.py thread 48883090 --limit 20
```

- Quote exact phrases: unquoted words match anywhere, so "reward hacking" matches unrelated posts.
- Many good posts have 0 to 5 points. `--min-points` hides them. Run once without it.
- Skews to US software people. Thin for medicine, law, non-English communities.

## X

Owns: researcher announcements, quick reactions, who is arguing with whom.
Coverage with free tools is partial. Details in the `social-search` skill.

```
python3 $S/social.py x search "sparse autoencoder" --since 90d --feed latest
python3 $S/social.py x search "interpretability" --from neelnanda5 --since 12m --feed latest
python3 $S/fetch.py https://x.com/user/status/123           # one post, counts and date, through fxtwitter
python3 $S/websearch.py "site:x.com \"sparse autoencoder\" criticism" --limit 10   # second sample
```

- `social.py x` searches X through a `site:x.com` web search, then reads each post through the free, unofficial FixTweet API (its own search endpoint is dead). The web fallback ignores `min_faves:` and samples far fewer posts than X search would: report it as a narrow sample.
- Search engines index a small slice of posts. Threads and replies are mostly missing. Post dates are decoded from the status id, so they are exact.
- Treat what you find as a sample of loud accounts, never as a measure of opinion.

## YouTube

Owns: talks, tutorials, conference sessions, demos.

```
python3 $S/youtube.py search "mechanistic interpretability" --since 12m --limit 8
python3 $S/youtube.py transcript VIDEO_ID --timestamps --max-chars 15000
```

- Auto captions drop punctuation and garble names, numbers and code. Check any figure elsewhere.
- Search ranking is YouTube's. The upload filter has four steps (day, week, month, year).
- Without yt-dlp the script uses an unofficial endpoint. It works today. If it breaks, `brew install yt-dlp`.

## Docs, changelogs, release notes

Owns: what the software is supposed to do and what changed.

```
python3 $S/fetch.py https://docs.example.com/page --max-chars 15000
curl -s https://pypi.org/pypi/PACKAGE/json | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['info']['version']; print(v, d['releases'][v][0]['upload_time'][:10])"
curl -s https://registry.npmjs.org/PACKAGE | python3 -c "import json,sys; d=json.load(sys.stdin); t=d['dist-tags']['latest']; print(t, d['time'][t][:10])"
```

- Docs describe intent. Issues describe behavior. Check both.
- Docs pages carry a version. Match it to the version you are researching.

## Blogs, Substack, Medium, news

Owns: reasoning, post-mortems, long comparisons, reporting.

```
python3 $S/websearch.py "\"why I switched from\" X" --since 12m
python3 $S/fetch.py https://author.substack.com/p/slug --max-chars 12000
```

- Medium and some news sites block scripts. `fetch.py` falls through to Jina Reader.
- Check the post date on the page. Search engines show stale dates.
- Vendor blogs are marketing. Treat their benchmarks as claims to check.

## Q&A and other communities

```
python3 $S/social.py stackoverflow "pytorch forward hook" --since "" --sort votes
python3 $S/social.py bluesky "interpretability" --since 90d
python3 $S/social.py lobsters --tag ai --pages 3 --grep "agent|claude"
python3 $S/social.py devto --tag llm --top 30 --grep "eval"
```

- Stack Overflow volume has collapsed. For fast-moving tools the newest question may be a year old. Use `--since ""` for old fixes and check the answer's date and version.
- Lobsters has no free search. The script filters tag feeds, so it only sees recent items.

## Web search

`python3 $S/websearch.py "query" --since 12m` uses Brave, then Yahoo. Brave uses coarse freshness buckets. Yahoo applies no upstream date filter beyond 31 days. When Brave degrades, search the owner's dated index or another engine, then verify publication dates on opened pages. Record the effective window. The script exits 2 when nothing survives the date filter. Use it for discovery. WebSearch built into the harness also works for discovery. Either way, results are leads.


## Reviewer objections and known titles

- For conference papers, `papers.py reviews "<title>"` then read the forum with `fetch.py`. Withdrawn
  and rejected submissions keep their reviews. Check whether the current version fixed each
  objection before repeating it.
- `papers.py lookup "<exact title or arXiv id>"` finds a known paper and ignores the date window.
