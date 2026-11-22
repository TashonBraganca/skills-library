---
name: ml-experiment
description: Guard any ML training run, fine-tune, post-training job, evaluation or benchmark against data leakage, evaluator tampering, broken baselines and overclaimed results. Use before and after training, fine-tuning, RL or GRPO runs, building a held-out or eval set, evaluating or comparing models, checkpoints or SAEs, reporting a metric, or saying a run "worked". Pairs with grilling (before) and ml-interp (interpretability work). Not for reading about ML or explaining a concept.
---

# ML experiment guard

Core: a result counts only if a locked plan predates it (`plan-check`), the score came from the frozen
evaluator bound to the candidate (`score --plan --run-key`, `--isolate` for decisions), and every
planned run is accounted for (`reconcile`).

`G=~/.skills-library/skills/ml-experiment/scripts/guard.py` (run `python3 $G --help`). Exit codes:
0 pass, 1 integrity failure (blocks a trusted score), 2 bad input (fix and rerun the check), 3 items a
human must resolve before the affected result is used.

Copy the sections below into your task list. A skipped step stays with its reason. Every way an
agent corrupts ML work, beyond training: `references/failure-modes.md`. Mark each applicable row in
the plan. Uncertainty: `S=~/.skills-library/skills/ml-experiment/scripts/stats.py`.

**Pick the tier first.** *Exploratory* (a quick look, a debug run, a hunch): a capped real-path
smoke run (finite loss, parameters actually update, logs written) plus the input checks in section
4; no plan lock, snapshot or reconcile; every number labelled exploratory, nothing decided on it. *Decision-grade* (anything the owner will
act on, report, or spend more compute on): every section, `--isolate` scores, and the plan grilled
before it is locked. When unsure, it is decision-grade.

**Hand-offs.** `grilling` attacks the plan before `plan-check` (decision-grade). `research` runs the
method scan. `ml-interp` owns any claim about model internals. `learn-fast` when the method is new
to the owner. `writing` for the report. `/second-opinion` on a plan or report the owner will spend
on (ask first). Subagents of any kind need the owner's yes first.

## 0. Pick the method from current evidence

Before locking a decision-grade plan, run `references/method-scan.md`: search the incumbent, a
task-only query and what wins in practice; shortlist the proven baseline, the strongest fitting
challenger and one different approach; pre-register a matched pilot. Skip only for an exact
reproduction of a historical protocol.

## 1. Plan before the run

Write `experiments/<id>/plan.md` from `references/plan-template.md` before spending the budget or
touching final evaluation data. Fill it from existing evidence and pick routine defaults yourself.
Ask the owner only about open decisions that would change the plan. The plan fixes:

- The **decision rule**: the result that would change what happens next, and what counts as
  inconclusive.
- The **comparison claim**: whole method versus baseline, or one component (which needs an
  ablation). Resources that matter for that claim are matched; list every remaining difference.
- The **held-out set** and its split unit (item, user, document, repo, time), matched to the claim.
  Nothing is tuned on it. Checkpoints, prompts, thresholds and templates are chosen on validation.
- **Leakage**: every applicable row of `references/leakage.md`, marked ruled out (how), possible,
  or present.
- **Uncertainty**: the independent unit, planned seeds, and how the interval is computed. Run
  `python3 $S mde --n <items> --p <baseline>` now for independent binary outcomes (for continuous
  or clustered outcomes, estimate power at the independent unit from pilot variance): if the
  smallest detectable effect is bigger than the effect worth acting on, add items or seeds before
  running, or call the result directional.
- **Budget** and stop condition, and the smallest pilot that would show the plan is wrong.
- **Predictions**: the result you expect from each arm before running, and the planned run matrix
  (`plan.json` with `keys` and `runs`) for `reconcile`.
- **Failure modes**: the applicable rows of `references/failure-modes.md`, each ruled out (how),
  possible, or present.

Then `python3 $G plan-check --plan experiments/<id>/plan.md --matrix experiments/<id>/plan.json` (plan and run matrix lock together, once). It fails on a missing or unfilled
section and locks the plan's digest. `score --plan` refuses a plan edited after the lock; a deliberate
change needs `plan-check --relock` and is reported as a protocol revision.

## 2. Keep the evaluator out of the agent's reach

For a trusted score, the evaluator bundle (eval code, final prompts and labels, metric spec,
tokenizer and chat template, decoding config) is frozen before the run and scored from a copy the
training process cannot write.

- Snapshot it outside the workspace, with every file the evaluator imports or reads, the entry
  command and the metrics it must print (its last stdout line must be a JSON object with them): `python3 $G snapshot --root . --files eval.py evallib/metric.py data/test.jsonl metric_spec.json --entry "python3 eval.py --model {candidate}" --metric accuracy --out ~/.ml-guard/<id>`.
  Relative paths are kept, so nested imports work from the copy.
- Score only through the snapshot: `python3 $G score --snapshot ~/.ml-guard/<id> --candidate <checkpoint> --plan experiments/<id>/plan.md --run-key arm=<arm> --run-key seed=<s>`.
  A record without the declared metrics is invalid (exit 1). The records feed `reconcile` directly.
  It runs the recorded entry in a fresh copy with `PYTHONPATH` set to that copy, refuses arguments
  that point back into the workspace, hashes the candidate before and after (a change voids the
  score), and writes a record with the run id, candidate digest, evaluator digests and trust tier.
  An explicit command needs `--exploratory` and is labelled exploratory.
