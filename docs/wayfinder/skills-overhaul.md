# Skills overhaul: every skill measurably helps, reads well, and runs on its own

## Done means
Each kept skill beats the no-skill run on a blind paired test, with outputs the owner finds easy and fun to read. ([live test](../../../.t3/projects/the-skills-god/review/paired/terra3_grading/grade_all-out.md))

## Constraints
- Ask the owner before any subagent, Codex reviewer or paired test run. ([global rules](../../templates/claude-md-fragment.md))
- Subagents run on Sonnet. ([global rules](../../templates/claude-md-fragment.md))

## Decisions
- humanizer and ste100 folded into writing; resume-all removed: owner request 2026-11-19. ([commit 3cae923](../../skills.txt))
- bro and wayfinder start on their own in long or deep work; replies over 300 words open with a bro summary: owner request 2026-11-19. (commit 89f5a59)
- Paired test harness: clean Codex home, neutral rules, skill helpers and network allowed for both runs: two earlier attempts were confounded. (run_terra.py, runs_terra3)
- studio hunts wide (30+ candidates, 5+ source types incl. Dribbble, 21st.dev, three.js), captures every reference, never builds the look from a literal picture of the subject, sketches 3 directions with one bold: owner feedback 2026-11-19 that its directions were too literal and too dense. (skills/studio/SKILL.md)
- research is deep by default with search floors, and its report puts a short read on top and the audit trail below: owner feedback 2026-11-19 that outputs were too dense. (skills/research/SKILL.md)

- studio fixes for F1 and F2 (gallery pages, no specialists, default look) are enforced by scripts/studio_check.py: sandboxed run 2026-11-19 tied the no-skill build. ([fault log](studio-test-2026-11-19-faults.md))
- Paper explainer pair (AtlasKV, Sonnet, leak-checked): with skills = HTML step explainer, 8.4 min, $1.42; without = 2,100-word Markdown, 6.7 min, $0.67; blind Opus grade 8.2 (with) vs 8.0 (without): with teaches the mechanism better, without is more accurate and more critical. Fixed studio vs no-skill landing page: 8.6 vs 8.4. Both n = 1, one grader. (review/explain-test, scratchpad blind/out/grades.md)
- studio puts the owner's taste (fun, motion-rich) above specialist house rules and demotes taste-skill to a toolbox: side-by-side test 2026-11-19, the plain build was more fun. ([fault log](studio-test-2026-11-19-faults.md), commit 0a6303e)

- whichai.dev (checked 2026-11-20): Taste skill v2 made the same 5-page job cost 8 to 11x more for Opus, Sonnet and Kimi; with no skill, Opus 5.5 and Sonnet 5.5 drew the same cream-serif page. Supports studio's toolbox use of Taste and its anti-default rule. Rankings there are one person's taste. (scratchpad whichai/, report https://claude.ai/artifact/E2J8Cg1A4theiqSmnaJLoY)

- Opus paper explainer pair (AtlasKV, 2026-11-20, leak-checked: 0 skill reads in the off arm): with = learn-fast + writing fired, interactive HTML, 14.3 min, $3.97 (https://claude.ai/artifact/6zr986dXqx7xWSScEv7KXN); without = Markdown, 3.6 min, $1.21 (https://claude.ai/artifact/4gq99dom11L83cxCraCUsp). Owner reads them; not graded. Comparison page of all 70 whichai runs plus tstack analysis: https://claude.ai/artifact/QQKWX5RnbzC2gwWSmHAu2j

- 2026-11-21: library errors from the Opus review fixed (commits d61ca0c, e11c2af); learning requests must run learn-fast and writing (prose_gate). Owner: Taste stays a toolbox; Claude is never a contributor in any profile (fragment rule, attribution settings, trailers stripped from 67 local commits, backup branch backup/before-trailer-strip-2026-11-21).
- 2026-11-21: owner called the Opus AtlasKV page "horrible". learn-fast rewritten twice (plain story, causal steps, catch on the default path, Go deeper layer, explain_check.py, tested template). New Opus page: https://claude.ai/artifact/DcPVnccW2g8H7kAUQdhFqF (passes the checker; the old page fails it).
- 2026-11-21 night run (owner: "fix them the entire night until all the skills are perfect"): per skill, a Sol 6.2 medium research review with web search (review/night/<skill>/sol.md), fixes, then a blind with-vs-without test generated and graded on Terra high (review/night/runs/). At most 2 model sessions at once.

- learn-fast: owner picked the old version (B) in a blind A/B/C review; kept with "make it fun to read" and a show-what-matters rule (key formulas and numbers stay on the main path). Earlier Terra 3/3 win was contaminated by test topics inside the skill. (commits 88ec8cb, 5fc45aa)
- research: trimmed 171 -> 83 lines and installed; blind test on fresh questions split 1-1, new version 2-3x faster and half the cost. (commit after a84a039)

- grilling, gtm, find-buyers: each beat the plain model in a blind with/without test on fresh tasks; gtm and find-buyers cost 6-9x more. ([results](../results-2026-11-21.md))

## Open decisions
- [x] Fix the library-level errors found 2026-11-20 (done 2026-11-21), as corrected by the Opus review: global CLAUDE.md loads twice and the ~/.claude copy lacks the never-a-contributor rule; installer leaves animate-expo, apple-design, improve-animations loading; ~54 skills listed without descriptions; learn-fast vs anthropic-skills:learn overlap; X search dead? | blocked by: owner (asked to find errors first, not improve); 3 corrections re-verified 2026-11-20 | evidence: [report](../../../.t3/projects/the-skills-god/research/skill-quality-2026-11-20/report.md)
- [ ] Re-test every skill after its night fixes | in progress: night run, owner go-ahead 2026-11-21 | evidence: live test results above
- [ ] Keep the 5 skills that won by only half a point, given 3.5x input tokens? | blocked by: owner | evidence: [grades](../../../.t3/projects/the-skills-god/review/paired/terra3_grading/scored_all.json)
- [ ] A sturdier verdict: 3+ tasks per skill and a grader that did not write the skills? | blocked by: owner | evidence: missing

## Next
Finalized 2026-11-21. Next session: test the remaining untested skills only when the owner asks ([results](../results-2026-11-21.md), Open).
