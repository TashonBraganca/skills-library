---
name: working-with-agents
description: Dispatching subagents and writing the instructions they run on. Use when fanning work out to parallel agents, when a task is big enough to delegate, or when writing or editing a SKILL.md, CLAUDE.md or AGENTS.md. Dispatching and instruction-writing are the same problem: an agent is only as good as the document it was handed.
---

# Working with agents

Two halves of one job. Merged from `dispatching-parallel-agents` and mattpocock's
`writing-for-agents` (MIT), because writing a subagent's prompt *is* writing for an agent.

## Dispatching

**Subagents run on Sonnet.** Always pass the model explicitly. Never let one inherit the session
model. This is a standing cost rule and it has been enforced by killing running agents mid-task.

**Fan out only for genuinely independent work.** Two tasks qualify if neither reads the other's
output and neither writes the same file. Anything else is sequential work wearing a parallel costume,
and you will pay for it in merge conflicts and contradictory results.

**Send them all in one message.** Separate messages run them in series.

**Guard the context window.** The reason to delegate is that the bulk stays out of your context: the
subagent reads 100k tokens and hands you back 400. If you find yourself pulling its raw output back
in, you have paid for delegation and received none of it.

**Isolation is not free.** Subagents cannot see each other, which is the point, but it means:
- Each needs the full context to do its job. A prompt that assumes what you know produces work that
  assumes what it invented.
- They converge. Independent agents given an open brief reach for the same ideas. Measured: three of
  five independently invented a deep-sea product, two named it identically. If divergence matters,
  say so in each prompt and name what to avoid.
- Shared resources collide. A shared browser reassigns tabs mid-call; agents writing near the same
  paths clobber each other. Give each its own path.

**Verify what comes back.** A subagent reporting success is a claim, not evidence. Check the file
exists, has sane size, and contains what it should. Agents have reported verified work that was a
404 page.

## Writing the instructions

Whether it is a subagent prompt, a SKILL.md, or a CLAUDE.md, the same levers decide whether the agent
behaves the same way twice.

**The pointer decides everything.** A skill's `description`, a line in CLAUDE.md naming a doc: the
*wording*, not the target, decides whether the agent reaches the material. Front-load the trigger
word. One trigger per branch, no synonyms restating one branch. Cut identity the body already carries.
A must-read document behind a weak pointer is a variance bug: sharpen the wording before you consider
inlining the content.

**Two budgets, and everything spends one.**
- *Context load*: always-loaded material, paid every turn whether or not it fires. A model-invoked
  skill's description. A CLAUDE.md line.
- *Cognitive load*: what the human must remember. A user-invoked skill costs zero context and spends
  this instead.

Set `disable-model-invocation: true` unless the agent genuinely needs to reach it alone. If only you
ever fire it, it should cost nothing.

**Push reference down, keep steps up.** Steps the agent performs go in the main file. Reference it
consults on demand can go behind a pointer in a separate file, loaded only when needed. Inline what
every path needs; disclose what only some paths reach.

**Every step ends on a completion criterion**, and its clarity is what stops the agent declaring
victory early. "Understanding reached" invites premature completion; "every modified model accounted
for" forces the work. Make it checkable and make it exhaustive.

**Prompt the positive.** Steering by prohibition drags the forbidden thing into context and makes it
*more* available. Say "write one-line comments", not "don't write long comments". Reserve prohibition
for hard guardrails you cannot phrase positively, and pair it with the target.

**Hunt no-ops.** An instruction the model already follows by default pays context and changes nothing.
The test is behavioural, not aesthetic: does this line change the output versus the default? If not,
delete the whole sentence. This is the highest-yield edit available and it is almost never done.

**One meaning, one place.** The same rule in two files costs maintenance, costs tokens, and inflates
its apparent importance. The environment is a source of truth too: a document restating what
`package.json` or `--help` already says is a cache that will go stale. Cache only what cannot be
looked up: the unwritten convention, the reason behind a choice, the gotcha nothing confesses.

## Done when

Dispatching: every agent got its own paths, an explicit Sonnet model, and enough context to work
alone; and you verified the artifacts rather than the reports.

Writing: every line changes behaviour versus the default, every meaning lives in one place, and every
step says how you know it is finished.