- `python3 $G verify --snapshot ~/.ml-guard/<id>` shows whether the workspace copy drifted.
- The training job never reads final test data or labels. The evaluator, not the candidate,
  chooses the template and decoding settings.
- For any score you will act on, add `--isolate`: the evaluator runs in an OS sandbox
  (sandbox-exec on macOS, bubblewrap on Linux) that cannot read the workspace except the candidate,
  cannot write outside its scoring folder and has no network (`--allow-network` only for an API
  judge; it is recorded). On 2026-11-19 a test evaluator read hidden labels and the network without
  `--isolate` and neither with it (one machine; the sandbox profile still allows reads outside the
  workspace root). Tier `isolated-sandbox`. Without it the tier says
  `local-snapshot-not-isolated`; a snapshot inside the workspace is `exploratory`.

## 3. Preflight, then keep the run honest

Before spending the budget, run `references/preflight.md` at tiny scale on the real code path:
loss at step 0, overfit one batch (training runs), step-0 eval reproduces the baseline, the smallest
dry run that exercises save, reload and evaluation, throughput and a time and cost estimate. Record
the pilot on a validation or smoke split; freeze the protocol and run matrix before full runs or
final scoring. While it runs, check it is alive by
evidence (log growing, steps advancing at the preflight rate) and watch the alarm lines listed
there. On the owner's RunPod, never edit or delete anything already on the pod: new run folders
only, pull results back, run the checks locally.

For a run that must produce its own checkpoint: pre-stage the approved base model, data and
dependencies by revision and digest; no network access to model hubs during the run; no
evaluation credentials or found API keys in the environment. Never download a finished or
instruction-tuned checkpoint when the task is to train one. Record the run with
`python3 $G manifest --run-id <id> --out experiments/<id>/run.json --data <file> --data <file> --seed <s> -- <command>`
(repeat `--data` per file).
Log every run, including failed and abandoned ones. Public benchmarks can sit inside an opaque
base model: for claims that depend on novelty, add a private or newly collected confirmation set.

## 4. Checks before any number counts

- **Split overlap**: `python3 $G overlap --train <train files...> --eval <eval> --id-field id --text-field <field>`.
  Exit 1 is confirmed overlap (shared id or identical content). Exit 3 lists near-duplicate pairs:
  open each and record the decision. Also pass every SFT, prompt, few-shot and method-building
  file as `--train`. A clean result covers only the files you passed.
- **Predictions and metrics**: `python3 $G sanity --pred <file> [--pred <other arm>] --id-field id --expected-ids <eval> --metrics m.json --spec metric_spec.json`.
  It checks ids against the expected set, identical arms, and the metric schema (finite values,
  declared bounds, declared endpoints). Add `--categorical` for classification outputs.
- **Inputs are what you think**: open one example of every input and print its shape, type, first
  rows and count.
- **Weights and config loaded**: print matched, missing and unexpected keys and every override.
- **Caches** are keyed on content and config, never store failures, and miss after inputs change.
- **Every planned run accounted for**: `python3 $G reconcile --plan experiments/<id>/plan.json --results <snapshot>/scores/*.json --lock experiments/<id>/plan.md.lock.json --require-metric <metric>`.
  By default it accepts only valid, isolated guard score records; `--allow-unisolated` marks exploratory work.
  Lock the matrix with the plan: `plan-check --plan plan.md --matrix plan.json`.
  Exit 1 means a summary would cover a subset. A run cut down after an error (fewer rows, steps or a
  skipped checkpoint) is a new protocol revision, never the original.
- **Every number traced**: record claims and result rows, then
  `python3 ~/.skills-library/skills/research/scripts/claims.py check --claims claims.jsonl --evidence results.jsonl`
  and `claims.py untagged report.md`.

## 5. Report

Use `references/report-template.md`: the result is met, missed, inconclusive or invalid, with
candidate, baseline, paired effect on shared items, uncertainty and its unit, and run-to-run
spread where measured. Compute them, never eyeball them: `python3 $S paired --a <baseline preds>
--b <candidate preds> --score-field <field>` (add `--cluster-field` when items share a source)
and `python3 $S seeds <metric per seed>`. Pass `--min-effect` with the plan's smallest effect worth
acting on. An interval that includes 0 is inconclusive, whatever the point estimate says; under 5
independent clusters there is no inference at all. Report seen and unseen separately and lead with unseen. Name what a filter
or dedup step removed. Compare each arm's result with its prediction. Name the missing or fragile
check most likely to reverse the conclusion. For a decision the owner will spend on, offer
`/second-opinion` on the plan or report (ask first).

## Done when

Decision-grade: the plan was grilled, preflight passed, `plan-check` locked the plan before the runs, decision scores came from `score --isolate` bound to the candidate, `overlap`,
`sanity`, `reconcile` and `claims.py check` passed or every finding is resolved and reported, and
the report states the decision outcome with its `stats.py` interval. Exploratory: every number in
the reply says exploratory.
