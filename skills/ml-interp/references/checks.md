# Interpretability checks

## Hooks and patching
- Set the tolerance from repeated no-op forwards in the dtype and backend you use, then check that
  patching clean activations back in reproduces the clean output within it.
- Verify the hook fires, the shape, token alignment and padding, and include a known-effective
  positive control. A real null and a hook on the wrong module look the same without it.
- Say which ablation (zero, mean, resample) and why. Fit ablation statistics on a separate split.
- Minimal pairs: clean and corrupted prompts differ in one controlled token or fact, same length.
- Report raw clean, corrupted and patched scores. If you also report normalised recovery, fix the
  aggregation and a minimum clean-corrupted gap in advance, and count the undefined cases.
- Check attribution or path-patching approximations against exact activation patching on a sample.

## SAEs and transcoders
- Report: model, layer, site (resid, MLP out, attention out), width, L0, explained variance or
  FVU, delta LM loss (spliced versus clean, and versus zero-ablation), dead-latent share and its
  criterion, error-term mode, and the evaluation token count. For transcoders, both hook sites.
- Compare on the same activation source and evaluation tokens. Match width, sparsity and training
  budget for the claim you make, or report curves across operating points. Name differences in
  training resources.
- Reconstruction and downstream usefulness are different targets, and benchmark metrics (for
  example SAEBench) can disagree. Say which metric supports which claim.
- Check whether a latent fires on most tokens before calling it a feature.

## Feature interpretation
- Look at examples across the activation range, including weak activations, not only the top 20.
- Autointerp labels are hypotheses. Score them on held-out examples.
- Freeze the feature, intervention site and selection rule on discovery data, pick strengths and
  thresholds on validation data, and confirm once on unseen prompt families. Compare against a
  no-op and a matched-size random perturbation.
- Watch for feature splitting (one concept across several latents) and absorption (a general
  latent that stops firing when a more specific one takes over).

## Probes
- Baselines: majority class, a probe on a randomly initialised model, and a control task.
- Split by prompt template or source document, not only by row.
- Linear first. A probe that needs an MLP may be learning the task itself.
- For downstream detection, compare SAE-feature methods with a plain linear probe on the same data.

## Steering
- Sweep the coefficient; plot target effect and side effects (general capability, perplexity,
  refusal) together.
- Evaluate on held-out prompts. Report all generations or a random sample, never hand-picked ones.

## Scale
- n prompts, seeds where training is involved, and a spread for every number.
- Confirm a feature or circuit on prompts that played no part in finding it.

## Safety repair after fine-tuning
- Score the original, fine-tuned and repaired checkpoints with the same protocol on harmful and
  benign requests.
- Report unsafe compliance, benign over-refusal and retained task capability separately. A repair
  that refuses everything looks perfect on harmful prompts alone.
- Test against the attack that caused the drift and at least one adaptive variant.

## Added 2026-11-19 (cross-model review)

- Corruption and metric choice can move a circuit. Define the behaviour, counterfactual and primary
  metric before selection; check a second plausible corruption and metric when the interpretation
  depends on them. Report per-pair raw scores and discordant pairs.
- Attribution shortlists (AtP and friends): sample high, middle and low estimated effects plus known
  nonlinear cases, run exact patches blind to the estimate, report false negatives and sign errors.
- A heatmap is not a circuit. For a circuit claim compare the circuit alone, the circuit removed and
  size-matched controls, and test joint interventions where components may substitute for each other.
- Zero and mean ablations create out-of-distribution activations. Match controls by layer, token and
  norm; prefer resample ablation where appropriate; track side effects on unrelated logits.
- Feature labels: test labelled positives and hard negatives across activation quantiles and prompt
  families; report label precision and missed positives separately.
- Matching features across dictionaries: match on held-out activations and intervention behaviour;
  decoder similarity is a lead. Allow splits and absorption (many-to-one, unmatched).
- Probes: match capacity and tuning budget, add a bag-of-tokens or metadata baseline, label
  permutation and group-held-out transfer; claim use by the model only with an intervention.
- Steering: pre-declare the coefficient sweep; report target success, side effects, fluency and
  missing outputs; confirm the chosen coefficient once on fresh prompts.
- Caches: key on model, revision, dtype, hook, processing mode and input tokens; show a cache miss
  after a relevant change; scope hook lifetimes and re-check clean replay.
