# ml-experiment: test prompts

For a paired run (with and without the skill, same model and grader) once the owner approves live
testing. Written 2026-11-19 during the round 8 review.

## Should fire, with the expected behaviour

- "Fine-tune Qwen on our street-view captions and tell me if it beats the base." -> decision-grade: grilled plan, method scan, stats.py mde before running, preflight, plan-check lock, isolated scores, stats.py paired interval in the report.
- "Quick check: does lr 1e-4 even train?" -> exploratory tier: preflight and sanity only, every number labelled exploratory.
- Run on the RunPod pod -> new run folder only, nothing on the pod edited, results pulled and checked locally.

## Should stay quiet

- "Explain what GRPO is." (learn-fast)
- "Which paper introduced LoRA?" (research quick fact)

## Failure to watch for

- Calling a difference real when the stats.py interval includes 0.
- Skipping preflight on an expensive run.
- Editing files already on the pod.
