---
name: social-search
description: Find what people are saying about a tool, model, paper, product or idea across Reddit, Hacker News, YouTube, Bluesky, Stack Overflow, Lobsters, dev.to, GitHub discussions, Product Hunt, blogs and X (sampled through web search). Use for "what are people saying about", "reddit", "twitter", "community opinion", "reviews of", "what do people use", "is X any good", "experiences with", "complaints about", "alternatives people recommend". Free tools only. Pairs with research. Not for facts the official docs or code settle.
---

> X: the FixTweet search API stopped answering in Nov 2026. `social.py x search` now falls back to a site:x.com web search plus per-post lookups: few posts, no like filter. Treat X as a thin sample and say so.

# Social search

Goal: a fair picture of what real users and experts report, with links you opened.
Community posts show what people report, not what is true. Use them to find failures, workarounds and sentiment. When called by `research`, return evidence rows and coverage gaps to it. When used alone, verify decisive technical claims against the owning artifact (docs, code, release notes).

Scripts: `S=~/.skills-library/skills/research/scripts`, shared with `research`. Commands, blind spots and route notes: `references/platforms.md`. WebFetch is blocked for Reddit, X and YouTube, so use the scripts. Copy the steps into your task list; a skipped step keeps its reason.

## Steps

1. **Brief.** One line each: the thing, the question ("is it any good", "what breaks", "what do people use instead"), the window (default last 12 months, 90 days for fast tools), how many options.
2. **Choose venues by who can answer.** For software or training behavior, search repository issues, discussions, Hugging Face discussions and Discourse forums before broad feeds. For alignment and interpretability, LessWrong and Alignment Forum posts and comments. Find niche subreddits with `reddit.py subs <prefix>` and by reading which communities the first hits link to. Seek first-hand reports and technical objections.
3. **Search for and against.** For every option run praise, failure and comparison queries: `"why I stopped using X"`, `"X problems"`, `"X vs"`, `"alternatives to X"`, `"X doesn't work"`. Use the product name, old name and repo name.
4. **Sample recent results without an engagement floor.** Default to date order; low and negative scores hold complaints. If popularity matters, run a separate ranked pass. Record each route's window, sort, pages read and stop reason (`window_reached`, `page_cap`, `error`). Search comments as well as titles (`reddit.py comments`, `hn.py search '<query>' --kind comment`, `social.py lesswrong --comments`, `youtube.py comments`).
5. **Go deep on what decides the answer.** For a decisive report, read the whole root post, the parent chain, the strongest contrary reply, any author update and the linked artifact. Then look for the same failure signature in another thread, venue or the owner's issue tracker. After the first readings, run a second pass with the exact error string, config flag, workaround name and the opposite outcome. Stop when new branches add no new mechanism, conflicting report or qualifier, or the stated cap is reached. Open the exact post, reply, issue comment, answer or timestamp and read its surrounding context. Record what the route returned and what it omitted. A transcript supports the speaker's statements. Claims about audience reaction need audience evidence.
6. **On failure, recover.** On 429, 422, a parser failure or missing replies, log the lost coverage. Narrow once if the service responds, then switch to indexed discovery plus direct item lookup, or another relevant venue. Attribute the substitute to its own venue. Qualify conclusions that depended on the unavailable sample. A failed fetch is not "nobody is talking about it". Exit code 3 or a PARTIAL marker means data with a failed part.
7. **Write up.** One paragraph with the finding and its coverage ("Opened 24 items across 11 threads. Six independently described the failure, two repeated the same run, three lacked detail."), then the incident rows below, then conflicts, nulls within stated queries, and what you could not reach. When called by `research`, return the rows to it.

## Parallel agents

Before any spawn, propose the count and split, then wait for explicit approval. Split by distinct communities or claim types. Launch each with `model: sonnet`. Deduplicate cross-posts and verify decisive items centrally.

## Evidence rules

- A search hit is a lead until you open the item.
- Quote the shortest decisive excerpt with its permalink (the reply's own link when the claim is about a reply) and date. Give a score only when selection or interpretation depends on it.
- Mark each item's read status: full, excerpt, deleted or unreachable. Never quote a deleted body or a search snippet as the post.
- Count distinct first-hand incidents separately from threads. Record version, hardware or workload when given, whether a maintainer reproduced it, and whether a fix shipped. Merge reposts and shared runs. Keep guesses, vendor claims and workarounds visibly separate.
- Upvotes are a proxy for agreement in one community that day. Separate hands-on reports from guesses and from vendor accounts.
- X coverage is thin. Never write "X users think". Write "the X posts I found (n=12) say".

## Incident rows

Count one incident per independently observed run or episode, not per thread or reply.

```
sample:   route | venue | query | from | to | sort | pages | opened | stop reason | gaps
incident: id | evidence links | first-hand? | date | version and setup | failure | repro by maintainer? | fix shipped? | independent of
```

Totals in the summary must recompute from the accepted incident rows. Every search command ends
with a `Coverage:` line (route, query, window, sort, pages, items, stop reason); copy those into the
sample rows instead of retyping them. A `stop` other than `complete` is a coverage gap to report.

## Output

Use the `research` output format and its evidence rules. Lead with what the opened sample supports and give a directional finding only within that described sample.
