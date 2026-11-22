# Studio test, 2026-11-19: fault log

Two Sonnet 5.5 builders at high effort, same Clearbook brief. One used the `studio` skill (sites/with), one used no skills (sites/without).
Scratch folder: /private/tmp/claude-501/-Users-tashonbraganca--t3-projects-the-skills-god/e033fab4-0f25-4480-8adc-a42895331a47/scratchpad/sites
Status column: open, fixed (with commit or check), or wontfix (with reason).

## Harness and tooling faults

| # | Fault | Evidence | Status |
|---|---|---|---|
| H1 | subagent_gate blocked the 2nd unit of an approved batch of 2 after unrelated owner follow-ups | gate denial after "keep a clean monitor" | fixed: fe445e6, 6 new tests pass |
| H2 | ref_board.py crashed on Dribbble (document.body null) | FAILED on dribbble.com/search | fixed: 9ab7cce, recapture ok |
| H3 | My monitor's stall check used BSD `find -newermt "-10 minutes"`, so it always reported a stall | false alarm while a gate script ran | fixed: monitor uses stat mtime |
| H4 | First monitor was noisy (reported every file the checker wrote) | 10+ events with no milestone | fixed: milestone-only monitor |

## Studio skill and specialist faults (with arm)

| # | Fault | Evidence | Status |
|---|---|---|---|
| S1 | taste-skill's whole asset library copied into site/ | 1,594 files, 37 MB | studio override added fe445e6; builder told to prune; verify final size < 10 MB |
| S2 | taste-skill photo library is Unsplash and picsum.photos | 548 Unsplash entries in assets/photos/photos.json | studio override added fe445e6; verify final page uses none |
| S3 | taste-skill chrome-check writes temporary Chrome profiles inside site/ | site grew to 84 to 86 MB during checks; 185 files in site/.taste-skill/chrome-check | open: verify cleanup after last check; consider a studio rule to run checks with output outside site/ |
| S4 | DESIGN.md written after the site was built and checked, not before | monitor: DESIGN.md=no until after shots=9 | open |
| S5 | Slow: 47+ min against 12 min for the plain build; about 30 min is taste-skill (asset copy, Chrome gates, long instructions) | trace summary: hunt 11.8 min, asset copy 6.2, gates 6.2, other 18.2 | open: judge against quality once both sites are compared |

## Plain build faults (without arm)

| # | Fault | Evidence | Status |
|---|---|---|---|
| P1 | 57 of 66 text blocks start hidden until scroll (blank page for previews, screenshots, no-JS) | scrollcheck: hidden 57 before, 0 after real scroll; reduced motion shows all | open (comparison only) |
| P2 | "Matches against the real books" card is two empty circles | screenshot | open (comparison only) |
| P3 | 13 text elements under 12px | audit_site.py | open (comparison only) |

## Still to check on the studio site when it finishes

Console errors, sideways scroll at 1440 and 390, hidden-until-scroll content, dead links, focus, invented claims, Unsplash or picsum in the shipped page, final site size, README accuracy, and the direction against the owner's "nice and fun, not literal".

## Outcome (studio build stopped by the owner at about 50 min, no README)

| # | Result |
|---|---|
| S1 | Shipped copy pruned to referenced files: 41 MB and 1,800+ files down to 436 KB and 21 files. The builder never pruned. |
| S2 | No Unsplash or picsum in the shipped files (grep). |
| S3 | Chrome-check profiles still inside sites/with/site; excluded from the shipped copy. Open: studio should run checks with output outside site/. |
| S6 | New: 7 to 9 text blocks stay hidden even after scrolling and under reduced motion. Open. |
| S7 | New: commented template leftover in index.html: canonical link to "[the client's domain]". Minor. |
| H5 | subagent_gate read "the moment it goes too long, you stop" as a refusal and blocked an approved launch | open |
| S8 | New: the builder never wrote README.md before the stop. |
| M1 | My pruning missed 2 stylesheets loaded by script, which caused 404s and a 404 px sideways scroll. Fixed by copying both components whole; re-audit clean. |

