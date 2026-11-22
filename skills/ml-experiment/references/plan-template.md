# Experiment plan: <id>

Written before the first run. Date: <YYYY-MM-DD>. Commit: <sha>.

**Question and hypothesis.** <one sentence each>

**Decision rule.** If <metric> on <held-out set> is <above/below> <value> versus <baseline>,
we <do X>; otherwise <do Y>. Decided before any run.

**Metric.** <name>, higher or lower is better, computed by <script path> at <commit>.
Evaluator snapshot: <path outside the workspace>, made <date>, scored only with `guard.py score`.
Approved base model, input snapshots and network policy for the run: <...>

**Baseline and controls.** <each one>. Comparison claim: <whole method, or one component>. Match the
resources that matter for that claim and list every remaining difference. Component claims need an
ablation or factorial design.

**Data.** Train <path, rows, sha256>. Validation <path, rows, sha256> (all tuning happens here).
Held-out <path, rows, sha256>. Split unit: <item, user, document, repo, time>, because the claim
is about <population>.

**Leakage review** (`leakage.md`): one line per type: ruled out (how), possible, or present.

**Uncertainty.** Smallest effect worth acting on: <...>. Smallest detectable effect at this size
(`stats.py mde`): <...>; if it is larger than the effect worth acting on, add items or seeds, or
label the run directional. Independent unit: <items, prompts, seeds>.
Planned seeds: <n>. Interval method: <...>. What we do if the interval is inconclusive: <...>.

**Method scan** (`method-scan.md`): contenders, evidence, runnable here, expected result, decision.

**Predictions.** Before any run: the result you expect from each arm, and the result that would
change the decision. The run matrix lives in `plan.json` (`{"keys": [...], "runs": [...]}`).

**Failure modes** (`failure-modes.md`): every applicable row, ruled out (how), possible, or present.

**Pilot and preflight** (`preflight.md`). The smallest run that would show the plan is wrong, the
preflight results (step-0 loss, one-batch overfit, step-0 eval versus baseline, dry run with reload,
throughput, time and cost estimate), and what promotes it to the full run.

**Budget.** <GPU hours, API cost>. Stop when <condition>.

**What would make this result untrustworthy.** <the specific failure you most fear>
