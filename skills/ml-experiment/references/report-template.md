# Experiment report: <id>

**Result.** <met, missed, inconclusive or invalid>, with candidate, baseline, paired effect on shared
items and its uncertainty. If the run underperformed, say so here.

**Numbers.**

| Variant | Metric (held-out, unseen) | Spread (n seeds) | Seen-items metric | Notes |
|---|---|---|---|---|

Item n, seed n, and the resampling or analysis unit. Say which source of variance was measured.
Paste the `stats.py paired` lines (shared items, paired difference, 95% interval, McNemar for 0/1
scores) and the `stats.py seeds` line. Items scored in only one arm are reported, not dropped.

**Checks run.** Score record from the evaluator snapshot: <path and digests, or "exploratory">.
Split overlap: <confirmed, candidates and their decisions>. Prediction ids and metric schema:
<result>. Inputs opened: <what you looked at>. Weights and config: <matched / missing keys>.

**What the number does not show.** <the proxy and its gap; what was not tested>

**What was removed.** <any filter, dedup or cleanup step, how much it removed, of what kind>

**All runs.** <every run, including failed and abandoned ones, with one line each>

**Model info sheet** (Kapoor and Narayanan):
1. Clean train-test separation: <argument>
2. Each feature in the model is legitimate: <argument>
3. Test set is drawn from the distribution of scientific interest: <argument>

**Weakest part of this result.** <say it before someone else finds it>
