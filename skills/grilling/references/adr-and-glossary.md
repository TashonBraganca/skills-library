# ADR and glossary formats (with docs mode)

Location: use the repo's existing convention (`docs/adr/`, `docs/decisions/`, `decisions/`). If
none, create `docs/decisions/` and say so. Number files `NNNN-short-title.md`, continuing any
existing numbering. Write only what the owner confirmed. Do not invent a rationale.

## ADR (one per decision that is costly to reverse)

```
# NNNN. Title in plain words

Status: accepted | superseded by NNNN | proposed
Date: YYYY-MM-DD

## Decision
One or two sentences.

## Why
The reasons, including the evidence (links, numbers, files).

## Alternatives rejected
Each with the reason it lost. Include the boring path.

## Assumption this rests on
What must stay true. How we would notice it stopped being true.

## Accepted risks
Failure, trigger, cheapest check. Who accepted it.

## Reversal cost
What undoing this costs later.
```

Bar: write an ADR when the decision is expensive to reverse or keeps getting reopened, and the
context explains a real tradeoff. Otherwise it goes in the summary, not a file. Record the evidence,
the decision owner, the signal that should trigger a revisit, and a supersedes link. A threshold or
choice the owner has not approved is `proposed`, never `accepted`. Update the old ADR's status
instead of editing its history when a decision is replaced.

## Glossary (terms that turned out to mean two things)

Create or extend `GLOSSARY.md` next to the ADRs, unless the repo already has one.

```
**Term**: the meaning we use, in one or two sentences.
_Avoid_: the rejected synonym or other meaning, and where it showed up.
```

The glossary holds terms and nothing else: no implementation detail, no specs, no running log of
answers. Record the settled definition when the ambiguity would change implementation or
interpretation. If the code and the proposed meaning differ, resolve that before documenting it.
