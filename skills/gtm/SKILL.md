---
name: gtm
description: Find the first customers and the channels that actually work for a specific product, and run the content and outreach that follow. Always runs the research skill (market, competitors, what got their first users) and the find-buyers skill (where buyers already talk, counted and linked) before any plan, then picks up to three evidence-backed channel bets with stop rules, and runs a founder-led content engine (posts, case studies, lead magnets, briefs) when content is a chosen channel. Use for "how do I get users/customers", "where should I market this", "go-to-market", "GTM", "launch plan", "find clients", "who would buy this", "marketing for my project", "content strategy", "LinkedIn content", "lead magnets", "B2B content engine". Needs a defined product; not for general marketing advice.
---

# Go to market

Generic advice ("post on Twitter, do SEO") is the failure. Every channel needs dated, linked
evidence that the buyers are there, talking about the problem now, and that the venue allows what
you plan to do. **No plan exists until `research` and `find-buyers` have run and the gate passes.**

Work in `gtm/` in the project (`company/`, `research/`, `buyers/`, `strategy/`, `content/`).
Execution skills come from the project's `market` pack; if one is missing, offer
`python3 ~/.skills-library/packs/install_pack.py add market --project .` (ask first) and continue
with what is available. In Claude Code invoke a skill with the Skill tool; in Codex read its
SKILL.md. Free tools only unless the owner says otherwise. `C=~/.skills-library/skills/gtm/scripts/gtm_check.py`.
Copy the steps into your task list; a skipped step keeps its reason.

## 1. Intake (at most six questions, once)

Read the repo, site and docs first. Then ask only what is still missing, in one round:

1. What do you sell, and at what price?
2. Who is the buyer (user, buyer and payer can differ), and who is it not for?
3. Which expensive problems does it solve, in the buyer's words?
4. Which customer results can we use, and which are confidential?
5. Which founders, creators and competitors should we track?
6. Which claims or names must we never mention?

Write `gtm/company/brief.md` with one line per field: `Sells:`, `Buyer:`, `Problems:`,
`Usable results:`, `Track:`, `Never mention:`. An unanswered item is written as "unavailable",
never guessed. If the
owner cannot name the buyer, run `grilling` on that first. Use `product-marketing` if installed.

## 2. Research the market (mandatory)

Invoke the `research` skill (its brief saved as `gtm/research/brief.md` with `Q1:`, `Q2:` asks) with a brief that asks: the 3 to 5 closest competitors and substitutes;
how each got its first 100 users (launch posts, directories, integrations, communities, content
that still ranks); their pricing and positioning; recent launches, funding and platform changes
that move the buyer; and the strongest evidence against the product's premise. Save the report in
`gtm/research/`. `competitor-profiling` and `reverse-engineer-marketing` from the pack feed it. A
channel that worked in 2023 or for a funded team may not transfer: say so per channel.

## 3. Find where buyers talk (mandatory)

Invoke the `find-buyers` skill with the brief. It writes `gtm/buyers/buyers.jsonl`,
`gtm/buyers/venues.jsonl` and `gtm/buyers/scores.json` (`venue_score.py ... --json`), plus the
buyer-language table. This step decides which channels are even eligible.

## 4. Gate

`python3 $C inputs --brief gtm/company/brief.md --report gtm/research/<report>.md --report-brief gtm/research/brief.md --scores gtm/buyers/scores.json`.
It runs the research report checker too. Exit 1 names what is missing: run that skill, then re-run
the gate. Never write channel bets while it fails.

## 5. Pick up to three channel bets

Only venues that `scores.json` marks `channel test` qualify (three distinct qualifying buyers and a
live rule receipt). A venue marked `reply only` justifies one disclosed reply, not a channel. A
non-obvious channel (a competitor's GitHub issues, an integration marketplace) qualifies only with
equally strong evidence. For each bet, a two-week experiment in `gtm/strategy/plan.md`:

```
| venue | exact action | success event | sample size | stop rule | buyer links |
```

The exact action must be one the venue's rule allows; the stop rule holds a number ("stop if fewer
than 2 replies from 40 disclosed answers"). Then `python3 $C plan --plan gtm/strategy/plan.md --scores gtm/buyers/scores.json`.
Fix every FAIL. A STRUCTURE PASS is not approval: read each CONFIRM line against the venue's rule
text and say you did. The buyer links must be the qualifying buyers' own posts from `scores.json`. An empty
shortlist is a valid answer: say what evidence is missing and how to get it.

## 6. Execute

With the matching pack skill: `community-marketing`, `launch`, `directory-submissions`,
`cold-email` (only to people who asked or opted in), `seo-audit`, `ai-seo`; `copywriting` built from
the buyers' own phrases; `pricing` or `offers` if the offer is unclear. `prospecting` only when the
owner asks for account-level lead lists. Every piece of copy goes through the `writing` skill.

When content is a chosen channel or the owner asks for content, run the content engine. If the
owner already chose the channel (say LinkedIn) and supplied customer evidence, skip channel
discovery: reuse current evidence, verify claims and platform rules, and label untested
distribution assumptions. Content engine:
`references/content-engine.md` (idea bank, evidence library, case studies, lead magnets, daily
brief and weekly review). Its five roles are passes you run yourself. Any subagent or scheduled run
needs the owner's yes first.

## 7. Measure

Track each experiment's success event against its denominator, and keep impressions and
engagement apart from qualified leads, meetings, opportunities and revenue. Stop or double down by
the pre-set rule, never by feel. Log every result, including flops, in `gtm/strategy/results.md`.

## 8. Report

Answer first: the three bets (or why none qualify), each with its receipt and stop rule. Then the
venue map, the buyer-language table, what competitors did, what you could not reach, and a **Why
this could fail** section with the strongest evidence against the plan. Use the `research` output
rules for citations.

## Rules

- Count distinct buyers with dated first-hand posts, not upvotes or follower counts.
- Disclose the owner's affiliation wherever you suggest posting. No fake accounts, astroturfing,
  automated DMs or engagement pods. Never scrape LinkedIn or private communities.
- You contact nobody, publish nothing and buy nothing. The owner acts.
- Say plainly when the evidence for a channel is thin.

## Done when

`gtm_check.py inputs` passes and `gtm_check.py plan` gives a STRUCTURE PASS (or the report says why no bet qualifies, or the owner chose the channel and the content route ran),
every CONFIRM line was checked against the rule text, and the report has its Why-this-could-fail
section.
