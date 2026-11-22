---
name: wayfinder
description: Keep one compact map of a long or multi-session project (destination, settled decisions with evidence, open decisions in dependency order, next unblocked action) so a fresh session resumes without the transcript. Use without being asked in long sessions and deep multi-step work, and for "wayfinder", "where are we", "where were we", "pick this back up", "continue", "what's next", "next steps", "how are things looking", "what's done", "map this project".
---

# Wayfinder

Keep one compact map that lets a fresh session resume the work without loading the full transcript. The map
records the destination, settled decisions, live unknowns, evidence pointers, and the next useful action. It
does not duplicate the evidence or become a diary.

Use the repository's issue tracker first when one already owns project planning; the map then links issues instead of copying them. Otherwise use a Markdown file in
the project's established planning directory, or `docs/wayfinder/<name>.md` when none exists.

## Map

```markdown
# <destination>

## Done means
<observable result and its acceptance evidence>

## Constraints
<only constraints that change decisions>

## Decisions
- <decision>: <reason> ([evidence](pointer))

## Open decisions
- [ ] <question> | blocked by: <name or none> | evidence: <pointers or missing>

## Next
<one executable action with its input and success check, or `Blocked: <dependency>, owner <who>`>
```

Keep evidence in its owning file, issue, commit, experiment, or research note. Link it from the map. Do not
paste transcripts, tool output, or full research reports into the map.

## Never invent

The map holds only what the sources say: notes, files, commits, results and the owner's words.
- Every decision, constraint and open question cites where it came from. No source, no entry.
- Keep the recorded next step as written. Change it only when newer evidence does, and cite that evidence.
- Your own ideas go under `## Proposed (not yet agreed)`, labelled as yours, never under Decisions, Open
  decisions or Next.
- Keep the numbers and dates exactly as the source states them.

Origin: in the 2026-11-19 paired test the skill added an "intended use" decision the notes never had and
replaced the recorded next step ("run 3 seeds") with "draft a protocol". The plain run did better.

## Start or resume

Name the destination and its observable finish. Read what already exists. Separate facts to research from
choices that need the user. Record only decisions that affect the route. Put unresolved choices in dependency
order, then choose the first unblocked one.

For each decision, use the skill that fits the uncertainty: `research` for external facts, and `grilling` for a
choice that needs pressure testing or a goal that is still unclear. Work independent
research questions together when that saves time without mixing their evidence.

After resolving a decision, replace its open entry with one decision line and an evidence pointer. Record the
choice and reason, not the source report's argument. Recompute the first unblocked action. If new facts change
an earlier decision, amend that line and retain the pointer to the evidence that caused the change.
Recommendations, proposed thresholds, and model preferences remain open decisions until their owner approves
them. Research can inform a choice; it cannot silently make a user-owned choice final.

## Context discipline

At the start of a later session, load the map and only the evidence linked by the current decision. At the end,
update the map once. A fact belongs in the map only when forgetting it would change the next decision.

## Done when

The destination has an observable finish, every settled decision has a reason and evidence pointer, every open
decision names its dependency, and `Next` identifies one unblocked action. 
