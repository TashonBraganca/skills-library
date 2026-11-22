# Query plan

Write the plan into your notes before running anything. Use one block per decisive question.

## Template

```
Question: the claim to resolve
Owner route:  announcement, technical report, model or dataset card, repo, leaderboard methodology
Independent:  replications, forward citations, issues, other labs, practitioners
Objection:    the strongest plausible objection
Conditions:   what must match for two results to compare (model, task, metric, setup, version)
Would change: the evidence that would change the answer
Option: X (alt names: ..., old name: ...)
For:      "X" / X tutorial / X benchmark / X review / X in production
Against:  "X problems" / "why I stopped using X" / "X doesn't work" / "X regression" / "X vs Y" / "X alternative" / "X too slow" / "X broke"
Beside:   comparison posts that name 2+ options, "what do you use for <job>"
Code:     gh issues labeled bug (open and closed), gh issues sorted by reactions, last 5 releases, last commit date
Window:   12m default; second pass 90d; one date-sorted pass
Stop a route after reasonable variants stop adding evidence. Before closing a decisive question, check the owner, an independent route, and the strongest counter-search. Log failed coverage separately.
```

## Against-searches that find real failures

Reddit and HN titles:

- `"why I stopped using X"`, `"why I switched from X"`, `"moved away from X"`, `"dropped X"`
- `"X is overrated"`, `"X is a trap"`, `"X vs"`, `"alternatives to X"`
- `"is X still worth"`, `"X after the update"`, `"X broke"`, `"X regression"`

GitHub:

```
gh search issues "X" --repo owner/name --label bug --state open --sort comments --json title,url,commentsCount
gh search issues "wontfix" --repo owner/name --json title,url
gh search issues "performance regression" --repo owner/name --created ">2026-01-01" --json title,url
```

Papers:

- `"X fails to reproduce"`, `"X replication"`, `"revisiting X"`, `"X does not generalize"`, `"critical look at X"`
- For each decisive anchor, walk backward to the originating method, metric and baseline, and forward by exact title or DOI to replications, critiques and successors. Search method aliases in those papers and their artifacts. Record `anchor -> cited/citing -> evidence role`. Open a second hop when it can change the answer.

## Synonyms

Fields reuse and rename ideas. List exact names, abbreviations and old names as aliases, and run each as its own query. List related methods separately. For each result, verify which method and configuration it actually evaluates.

- Aliases: sparse autoencoder, SAE. Broader discovery term: dictionary learning. Related methods, not synonyms: transcoder, crosscoder
- mechanistic interpretability, mech interp, circuits, activation patching, causal tracing
- reward hacking, specification gaming, reward tampering, evaluator tampering
- jailbreak, red teaming, adversarial prompt, prompt injection
- RAG, retrieval-augmented generation, grounded generation

Check the first pass for terms you did not know and add them to the list.

## Date discipline

- Use the route's supported date or version filter. Record the effective window. Retrieval commands (thread, transcript, fulltext) and the dev.to path have no date filter.
- Run both relevance and recent-first discovery for fast-moving claims (`--sort date`, `--by date`), then verify dates on the sources.
- Search without a date limit for original methods, decisive prior comparisons or negative results, and citation chains.
- When recent evidence is sparse, check a dated owner index and a second discovery route. Record the effective cutoff and the remaining gap.

## Choosing subreddits and venues

- Reddit: one general (r/MachineLearning, r/programming), one tool-specific (r/ClaudeAI, r/LocalLLaMA), one skeptical or niche. Include the tool's own subreddit if there is one.
- HN: run stories and comments. Comments hold the objections.
- Papers: arXiv categories cs.LG, cs.CL, cs.AI, cs.CR for ML safety. Add stat.ML for evaluation methods.
