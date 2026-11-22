# Writing skills the tstack way

Source: t3dotgg/tstack at commit 11e37a7 (2026-11-11), all 9 SKILL.md files read in full. Measured
with `style_stats.py` on 2026-11-21 against our 16 installed skills.

| Median | tstack | ours |
|---|---|---|
| Body words | 382 | 845 |
| Description words | 8 | 74 |
| Headings | 2 | 5.5 |
| "If" rules | 3 | 1.5 |
| "Do not" / "Never" lines | 3 | 1.5 |
| Links to scripts or references | 0 | 5 |
| Average sentence | 12.7 words | 15 words |

## The rules

1. **Description: the trigger, nothing else.** A typed phrase ("Trigger this if the user says
   'council'.") or one line of what plus when ("File a concise pull request. Use when the user asks
   to file, open, or create a PR."). Never a keyword inventory. For a skill that must fire on its own,
   list only the phrases the owner really types, at most about 25 words.
2. **First paragraph: the job and who owns it.** "You own the work from its current state to a merged
   PR." Then the limits of that ownership.
3. **One paragraph per decision.** Each paragraph is a rule, the condition that changes it, and what
   to do then: "If you cannot reach three providers, or a named member is unavailable, report it
   instead of substituting." Prefer paragraphs to bullets; use bullets only for real lists
   (permissions, a budget, a severity scale).
4. **Predict the cheat, then forbid it in one line.** "If a delegate gives no score, write `no score`.
   Do not invent one." "Timeout, error, or no reply is not approval." "Green mocked tests do not prove
   the user experience works."
5. **Say what is not proof.** Handoffs, summaries and passing mocks are context, not evidence: "Treat
   the handoff as context, not proof."
6. **Permissions are explicit and scoped.** Say what the trigger authorizes, what it does not, and
   that system prompts still apply: "It covers only the tests needed for this task."
7. **Show the output.** Give the exact artifact: a table to paste, a brief to send, a comment format.
   One BAD and one GOOD example beat a paragraph of rules.
8. **Compose small skills by name.** "Use the `sol-loop` skill to verify changes." A big workflow is a
   short ordered list of other skills.
9. **Fight scope.** "It is your job to fight to keep scope limited." "Fix the case that happened, not
   every case that could."
10. **Name the environment and the fallback.** "In T3 Code, use X. Elsewhere, use Y. If neither works,
    report the blocker. Do not substitute."
11. **End with the report.** "Report the PR link, final head, verdict, proof, reviewer outcome, and
    remaining risks."
12. **No helper sprawl.** Self-contained text first. A script only when a check must be mechanical
    (tstack ships one, `pr-wait`).

## What to cut from our skills when rewriting

Origin stories (keep one line at most, or move it to the commit message), "Done when" checklists
that repeat the body, links to more than one or two reference files, keyword-list descriptions,
numbered procedures where the order does not matter, and any rule the plain model already follows.
Keep every rule that a measured failure created.

## Limits

Our skills fire automatically; most tstack skills are typed by phrase. A trigger-only description
risks never firing on its own, so rule 1 allows real typed phrases for auto skills. Every rewrite is
a draft until it beats the current version in a with-and-without test.
