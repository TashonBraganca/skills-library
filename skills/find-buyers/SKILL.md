---
name: find-buyers
description: Find where the buyers of a product or service already talk about the problem - which subreddits, forums, Discords, review sites, GitHub repos, newsletters and events - with counted, dated, linked evidence of pain, active search and willingness to pay, plus what each venue allows. Use for "where do my buyers hang out", "find buyer communities", "where are people asking for a tool like this", "where do people discuss <problem>", or as the first step of gtm. Not for generic complaint research (social-search) or account-level lead lists.
---

# Find buyers

Goal: a venue map built from evidence. For each place: who is there, how many distinct buyers
showed real intent recently, what they said in their own words, and what kind of participation the
venue permits. Generic channel advice ("post on Twitter, do SEO") is the failure this prevents.

When `gtm` calls this skill, write every file into `gtm/buyers/` (`buyers.jsonl`, `venues.jsonl`,
`scores.json`, the venue map) so its gate can read them.

Scripts: `R=~/.skills-library/skills/research/scripts`. Query templates and the scoring sheet:
`references/query-bank.md`. Copy the steps into your task list; a skipped step keeps its reason.
Free tools only. Observe public material. No private scraping, contact enrichment, automated
messages, fake accounts or disguised promotion.

## Steps

1. **Freeze the buyer.** Write the user, buyer and payer (often different in B2B), the job they need
   done, geography and language, the current workaround, and the trigger that makes them switch. If
   the owner cannot name the buyer, grill that first (`grilling`). Write the venues you expect to
   win before searching, so surprises are visible.
2. **Start from the job, not the product.** Search the buyer's words for the problem and the
   workaround before the product category. Build the phrase list from the first real posts, then
   run the active-search and switching templates (`references/query-bank.md`). Run the
   counter-evidence templates too ("we built our own", "not worth paying").
3. **Discover venues by four routes:** one role venue (where this job title talks), one workflow
   venue (where the task is discussed), one incumbent's support or review venue, one adjacent
   substitute. Follow the communities, newsletters and events the first hits link to.
   - Reddit: `python3 $R/reddit.py subs <prefix>`, `reddit.py top -s <sub> --since 90d --by date --pages 5`,
     `reddit.py comments "<pain phrase>" -s <sub> --since 90d --by date`, `reddit.py search "<phrase>" -s <subs>`.
   - Hacker News: `python3 $R/hn.py search '"<phrase>"' --kind comment --since 12m`.
   - Developers and technical buyers: `gh search issues "<phrase>" --repo <competitor repo>` (feature
     requests and complaints against incumbents), `social.py discourse <forum host> "<phrase>"`,
     `social.py hfdiscuss <repo>`, Stack Overflow (`social.py stackoverflow`).
   - App users: resolve the incumbent's app id in the buyer's storefront (`curl -s 'https://itunes.apple.com/search?term=<app>&entity=software&country=<cc>&limit=5'`),
     then `social.py appreviews <id> --country <cc> --max-rating 2 --pages 3`. Cite each review by its review id.
   - Video and social: `youtube.py search`, `youtube.py comments <id> --sort new`, `social.py x search`,
     `social.py bluesky`. Use them to learn vocabulary and find communities, then verify intent at the source.
   - Everything else (G2, Capterra, Trustpilot, Indie Hackers, Product Hunt, Quora, newsletters,
     meetups, Slack and Discord directories): `websearch.py 'site:<domain> "<phrase>"'` then `fetch.py`.
     A Discord or Slack invite page proves the community exists, not that buyers are active there.
4. **Read and code.** Open each candidate post. Record buyer role (or unknown), pain in their words,
   evidence of action, date, version or setup, and an intent rung (0 to 5, `references/query-bank.md`).
   Count an episode only when the opened post supports buyer role, intent and date; one buyer or
   organisation per episode; merge reposts; vendor posts never count. Quote the rung's evidence.
5. **Check each venue's rules.** Read the posting rules and pinned threads (Reddit:
   `python3 $R/reddit.py rules <sub1>,<sub2>`; elsewhere the forum's rules or FAQ page through `fetch.py`). Look at how
   promotional posts are received: removed, downvoted, welcomed in a weekly thread. The archive copy
   from `reddit.py rules` is a lead: before any test is planned, confirm the live rule (the venue's
   current rules page or a moderator statement) with its date. Without it, permission is unknown and
   the venue stays ineligible. One high-intent request justifies a reply where allowed. It does not
   prove a repeatable channel.
6. **Score from the ledger, not by eye.** Keep `buyers.jsonl` (one row per opened buyer post) and
   `venues.jsonl` (rules link, live check date, the rule excerpt, permission allowed/prohibited/unknown, allowed action, posts opened), formats in the script
   header, then run `python3 ~/.skills-library/skills/find-buyers/scripts/venue_score.py --ledger buyers.jsonl --venues venues.jsonl --json scores.json`.
   One ledger and scoring run per target segment (geography, language, role): tag rows with
   `segment` and pass `--segment`. One permalink is one buyer. `allowed_action` names the one
   active action the rule permits, or "" for a read-only venue. Uncertain-fit posts stay out of
   the count and are listed as leads.
   It merges duplicate buyers, ignores non-first-hand posts, and marks a venue eligible only with a
   live rule check, a named allowed action and real intent. Keep private or unverified venues as leads.
7. **Return the map.** One line on coverage, then the table below, then the buyer-language table,
   then gaps (private communities, unreachable sites, thin X coverage). For each venue that
   qualifies: the allowed action, the smallest observable success event, the denominator, and the
   stop threshold. Any outreach is the owner's call.

```
venue | rules link | segment | window | opened | distinct buyers | rung counts (1-5) | best links | score (fit/intent/recency/reach) | allowed test | gaps
```

## Rules

- Distinct buyers with dated first-hand posts, not upvotes or member counts. A trend needs dates.
- A venue with many members and no recent first-hand pain ranks below a small one with five.
- Say plainly when evidence is thin. An empty shortlist is a valid answer.
- Disclose the owner's affiliation wherever you suggest posting.
