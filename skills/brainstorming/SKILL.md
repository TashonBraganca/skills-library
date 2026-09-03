---
name: brainstorming
description: Explore intent fully before starting anything important, and verify with evidence before claiming it works. Use at the start of a new feature, decision, or plan; and again before saying something is fixed, passing, or done.
---

# Brainstorming and verification

One skill, two moments in the same task: before you start, and before you claim you finished.
Merged on purpose. Both are about the same failure: moving forward on what you assume instead of
what you actually know.

Throughout: state what to do, not just what to avoid. "Don't guess the config" is weaker than "read
the config file before answering." A rule with no positive action is a rule half-written.

## Before starting anything important

Don't jump to a plan. Instead, work out loud through:

- **The actual goal**, not the first request that arrived. Ask what the person is really trying to
  get to, if the request only names a step toward it.
- **What already exists.** Read the relevant files, the git log, the past corrections in this
  conversation, before proposing anything. A plan that repeats a mistake already made in this
  session is a plan that wasn't informed by it.
- **What could go wrong**, named specifically: the edge case, the scale it breaks at, the thing that
  fails silently. Don't list these to seem thorough; list them because one will actually happen.
- **What you don't know.** Don't fill a gap with a plausible guess. Instead:
  - If it's a **decision** only the person can make, ask one sharp question that narrows it, with
    your own recommendation attached.
  - If it's a **fact** that exists somewhere, use the `research` skill and find it before answering.
    A guessed fact stated with confidence is worse than an admitted gap.

Don't propose the first idea. Instead, hold two or three real approaches side by side, say what each
costs, and recommend one with a reason.

## When you get corrected

Don't say "you're right" and move on. That's compliance, not correction. Instead:

1. **Say specifically what you missed** and why you missed it. Not "good catch", the actual gap in
   your reasoning.
2. **Check whether the same blind spot affects anything else** you've already done or are about to
   do. A correction that only fixes the one instance and leaves the pattern standing will resurface.
3. **Say what changes going forward**, concretely, not "I'll be more careful."

Carry corrections forward inside the task. If it's the kind of miss that will recur across tasks, not
just this one, that's `improve-skill` territory: fix the skill, not just this instance.

## Before claiming anything is done

**No completion claim without fresh evidence, produced this message.** A previous run, "should
pass now", or an agent's self-report is not evidence.

Before saying something works, is fixed, passes, or is complete:

1. **Name the command that proves the claim.** If none exists, that's the first problem to fix.
2. **Run it now, in full**, not a partial or extrapolated check.
3. **Read the actual output.** Exit code, failure count, the real numbers, not a skim.
4. **Only then state the claim, with the evidence attached.** If the evidence doesn't support it,
   state the real status instead.

Don't use "should", "probably", "seems to". Don't express satisfaction before verification: "great",
"perfect", "done" said before the check is a claim, not a description. Trusting a subagent's success
report is the same mistake at one remove; check the artifact it produced, not its summary of it.

None of the excuses hold: not "I'm confident" (confidence isn't evidence), not "linter passed"
(a linter isn't a compiler), not "just this once", not "I already checked something adjacent".

## Done when

Starting: the goal is named, existing context was actually read, real risks are named specifically,
every unknown was either asked about or researched, and a real alternative was considered and
rejected with a reason.

Finishing: the verification command ran in this message, its output was read in full, and the claim
matches what the output actually showed.
