# How ML work gets corrupted, beyond training

Every row is a failure seen in real agent or human work, the check that catches it, and the tool.
Mark each row that applies in the plan: ruled out (how), possible, or present. `G` is guard.py,
`C` is `~/.skills-library/skills/research/scripts/claims.py`.

## Research loop (the agent's own process)

| Failure | Check | Tool |
|---|---|---|
| Silent protocol degradation: an OOM or download error makes the agent cut epochs, rows, sequence length, or skip the pretrained checkpoint, then report the original protocol (arXiv 2608.26753, M2) | Freeze the planned runs x arms x datasets x budgets. Compare actual tokens, steps, rows and checkpoint ids. A deliberate reduction is a new protocol revision and cannot support the original claim. | `G reconcile`, `G manifest` |
| Oracle or stub substitution: a lookup, exact-match or hard-coded answer replaces a failed model, retriever or reward (M1) | Name the mandatory components. Feed an unseen canary input and perturb required inputs: the real component must consume them and change the result. Read the code path. | Project test |
| Incomplete execution claimed complete: one of three configs run, baselines skipped (M5) | Every planned run is `complete`, `failed` or `not run`. Summaries cover the full matrix or say which part. | `G reconcile` |
| Scale-driven inversion: a small pilot flips the ranking and the agent extrapolates (M3) | State which scale bounds the claim. Use a scale ladder when the mechanism depends on data, compute or capacity. | Plan |
| Post-hoc selection: picking the candidate with the best test score, or swapping in a nicer metric (arXiv 2509.08713) | Selection uses validation only and is logged. The metric list is frozen in the plan. Extra looks at the test set are exploratory. | Plan, run log |
| Number misattribution: a real value from the wrong arm, split, metric or run lands in the report (arXiv 2610.38691) | Every printed number has a claim row bound to its result row. | `C check`, `C untagged` |
| Chasing the last gain: failed branches erased, one pass, then stop | Per iteration log hypothesis, predicted effect, change, result, decision. One factor per change unless the hypothesis is an interaction. | Run log |

## Data

| Failure | Check | Tool |
|---|---|---|
| Train and eval overlap, near-duplicates, shared source families | Overlap on ids, normalised text and n-grams across every training, SFT, prompt and few-shot file. Group by source family where it matters. | `G overlap` |
| Misjoined rows or labels, many-to-many joins, dropped classes, duplicate ids | Unique non-empty ids, join cardinality checks, per-stage row counts with a reason for every dropped row, sample raw-to-final rows by id. | Project test |
| Transform fit on all data (normaliser, tokenizer, sampler, threshold) | Fit on train only; hash the fitted state. | Read the code path |
| A filter or dedup step deletes the signal | Diff before and after; report what was removed and from which slices. | Project script |

## Tokenizer, template and inputs

| Failure | Check | Tool |
|---|---|---|
| Wrong chat template (base vs instruct), duplicated BOS or EOS, wrong assistant loss mask, left-padding shifts, answer truncated by max length | Freeze the tokenizer revision. Save rendered prompts and token ids for representative cases (multi-turn, tool call, near the length limit). Compare training mask and serving boundaries. | Golden fixture |
| Inputs are not what the filename says | Open one of each input; print shape, type, first rows, count. | Manual |

## Evaluation harness and scoring

| Failure | Check | Tool |
|---|---|---|
| Evaluator or labels edited by the agent | Score only through a snapshot outside the workspace, bound to the candidate digest. | `G snapshot`, `G score` |
| Wrong split, benchmark revision, metric direction, few-shot leakage, stale cache | Golden rows with hand-computed expected scores; a cache-miss test after a config change; split and metric ids in the record. | Golden fixture, `G sanity` |
| Answer extraction moves the score: last-number regex grabs reasoning, parser failure becomes "wrong" or "abstain" | Blind-label a stratified sample of raw outputs. Report parsed, invalid and truncated counts per arm. Keep raw completions. | Project script |
| LLM judge follows order, length, identity or text that addresses the grader | Freeze judge version and rubric. Swap pair order, anonymise, include benign injection fixtures, compare with blinded human labels on a calibration set. Report order flips and disagreement. | Project script |
| Small benchmark, few seeds: false precision (arXiv 2504.07086 saw 5 to 15 point seed spread on AIME-sized sets) | Separate item, prompt and seed variance. Paired comparisons on shared items. Ten or more seeds on small sets, or say the result is inside the noise. | Analysis |
| Metric keys, % vs ratio, micro vs macro averaging | A metric spec with units, denominator, aggregation and allowed range. | `G sanity --spec` |

## RL for LLMs

| Failure | Check | Tool |
|---|---|---|
| Contamination or format learning masquerades as RL learning: random or format-only rewards also improve (arXiv 2506.10947, 2507.10532) | At matched rollout budget run base, format-only reward, true reward and a shuffled or random reward. Add a fresh held-out task family. | Plan |
| Reward rises while task success falls; length dominates; all-tie groups give zero advantage; NaN advantages; wrong KL sign | Unit-test reward components on good, wrong, empty and malformed outputs. Track reward against independently scored success, length, KL, clip fraction and group variance. Read high-reward failures. | Project test |
| Train-inference mismatch: sampler and trainer compute different token probabilities (stale weights, quantisation, kernels, MoE routing) | On identical prefixes and weights, log sampler and trainer log-probs per token; check ratio tails and clip share. | Project script |
| Reward hacking of the environment or tests (ImpossibleBench, arXiv 2510.20270) | Include impossible or contradictory task variants; any "pass" there measures cheating. Keep tests outside the agent's write access. | Plan |

## Agentic benchmarks

| Failure | Check | Tool |
|---|---|---|
| Answers reachable in the environment: git history, cached packages, public references, mounted credentials | Build from approved inputs in a clean runner. Inventory reachable files. Keep tests and labels outside. Plant a canary in forbidden material and check traces for it. | Runner |
| Timeouts and infra errors silently counted as passes or dropped | Every task id is accounted for with a status. | `G reconcile`, `G sanity` |

## Inference, serving and timing

| Failure | Check | Tool |
|---|---|---|
| Outputs change with batch size, parallelism, dtype, quantisation or backend at fixed seed | Record the serving config. Compare the same inputs alone, batched and after cache perturbation against a reference. | Golden fixture, `G manifest` |
| Checkpoint loads partially (adapter, expert or shard missing); resume resets scheduler or RNG | Print matched, missing and unexpected keys with an allowlist; compare a resumed run with an uninterrupted one on a short fixture. | Project test |
| Benchmarks time enqueue, a warm cache or a different workload | Fix input and output lengths, concurrency, warmup and cache state. Report time to first token, per-token latency, percentiles and failures. Discard warmup. | Project script |

## Reporting

| Failure | Check | Tool |
|---|---|---|
| Best of N runs reported as typical | All runs, or the pre-registered selection rule, with spread. | Report template |
| Baseline under-tuned compared with the method | Equal tuning budget, logged. | Plan |
| Seen and unseen mixed | Report unseen first, seen separately. | `G overlap` |
