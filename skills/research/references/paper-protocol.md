# Paper reading protocol

Use this for every paper the answer depends on. Skip it for papers you only mention as background.

Get the text: `python3 $S/papers.py fulltext <arxiv-id>` shows a section table. Read sections with `--section`.
Open the exact version on the venue, owner, or author site. For arXiv, use fulltext and expand clipped sections. If extraction fails, try the publisher or author PDF, then inspect decisive figures and tables in the rendered original. Record unavailable sections and qualify any claim that depends on them.

## Read in this order

1. **Abstract and intro.** Write the claim in one sentence. Note what the paper says is new.
2. **Method.** What was done, exactly? Could you reimplement it from the text? Note any step that is vague.
3. **Eval setup.** Datasets, metrics, seeds, compute, prompts, judge models, data splits. Where did the test set come from?
4. **Baselines.** Are baselines recent, tuned and run by the authors with equal effort? Weak or default baselines inflate gains.
5. **Results.** Record the table row or plot and the comparator, metric, denominator, uncertainty, and workload. For SAEs record model, layer, site, L0, width, and dataset. For safety repairs record threat model, template, safety metric, and task utility. For training record hardware, precision, sequence length, rollout settings, and versions. Rank only within shared conditions. Are there error bars or several seeds? Is the headline number the best of many runs?
6. **Ablations.** Does the removed part actually matter?
7. **Limitations.** Read the authors' section. Then list what they did not say.
8. **Appendix.** Hyperparameter search budgets, extra datasets, failure cases. Many caveats live here.

## Checks that catch most problems

| Check | How | Red flag |
|---|---|---|
| Code released | `--code`, then `gh api repos/OWNER/REPO` and open the README | No repo, "code coming soon", repo untouched since the paper, no eval scripts |
| Code matches paper | Trace the decisive table or figure to the exact config, evaluator, data or model revision and raw outputs. Cross-check code defaults (prompt template, split, scorer) against the reported protocol and look for errata. If cheap, recompute a table slice locally. | Only training code, defaults that differ from the paper, or a recomputation that disagrees. A table recomputation earns table-level confidence, not a training replication. |
| Independent evidence | Search exact titles, aliases, forward citations, code forks and benchmark reports. Compare authors, model, task, metric, and setup. | Distinguish same-protocol replication, changed-setting evaluation, discussion only, and no evaluation found in the routes searched. |
| Overlap and leakage | For decisive metrics, trace overlap among training, calibration, tuning, prompt construction, and evaluation data. Inspect deduplication, split unit, and judge validation. | Record what was checked and classify overlap as demonstrated, plausible, or unresolved. |
| Cherry-picking | Number of tasks tried versus reported | Only the tasks where the method wins |
| Scale of claim | Does the evidence cover the claim (one model, one dataset) or only a slice? | "General" claim from one 7B model |
| Version and status | Check v1 against the latest version, the landing page and proceedings. Record preprint, peer-reviewed, corrected or withdrawn. | Citing v1 for a number revised in v3; citing a withdrawn paper as evidence |
| Reproduction reports | `gh search issues "reproduce OR replicate OR mismatch" --repo OWNER/REPO`, plus `papers.py cites <id> --grep "reproduc|replicat|fail"` | Open issues reporting different numbers with no maintainer answer |
| Reviewer objections | `papers.py reviews "<title>"`, then read the forum with `fetch.py` | An objection the final version did not address |
| Venue | Preprint, workshop or main conference? | Peer-review status unknown |
| Conflicts | Authors' employer sells the thing measured | Vendor benchmark of its own product |

## Safety and interpretability specifics

- Probing and steering results: is there a control (random direction, shuffled labels)? Probes can read what the model did not use.
- SAE and circuit claims: is faithfulness measured by intervention, or only by looking at activating examples? Do features survive a different seed or dictionary size?
- Reward hacking and eval tampering: does the setup let the agent see or edit the evaluator? Who patched what, and how was it measured?
- Alignment evals: are the scenarios synthetic? Does the model know it is being tested?

## What to record

Add one row per decisive claim and source (see evidence-register.md). Pin the version and locator, and record what would change the conclusion.
