---
name: grilling
description: Stress-test a plan, decision or idea before it is built. Use for "grill me", "poke holes in this", "what am I missing", or before committing to an approach that is expensive to reverse. Add "with docs" to capture decisions as ADRs.
---

# Grilling

Interview relentlessly until the plan has no unexamined assumptions left. Merged from mattpocock's
`grilling`, `grill-me` and `grill-with-docs`, which were one skill and two two-line wrappers.

## The frontier method

Map the plan as a **decision tree**: every decision branches into the decisions hanging off it.

The **frontier** is every decision whose prerequisites are already settled: what you can ask *now*
without guessing at answers you have not heard. Ask the whole frontier in one round. Then wait.

Each round's answers reshape the tree. Settled decisions push the frontier outward and unblock what
depended on them. Recompute, ask the next round. A question whose answer depends on another question
still open in this round belongs to a **later** round.

```
❓ **Q1** , **<title>**: <question, including options if there are any>

➡️ <your recommended answer, and why>

---

❓ **Q2** , **<title>**: <question>

➡️ <your recommended answer, and why>
```

Always give your recommended answer. A question without one makes the human do your thinking.

## Facts are your job, decisions are theirs

When a frontier question needs a fact from the environment, **go find it**: read the file, run the
command, dispatch a subagent, search the web. Never ask the human something you could look up.

Do not block on it either. A running lookup is an unsettled prerequisite, so only questions
downstream of it wait. Ask the rest of the frontier now.

## Hunt the edge cases

Rounds one and two find the obvious. The value is in what comes after. Work these axes explicitly,
and only skip one when you can say why it does not apply:

- **Scale.** What breaks at 100x the expected input? At zero? At one?
- **Failure.** What happens when the thing it depends on is down, slow, or returns garbage? What is
  the state after a crash halfway through?
- **Concurrency.** Two of these running at once. The same user in two tabs. A retry arriving before
  the first attempt finished.
- **Lifecycle.** How does this get migrated, rolled back, deleted? Who cleans up the data in a year?
- **The boring 80%.** Every plan is written for the interesting case. What does the mundane path look
  like, and is it worse than doing nothing?
- **Cost.** What does this cost per run, per month, at the scale above? Who pays attention to it?
- **The undo.** How expensive is reversing this decision in three months? If the answer is "very",
  that decision deserves its own round.
- **The unstated why.** What has to be true about the world for this plan to be the right one? Name
  the assumption, then ask whether it has been checked or just believed.

When a plan survives all of these, say so plainly. Premature agreement is the failure mode of this
skill; so is grilling past the point of value.

## Modes

**Default:** interview only, nothing written.

**With docs** (invoked as "grill me with docs" or similar): as decisions settle, capture them.
One ADR per irreversible decision, stating the decision, the alternatives rejected, and the
assumption it rests on. A glossary entry for every term that turned out to mean two things. Write
them where the repo already keeps such notes; if there is no convention, put them in `docs/decisions/`
and say where.

## Done when

The frontier is empty: every branch visited, every edge-case axis above either worked or explicitly
dismissed, and nothing left silently assumed.

**Do not start building on it until the human confirms you have reached shared understanding.**
