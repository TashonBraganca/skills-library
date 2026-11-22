# find-buyers: test prompts

For a paired run (with and without the skill, same model and grader) once the owner approves live
testing. Written 2026-11-19 during the round 8 review.

## Should fire, with the expected behaviour

- "Where do bookkeepers complain about reconciliation tools?" -> venue map from opened posts, buyers.jsonl and venues.jsonl, live rule receipts, venue_score.py --json.
- Called from gtm -> files land in gtm/buyers/.

## Should stay quiet

- "What are people saying about Claude Code?" (social-search)
- "Build me a lead list of 200 CFOs." (prospecting, owner must ask)

## Failure to watch for

- Counting upvotes or member counts as buyers.
- An archive-only rule copy treated as permission.
