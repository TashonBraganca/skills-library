# Writing for agents: SKILL.md, CLAUDE.md, AGENTS.md, subagent briefs

An agent is only as good as the document it was handed.
(Adapted from earlier skills in this library and mattpocock/skills, MIT.)

## The pointer decides whether it fires

A skill's `description` and a CLAUDE.md line that names a doc decide whether the agent reaches the
material. Write the description as a trigger: the verbs, file types, error strings and phrases the
owner actually types. One trigger per branch. A summary of what the skill "is" tends to fire less
often; check trigger wording against real owner prompts when it matters.

## What the evidence says about skills (read 2026-11-19)

- Skills help as procedural anchors (numbered steps, checklists, scripts that stabilise what the agent
  does), much less as injected facts: 65.7% versus 4.5% of skill-use cases in "Demystifying Agent
  Skills" (arXiv 2608.14036). Write steps and checks, not essays.
- Focused skills with at most three modules beat larger or exhaustive bundles (SkillsBench, arXiv
  2602.12670, 87 tasks, 18 model-harness setups; curated skills +16.6 points on average).
- Public web-dev skills lowered pass rates by 1.3% to 4.2% and raised token cost 72% to 394%; losses
  concentrated on easy tasks; anti-pattern rules beat example-heavy content (WebDev-Skills-Bench,
  arXiv 2608.23067). So: a skill must not fire on easy tasks, and "do not X, because Y" lines beat
  long examples.
- Retrieval degrades as the pool grows: actual-use precision fell from 29.6% to 3.3% going from 5 to
  100 skills (arXiv 2608.14036). Few skills, distinct triggers.
- Adherence drops as instruction count rises and earlier instructions are favoured (IFScale, arXiv
  2507.11538). Put the rule that matters most first.
- Scan-only reviews (structure checks, LLM judges) do not answer whether a skill helps a live agent; two scan types agreed at Spearman 0.14 (ACES, arXiv 2608.20614). The only proof a
  skill helps is a paired run with and without it on the same tasks, model and grader, plus a
  length-matched irrelevant control.

## Two budgets

- Context: always-loaded text (auto skill descriptions, CLAUDE.md lines) is paid every turn.
- Attention: what the human must remember. A manual skill (`disable-model-invocation: true`) costs no
  context. Use it for anything only the owner starts.

## Shape

- Steps the agent performs stay in SKILL.md. Reference it consults sometimes goes in `references/`
  behind a pointer that says when to read it.
- Write each step as trigger, inputs, action, success evidence, failure branch, stop. Say who may
  act, what it may read and write, where results land, and when it must ask. "Understanding
  reached" invites early exit; "every modified model accounted for" forces the work. A partial tool
  result (exit 3, PARTIAL, a capped page) must never be reported as complete: say so in the step.
- Tell the agent to copy the steps into its task list and keep a skipped step with its reason. A
  skipped check must stay visible.
- Prompt the positive ("write one-line comments"). Keep prohibitions for hard guardrails and pair
  each with the target behaviour.
- Delete no-ops: a line the model already follows by default changes nothing and costs tokens. The
  real test removes the line in a fixture task and compares behaviour; your own guess is a weak test.
- One meaning, one place. Do not restate what `--help`, `package.json` or another skill already
  says. Cache only what cannot be looked up: the unwritten convention, the reason, the gotcha.
- Use the [ASD-STE100 mode](../../writing/references/ste100.md) for steps that must be followed exactly.

## Subagent briefs

- Give the full context: goal, decisions already made, file paths, the evidence rules, and the file
  to write. A brief that assumes what you know returns work built on what it invented.
- Independent agents converge on the same ideas. When variety matters, have each write
  independently before seeing others' output, and name what to avoid.
- Give each agent its own output path. Shared browsers and shared files collide.
- Ask the owner before spawning. Give the count, model, task and reason for delegation. Use high reasoning effort.
- A subagent's "done" is a claim. Open the artifact: exists, sane size, fresh timestamp, right content.

## Done when

Every line changes behaviour versus the default, every meaning lives in one place, every step says
how you know it is finished, and the description names the words that should trigger it.
