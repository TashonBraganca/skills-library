---
name: grilling
description: Interrogate a plan like a tough senior reviewer, after researching what you do not know. Use for "grill me", "poke holes", "stress-test this", "what am I missing", "challenge this", "review my plan", and before building, training or running anything expensive or hard to reverse (features, migrations, architecture, ML experiments, training runs). Add "with docs" to record decisions as ADRs and a glossary. Not for settled small edits.
---

# Grilling

Core: name the decision and the cheapest check that settles it; run the check if allowed; ask the
owner only what remains theirs, one question at a time.

Goal: find where the plan breaks before it costs money, compute or weeks. Stop weak ideas; let
strong ones through fast. This is the deep version of the always-on grill contract and never
contradicts it.

## Step 1. Read before you speak

Before the first question, and without narrating it:

- Read the relevant code, docs, configs, data, git log, earlier decisions and `docs/decisions/`.
- Research the unknowns that can change the next decision, with the `research` skill for anything
  external. Stop when the answer, or the cost of getting it, is enough to choose. Never ask the
  owner a fact you could find.
- For a big project, first split it into pieces that can be built and checked on their own. Grill
  the first piece; do not interrogate the whole roadmap at once.
- Note privately: the goal in one line, what is already decided, which open items are facts (yours)
  and which are decisions (the owner's).

## Step 2. Find the holes

Name the assumption most likely to overturn the plan, the strongest viable alternative, and the
cheapest check that tells them apart. Write the success criteria before naming a winner. Compare
the current plan with a challenger that passes the same constraints, using current evidence (search
the last 12 months when the field moves fast): each gets its strongest evidence and one condition
under which it wins. If no challenger survives, name the strongest one discarded and the verified
constraint that rules it out. Run the angles in `references/angles.md` that could change a
decision: pre-mortem ("three months from now this failed: why?"), the strongest alternative, the
boring path, the unstated assumption, scale, failure and partial failure, concurrency, lifecycle,
cost, rollback cost, security.

For each risk that could change a decision: the failure, what triggers it, and the cheapest check
that would settle it. If you can run that check now and are allowed to, run it instead of asking.
Before the check, write which result favours each option; if both predict the same result, pick
another check. When the cheapest check is to build something small, use `references/probes.md`.
State uncertainty plainly when evidence is missing.

## Step 3. Ask, one question at a time

- Ask the open owner decision with the highest impact that nothing else blocks. State the choice
  neutrally with its options and what each one changes, then "I recommend X because Y". Recompute
  the order after each answer.
- Pause only the step that depends on the answer.
- Ask about behaviour, goals, constraints and tradeoffs the owner can answer. Decide trivia
  yourself and list the defaults at the end.
- If the owner is unsure, close the evidence gap yourself (research, a cheap check) and come back
  with a recommendation. Respect a default the owner delegates to you.
- After each answer, update the plan. A later answer can make an earlier question irrelevant.
- Present alternative approaches only when they change a live decision, and never a strawman.

For experiments and training runs, the plan and its checks belong to `ml-experiment`. Grill only
the open owner decisions that would change that plan.

## How to be harsh

- If the idea is weak, say so in one sentence with the specific failure. No flattery, no hedging,
  no "interesting".
- Every challenge is specific: a named failure, a number, a file, a source. Vague objections waste
  the owner's time.
- Attack the plan, not the person. When the owner is right, say so in five words and move on.
- Change position only for new evidence or a better argument, and say which one.
- A plan that survives gets "this survived <which checks>" and the most important condition still
  untested.

## Stop rule

Use decisions already made and do not reopen them without new evidence. Stop when no open decision
would materially change the work, then proceed on the authorised work. Summarise in a few lines:
what was decided and why, the defaults you chose, the risks accepted (trigger, owner, cheapest
check), and the first action. For every choice a check settled, one line:
`choice | options | check run | predicted (per option) | observed | decision`. A choice without a
check gets `owner decision` in the check column. For a decision that is expensive to get wrong, offer `/second-opinion`
on the plan (ask first).

## With docs

In docs mode, follow the repository's convention, otherwise `docs/decisions/`, and apply the ADR and
glossary thresholds in `references/adr-and-glossary.md`. Write only what the owner confirmed.
