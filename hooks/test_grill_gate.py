"""Regression cases for grill_gate.decide. Run: python3 test_grill_gate.py"""
from grill_gate import decide
FIRE = ["How do we train a 7B model?", "Build me a small CLI that renames photos by date",
        "Plan the migration of our Postgres schema to v2", "Find papers on induction heads.",
        "Can we compare the build against the last stable release?", "I need you to train a model on this data",
        "Implement the best checkpoint selection rule from the approved spec.", "the build is broken. fix it and add a test",
        "Which optimizer should we use for this run?", "Research the best SAE architectures for Gemma 3",
        "let's set up the eval harness", "Training plan for the 1B run",
        "Could you write a training plan for GRPO?", "Draft an eval protocol for the judge study",
        "Find the best tokenizer for Hindi", "find out why the loss spikes at step 3k",
        "We are choosing between DPO and GRPO for the next run. Which fits a single GPU?",
        "Plan a zero-downtime database migration. Change nothing else.",
        "/research compare two evaluation protocols for the release",
        "Fix the typo in the README. Then design a migration of the production database."]
SKIP = ["Do not train or fine-tune. Explain this chart.", "what does this function do", "thanks, looks good",
        "/review the latest diff", "Why is the build failing on CI?",
        "<task-notification>Agent Build hooks finished</task-notification>",
        "Delegated task node:x (Answer keys) [completed]: build research", "Context handoff (delta): build",
        "12345", "", "Find the duplicate key in this row", "Explain this chart. Do not plan anything yet.",
        "Replace the typo in the approved report. Fix it and change nothing else.",
        "/bro", "/review the latest diff", "Add a period to the README",
        "Explain this snippet:\n```\ntrain the model for 3 epochs\n```"]
bad = [p for p in FIRE if not decide(p)] + [p for p in SKIP if decide(p)]
print(f"{len(FIRE)+len(SKIP)-len(bad)}/{len(FIRE)+len(SKIP)} cases correct")
for p in bad: print("WRONG:", repr(p), "->", decide(p))
import sys as _s; _s.exit(1 if bad else 0)
