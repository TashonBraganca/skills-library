# gtm: test prompts

For a paired run (with and without the skill, same model and grader) once the owner approves live
testing. Written 2026-11-19 during the round 8 review.

## Should fire, with the expected behaviour

- "How do I get my first 10 customers for this tool?" -> intake (max 6 questions), research and find-buyers run, gtm_check.py inputs passes before any plan, up to 3 bets each with a receipt, gtm_check.py plan passes, Why this could fail section.
- "Make me a LinkedIn content plan for the agency." -> same gates, then content-engine.md with scored ideas and sources; no automated DMs.
- "Where should I market this?" with no defined product -> grilling on the buyer first.

## Should stay quiet

- "What is go-to-market in general?" (general advice, no product)
- "Fix the pricing page CSS." (studio)

## Failure to watch for

- Writing channel bets before the gate passes.
- Recommending a venue marked 'no' or 'reply only' as a channel.
- Treating impressions as pipeline.
