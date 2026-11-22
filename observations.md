# Skill observations

One line per skill misfire or owner correction: `date | skill | what happened | what should have happened`.
Reviewed with `/improve-skill review observations`.

2026-11-19 | agent fan-out | user: max 1 Sonnet subagent at a time, rest on GPT-6.1 Terra medium via Codex delegate_task (limits)
2026-11-19 | learn-fast | rebuilt around quizzes and hint-gating | owner wanted the clearest explanation: a step-by-step story where each step builds on the last, one growing diagram, micro-animation, writing skill's fun+humanize passes; practice optional
2026-11-19 | writing | pilot: 0/2 should-fire prompts invoked writing, even 'Humanize this' | owner wants writing forced in every Claude session: always-on rule, router hook, prose_gate Stop + PostToolUse hooks
2026-11-19 | skill evaluation | proposed grading the partial pilot on Terra | owner wants blind grading by Opus at the end
2026-11-19 | writing | treated enjoyable prose as an extra pass and mixed in agent instructions | draft for readability from line one, retain the humanizer, and scope writing to text for people
2026-11-19 | bro | disable-model-invocation kept plain restatements manual | route plain-language and confusion requests automatically
2026-11-19 | studio / HyperFrames | Owner caught a clipped Loop count and distracting map-pin sounds in the exported film | Check decoded frames at each count peak and confirm the actual mix follows the marker cues before delivery.
2026-11-19 | paired eval harness | no-skill arm still got global AGENTS.md and harness rules naming skills it lacked, so baseline was handicapped and answers leaked their arm | run both arms from a clean CODEX_HOME with neutral rules; strip and log arm-revealing sentences before grading
2026-11-19 | learn-fast | owner typed /teach, which does not exist; routed to learn-fast | consider a /teach alias for learn-fast
2026-11-19 | studio, research | outputs too dense; studio directions too literal and narrow, no wide reference hunt | studio hunts 5+ source types and sketches non-literal directions; research report = short read + audit appendix
2026-11-19 | subagent_gate | approved batch of 2 blocked its 2nd unit after unrelated owner follow-ups | anchor the batch to the approving message; a later hold or refusal still cancels
2026-11-19 | studio + taste-skill | builder copied taste-skill's whole 37 MB asset library, whose photos are Unsplash and picsum | studio overrides: never use those photos, ship only referenced assets
2026-11-19 | studio | with-skill site blander than plain Sonnet: taste-skill house rules (neutral 90-95%, no playful copy, dealt layouts) overrode the bold direction | owner taste beats specialist rules; motion-rich by default; taste-skill demoted to toolbox
2026-11-19 | subagent_gate | REFUSAL regex read a conditional 'you stop it when it runs long' inside an approval ('sure ...') as a hold | needs a smarter hold check: only treat stop/wait as a hold when it targets the launch itself
2026-11-19 | test design | I gave the studio rerun the first run's research and a richer brief than the baseline, two variables at once | fair rerun: identical brief, fresh isolated folders, trace-checked, blind grading
- 2026-11-20 research: reported 'every skill loads twice' from /skill-doctor duplicate rows without checking the live skill listing; Opus review showed it was CLAUDE.md that loads twice (and has drifted). Lesson: confirm a tool's count against the session's own listing before calling it an error.
2026-11-21 | learn-fast | AtlasKV page (Opus, with skill) was an expert paper digest in ladder form: 5+ new terms per step, Greek letters, many numbers, no everyday picture; prose_check passed it (grade 6.2) because short jargon sentences score easy | owner: 'horrible, make it way easier and fun'; needs plain-story-first, a jargon/number budget per step and a check that catches jargon
2026-11-21 | night run | Codex usage limit hit at 02:56 after 6 Sol research runs and 4 Terra test batches; 4 queued Sol runs and the studio pair failed instantly | check codex rate headroom before long queues; make sol_research.sh stop the queue on a usage-limit error
2026-11-21 | learn-fast | old skill files contained all 3 test topics (AtlasKV example, the watch prompt phrase, tests/cases.md), so its Terra 3/3 win was contaminated | fresh leak-checked topics for every test; keep test topics out of skill text
2026-11-21 | research | in clean runs (no router hook) research did not fire even on 'Research whether...'; forced /research for the test | triggering depends on the router hook; test content with forced invocation
2026-11-21 | shutdown | pkill -f 'cloudflared tunnel' also killed T3 Code's own tunnel (it auto-restarted) | stop only processes by the pid files you created, never by name pattern
