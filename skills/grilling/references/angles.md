# Attack angles

Use the angles that could change a decision. For each live risk, name the failure, trigger, and cheapest discriminating check. For each live one, produce
a named failure, a trigger, and the cheapest check. If you can run the check, run it.

## Pre-mortem
Assume it failed in three months. Write the three most likely causes, ranked. The top one is
usually something the plan does not mention. Ask: "What did we not look at because it was boring or
because the owner did not want it to be true?"

## Strongest alternative
Argue the best different approach as its owner would. Include a build-vs-buy or a library-vs-custom
option when relevant. Then say what evidence would make the alternative win. If you cannot find a
credible alternative, search for prior art and newer methods (use `research`). If one realistic
option remains after that, name the strongest discarded one and the verified constraint that rules
it out, then challenge the requirement behind that constraint.

## The boring path
Simplest thing that could work: a script, a cron job, a spreadsheet, an existing library, or doing
nothing. State what the plan buys over it, in numbers if possible. If the answer is "flexibility we
might need later", the plan is weak.

## Unstated assumption
Fill in: "This plan is right only if ___." Look for assumptions about users, data quality, model
behavior, API stability, team time, and the owner's own memory of how a system works. Mark each
checked (with evidence) or believed.

## Scale
Current load, the forecast peak, and the first point where something saturates (memory, latency,
rate limits, queue depth, disk, cost). Include the empty or first-run case when it affects the design.

## Failure and partial failure
Each dependency down, slow, or returning garbage. Crash halfway: what state is left, can it be
re-run, is it idempotent. Timeouts and retries that multiply load. Silent failure is the worst kind:
what would show that it failed?

## Concurrency
Two runs at once. Same user, two tabs. Retry before the first attempt ends. Race on a shared file,
row, GPU, or checkpoint directory. Locks and what holds them when a process dies.

## Lifecycle and cleanup
Migration path, versioning, rollback, deletion. Who removes the data, the checkpoints, the pods, the
buckets in a year? What is left running and billing?

## Cost
Per run, per month, at scale. GPU hours, API spend, storage, egress, and the owner's time. Who
notices when the bill doubles?

## Rollback cost
How expensive is undoing this in three months, in hours and in broken downstream things? If high,
that decision gets its own question and a cheaper reversible first step.

## Security and safety
Secrets, auth, input trust, injection (including prompt injection), data exposure, dependency
risk. For LLM and agent systems: tool permissions, what a hostile input can make the agent do.
For safety and interpretability work: dual-use of the artifact, and what is released.

## Evidence and measurement
What number will be believed, and does it measure the claim or a proxy? Could the result be
produced by a bug? Is a good result suspiciously good? (See the owner's verification rules; do
not restate them, apply them.)

## Web apps specifically
Auth and tenancy boundaries, migrations on live data, background jobs and retries, cache
invalidation, abuse and rate limits, observability (how will you know it is broken), and what a
bad deploy costs to reverse.

## Example sharp questions
- "If this fails, what is the first log line that tells you? I found none in the current code."
- "Both arms differ in the intervention and in training tokens. Which equal-token comparison would isolate the intervention?"
- "The boring path is a 40-line script. What does the service buy that is worth the on-call load?"
