# Output template

Save as `research/<topic>-<YYYY-MM-DD>.md`, or `docs/research/<topic>-<YYYY-MM-DD>.md` when the repo has
no `research/` folder. Two parts: a short read for the owner on top, the audit trail below a rule.
The owner reads the top part only, so it must stand alone. Plain short sentences. No em dashes.
Sentence-case headings. The `writing` skill's prose check runs on the top part.

```markdown
# <The question as a decision, in the owner's words>

Researched <date> · <depth> · <N> searches, <N> sources opened · window <12 months or other>

## Answer

<2 to 4 sentences. The recommendation or finding first, with its confidence (settled, likely,
contested, unknown) in plain words. One real number if it decides the answer.>

## Why

<3 to 6 short paragraphs or bullets, one per decisive point. Each: the claim, the number or quote
that carries it, the source linked inline, and how far it transfers to the owner's case. No tables
here unless 3+ options are compared on the same measured basis; then one small table.>

## What could change this

<1 to 3 bullets: the strongest evidence against, and the one check most likely to flip the answer,
with what it would take to run it.>

## Read next

<2 or 3 links, each with one line on what it adds.>

---

# Appendix: audit trail

The gates read this part. Keep every heading.

## Did we answer what was asked

One row per ask from the brief. Status words must be exactly match, mismatch, unknown or n/a.
The disposition is answered or unresolved.

| Ask (owner's words, with its id) | What was measured | Who or what | Compared with | Under the stated limits | Kind of evidence | Disposition |
|---|---|---|---|---|---|---|
| Q1: <ask> | match | match | match | match | match | answered |

## Ranking (only when the options were measured on comparable evidence)

| Rank | Option | Verdict | Why | Evidence | Last activity | Links |
|---:|---|---|---|---|---|---|

## Checked

- <claim> ([source](url), <date>): "<short quote>"

## Inferred

- <claim>. Reasoning: <steps>. Rests on: <register ids>.

## Unknown

- <question>. Looked in: <routes and queries>. Why it stays open: <reason>.

## Conflicts

- <conclusion, confidence, strongest contrary result, the differing condition, what survives both>

## Refute pass

| Claim (with its ask id) | How we tried to break it | What the opened source says | Verdict |
|---|---|---|---|

## Strongest case against

- <the strongest material objection, its evidence or the missing check, and what it changes>

## Null results

- <route, query, window, result>

## Coverage

<Routes that failed or were blocked, and what that coverage loss could change.>

## Method

Depth, rounds, searches run per route, sources opened (primary count), refute verdicts, and any pass
that did not run.

## Evidence register

| id | ask | claim | provenance group | URL and version | locator | source date | excerpt or value | evidence basis | fit and limits | stance |
|---|---|---|---|---|---|---|---|---|---|---|
```
