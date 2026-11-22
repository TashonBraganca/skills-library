# writing: test prompts

For a paired run (with and without the skill, same model and grader) once the owner approves live
testing. Written 2026-11-19 during the round 8 review.

## Should fire, with the expected behaviour

- "Write a README for the walkability grader in this repo." -> outline first, answer in the first lines, prose_check.py run with no HARD flags, one real example or number per section.
- "Humanize this: <paragraph with em dashes, 'not just X, it's Y', 'delve'>" -> humanize route, protected facts unchanged, one-line list of anything left on purpose.
- "Rewrite these deploy steps in STE100." -> STE route, ste-lint clean, conditions and units unchanged.
- "Make this report fun to read" (attached report) -> use real material in the draft; preserve facts and certainty.

## Should stay quiet

- "Rewrite this function to use async." (code, not prose)
- "Fix the typo in line 3." (one-line edit)
- "Write an AGENTS.md for our repo." (agent instructions)

## Failure to watch for

- Inventing a lively number or anecdote while drafting.
- Dropping a qualifier or date during the humanize pass.
- Firing on code rewrites because of the word "rewrite".

## Paired tests from the Sol research review (2026-11-21)

Generation and grading on GPT-6.1-Terra high. Same rules and hooks in both arms; vary only whether
`writing` loads. Blind the pair; if reversing the order changes the verdict, report it unresolved.
An invented fact, a lost condition or a changed level of certainty fails the output.

1. Release note (at most 100 words) for support leads on the double-click Export fix: staging replay
   of 500 double-clicks, old build 500 extra copies, new build zero because it reuses the original
   job, production not measured. Pass: leads with what happens on the second click; 500 and
   500-to-zero in the first two sentences; job reuse in ordinary words; staging named and the lack
   of production data kept; at most 100 words; no speed, savings or rollout claim.
2. Field note cleanup ("keep my dry voice"): one-line fix, finding it ate Tuesday, a "not just
   pivotal, testament, seamlessly" sentence, four staging runs with no duplicate emails, "may have
   helped", a link and the literal log text `BACKOFF -- retry`. Pass: keeps the one-line fix and
   Tuesday lines first; keeps four runs and zero duplicates; keeps the causal link uncertain; keeps
   the link target and log text exactly; drops the promotional contrast and adds nothing.
3. STE runbook for eu-west-1 queue pause and resume (200 jobs for 5 minutes, no active deploy, page
   Release Ops if a deploy is active, wait 30 seconds, resume only below 50, else page Billing Ops).
   Pass: all three pause conditions before the command; the deploy branch pages Release Ops and
   forbids pausing; waits 30 seconds; at exactly 50 stays paused and pages Billing Ops; both commands
   byte for byte; one action per procedural sentence.
