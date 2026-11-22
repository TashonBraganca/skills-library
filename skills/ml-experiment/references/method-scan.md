# Find the best current method before choosing one

Agents default to the methods in their training data. MLE-STAR (arXiv 2506.15692) found agents
relying on model priors picked older architectures, and that retrieving current task-specific models
by web search improved results. Retrieval finds contenders. A matched pilot decides.

Skip this for an exact reproduction whose goal is to preserve a historical protocol.

## Steps

1. **Write the target.** The claim, the acceptable error, the compute and time budget, the exact
   model and task, and what "better" means (metric, cost, robustness).
2. **Search three ways** with the `research` skill, last 12 months first:
   - the incumbent by name, plus its failure reports (`"<method> fails"`, repo issues);
   - a task-only query with no method names: task, metric, limiting resource
     (`papers.py search "<task> <metric> <constraint>" --since 12m`, `papers.py hf "<task>"`);
   - what wins in practice: Kaggle or competition write-ups, the leaderboards' methodology pages,
     maintainers' recommended recipes (TRL, vLLM, verl, SAELens docs and issues).
3. **Open the artifacts** for each contender: code, config, the strongest failure report. A method
   with no runnable implementation for your stack is a lead, not a contender.
4. **Shortlist three:** the proven baseline, the strongest fitting challenger, and one materially
   different approach if it can test the claim. For each, the evidence it works in a setting like
   yours and one condition under which it loses.
5. **Pre-register a matched pilot:** same data, budget and evaluator; the result you expect from
   each; the adoption threshold. Select on validation only.
6. **Freeze the confirmation protocol** after selection, then run it once.

## Record in the plan

`contender | evidence (link, setting) | runnable here? | expected result | loses when | pilot result | decision`