| H5 | subagent_gate read "the moment it goes too long, you stop and log it" as a refusal and blocked an approved launch | fixed 2026-11-20: lines the owner pasted from Claude's recent replies are ignored for refusal words; 3 new tests, the owner's own "stop" still blocks |

## Rerun with the revised studio skill (commit 0a6303e)

12 min, the same as the plain build. Single 64 KB file, GSAP 3.12.5 + ScrollTrigger pinned. Audit: 0 console errors, 0 sideways scroll, 0 hidden text blocks (first studio: 7 to 9, plain: 57 before scroll), focus visible, no Unsplash or picsum. DESIGN.md written at minute 4, before the build.

| # | Fault | Status |
|---|---|---|
| S1 to S5, S8 | asset copy, Unsplash photos, check profiles in site/, design doc order, slowness, no README | fixed in the rerun |
| R1 | Footer: the giant "Clearbook" wordmark is drawn over the small footer text (tagline and demo-data note hidden) | open |
| R2 | Mobile 390 checked only in the hero and dashboard, by the builder's own account | open |
| R3 | Sign-up buttons point to #trial (no URL given) | expected |

| T1 | Rerun was contaminated: it read the first studio run's board, directions, DESIGN.md and sketch A, and its brief alone asked for "a lot of animations" and GSAP. The 8.4 vs 7.4 comparison is void. | open: fair rerun with identical briefs, fresh folders, no cross-reads, blind grading |

## Fair rerun: revised studio, sandboxed (earlier work chmod-locked, same brief as the plain build)

12 min, 52 KB, GSAP + ScrollTrigger. Trace: 42 tool calls, 0 attempts to read earlier work. Audit: 0 console errors, 0 sideways scroll, 0 hidden text, focus visible, 2 to 3 text elements under 12px, no Unsplash.
Result: roughly a tie with the plain build. Both independently chose the same look (Bricolage Grotesque + Figtree, ink outlines, hard shadows, a playable "match" hero). The skill's measurable gains are technical: content visible at rest, GSAP scroll motion.

| # | Fault | Status |
|---|---|---|
| F1 | studio not followed whole: 15 references captured, 4 kept (target 50+ looked at, 10 to 15 kept). Correction: it did sketch 3 directions (design/sketches/a, b, c); my first trace check missed them. Root cause: 11 of 15 captures were gallery pages, only 6 screenshots opened, and the 25-min cap cut the hunt | fixed in skill (2026-11-20): candidates.txt, gallery pages flagged LISTING by ref_board.py, every kept screenshot opened, Borrowed table (4 of 5 rows cite a reference), default-look rule; enforced by scripts/studio_check.py. Needs a live run |
| F2 | No specialist skill opened (GSAP, animate, impeccable), though studio routes motion to them. Root cause: the pack was on disk in .claude/skills but not in the subagent's Skill list; the brief named the fallback, studio did not, and the run ignored it | fixed in skill (2026-11-20): 4-place lookup order, mandatory skills ledger in DESIGN.md, motion plan from animate before motion code; studio_check.py fails a missing ledger row. Needs a live run |
| F3 | "Bank line. Book line" display type runs off the right edge in the full-page capture (clipped, no scroll) | not a bug: an aria-hidden band scrubbed sideways on scroll (main.js:123, xPercent 4 to -42). Skill now says to confirm edge clipping is a deliberate marquee |
| F4 | Left the sandbox twice: wrote its check script to scratchpad/check.py, and by its own account listed the scratchpad folder. Earlier work was chmod-locked, so it could see folder names only; no contents were read | mitigated: review/studio-test/trace_watch.py flags every OUTSIDE path live (reproduces both writes on the old trace), so a leak can be stopped mid-run; not airtight, a subagent cannot be given an OS sandbox |

## Fixes, 2026-11-20

studio_check.py on the sandboxed run: 8 FAIL (candidates missing, 4 usable references, 11 gallery pages, no borrow notes, no Borrowed table, no skills ledger, no motion plan, default fonts). tests/test_studio_check.py: 11 of 11 cases pass, and a disabled gate makes its case fail. R1 (footer overlap) and R2 (mobile checked in hero only) now covered by the step 7 full-page check at 1440 and 390.
