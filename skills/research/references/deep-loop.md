# The deep research loop

Deep research is a loop with a stopping rule, and the draft is a hypothesis to attack, not an answer
to trust. One search-and-summarise pass is the failure this prevents.

Sources for the design: Anthropic's "How we built our multi-agent research system" (2025-06-13,
https://www.anthropic.com/engineering/multi-agent-research-system): effort scaled to the question
(1 agent and 3 to 10 tool calls for a simple fact, 2 to 4 workers with 10 to 15 calls each for a
comparison), "start with short, broad queries, evaluate what's available, then progressively narrow
focus", a separate citation step, and token usage alone explaining 80% of performance variance on
BrowseComp, which is why deep work gets a bigger budget; STORM (questions asked from several
perspectives), and open deep-research agents that run a knowledge-gap loop, a devil's-advocate pass
fed back as new gaps, and a per-claim refute-or-survive check (github.com/ai-foundry-byu/deep-research-agent,
read 2026-11-19). Another pass can also make an answer worse: in DeepVerifier v2 (arXiv 2601.15808,
Tables 3 to 5), Claude 3.7 Sonnet on XBench-DeepSearch went 41.0% before feedback, 47.0% at two
rounds, 44.0% at ten; on GAIA-Full 52.22%, 60.12% at four rounds, 58.93% at ten. Revise toward a
gap, and stop when a pass adds nothing material.

## Depth

Depth, round plan and stop rule: SKILL.md section 0. Never add filler searches to hit a number.

## Perspectives (before round 1, deep)

List 3 to 5 people who would ask different questions about this topic: a practitioner who must ship
it, a skeptic or competitor, the researcher who built it, the buyer or user, a regulator or
security reviewer. Write 2 or 3 questions each. They seed the gap list, so the search does not only
follow your first framing.

## Each round

Write a block into `research/<topic>/log.md`:

```
## Round N  (<date>)
Queries run: <route: query, window>  ...
Opened: <count> (primary <count>)
Register rows added: <register ids, or none (reason)>
Learned: <one line per finding, with register ids>
Gaps, ranked by how much they could change the answer:
  1. <gap>  -> next query/route
  2. ...
New terms and aliases: <...>
Decision: continue | stop (<why>)
```

Pick the next round's queries from the top gaps only. Stop when two rounds in a row add nothing that
could change the answer, every decisive ask is closed, or the timebox ends. Failed routes do not
count as "nothing new".

## Refute pass (every decisive claim)

For each claim the answer rests on, run one fresh search built to break it, on a different route
from the one that found it ("<claim> fails", "<method> does not replicate", issues, critiques,
negative results, a newer benchmark). Open what you find. Record:

```
| claim (with its ask id) | how we tried to refute it | result | verdict |
| Q1: <claim> | <route and query> | <what the opened source says, with link> | survives / weakened / refuted / unverified |
```

`unverified` means no opened source supports the claim; it leaves the answer or becomes an open
question. A `weakened` claim keeps its new scope in the answer.

## Strongest case against (after the draft)

Write the strongest material objection to your answer, as its smartest critic would, with its
evidence or the missing check, and say what it changes. If no counterevidence surfaced, give the
route, query, window and coverage. A point that could change the answer becomes a gap for one more
round (one extra round at most). Keep the section in the report.

## Parallel lanes

Run lanes yourself in sequence by default. Subagents follow SKILL.md section 2 (ask first).

## In the report

The Method section states: `Depth:`, `Rounds:`, queries run, sources opened (primary), refute
verdict counts, and the passes that did not run. `report_check.py --depth deep` checks it.
