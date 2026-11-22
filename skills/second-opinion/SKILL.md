---
name: second-opinion
description: Have GPT (through the Codex CLI) attack a plan, diff, experiment design, report or skill from a fresh context, then triage its findings. Use for "second opinion", "ask GPT", "ask Sol", "cross-check", "have another model review", and when research, grilling or ml-experiment reach a decision-grade or hard-to-reverse result.
disable-model-invocation: true
---

# Second opinion

A model misses its own errors far more often than identical errors written by someone else
(Self-Correction Bench, arXiv 2507.02778, 14 models). A reviewer from another model family with
fresh context catches what the author cannot. It costs Codex usage, so use it where a wrong answer
is expensive: a training or eval plan, a research conclusion the owner will act on, a skill rewrite.

## Steps

1. Pick the files the reviewer must read and one sharp question ("Will this eval leak?", "Which
   number in report.md is not traceable to runs/?"). Pass decisions already made with `--context`.
2. Run, with stdin handled by the script (add `--blind <source files>` so the reviewer forms its own answer from the sources before it sees your draft):
   `python3 ~/.skills-library/skills/second-opinion/scripts/second_opinion.py --files <files> --ask "<question>" --out <dir>/<name>-sol.md`
   Default model `gpt-6.2-sol`, effort `medium`. Use `--effort high` only for decision-grade work.
   Exit 3 means the review came back empty or without its sections: read the log.
3. Triage every finding yourself. Sort into **act on**, **consider**, **dismissed**. Each dismissal
   gets a one-line reason. Verify a finding before acting on it: the reviewer can be wrong too.
4. Apply what survives. Report to the owner: tokens used, what you changed, and the dismissed list
   with reasons, so the owner can overrule you.

## Rules

- The reviewer reads only. You make every edit.
- Before every run, unless the owner's latest message asked for exactly this review, ask and wait:
  model, effort, what it will read, and the expected cost (30k to 150k Codex tokens).
- One reviewer at a time. Do not loop until it agrees: two rounds at most, then decide.
- If `codex` is missing or fails, say so. Do not substitute a same-model subagent and call it a
  second opinion.
