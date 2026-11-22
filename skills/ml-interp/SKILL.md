---
name: ml-interp
description: Mechanistic interpretability on transformer models with TransformerLens, SAELens and nnsight. Use for "activation patching", "SAE", "steering vector", "probe", "circuit", "Gemma Scope", activations, hooks, activation patching, attribution, ablations, sparse autoencoders and transcoders (loading, training, evaluating), probes, steering vectors, circuits, Gemma Scope, safety repair analysis, and any claim about what a model's internals do. Pairs with ml-experiment for training and decision-grade evaluation, and research for the literature. Not for general ML training questions (ml-experiment) or reading papers (research).
---

# Mechanistic interpretability

Core: verify the actual hook site, model revision, runtime and token positions before any claim;
the gpt2 smoke fixture checks the installation, not your site.

Two failures dominate: code written from memory against an API that changed, and interpretability
claims that were never tested causally.

## 1. Code against the installed versions

- In the interpreter that will run the code, read the installed versions:
  `python3 -c "from importlib.metadata import version as v; print([v(p) for p in ('transformer-lens','sae-lens','nnsight','transformers')])"`
  (drop the packages you do not use).
- Open the matching docs or tagged source for every call you have not used in this version. Start
  at `references/api.md`, which records what changed and where each fact came from.
- The changes that break remembered code (checked 2026-11-19):
  - TransformerLens 4 removed `HookedTransformer` and the other `Hooked*` model classes. Use
    `TransformerBridge.boot_transformers(...)`. Its default numerics are raw Hugging Face weights;
    `enable_compatibility_mode()` restores legacy default processing.
  - SAELens: `HookedSAETransformer` needs `transformer-lens<4`. With TransformerLens 4 use
    `SAETransformerBridge`. `SAE.from_pretrained(...)` returns the SAE only.
  - nnsight: export values from a trace with `.save()` or `nnsight.save(...)`. Module outputs can be
    a tensor or a tuple depending on the module and the `transformers` version.
- Never fix an import error by guessing another name. Read the migration guide.
- DeepWiki (MCP) answers repo questions fast but can lag releases: on 2026-11-19 it described
  TransformerLens "3.x" behaviour that 4.4 had removed. Confirm every API fact against the installed
  version or tagged source.

## 2. Smoke test before any real run

Run the fixture first, in the interpreter that will run the work (it needs `transformer-lens>=4`;
a tested environment lives at `~/.cache/skills-interp-venv/bin/python`):
`python ~/.skills-library/skills/ml-interp/scripts/smoke.py --model <model> --layer <L> --clean "<prompt>" --corrupt "<prompt>" --clean-target "<tok>" --corrupt-target "<tok>"`.
It checks the bridge against a plain Hugging Face forward, that the hook fires once with the right
shape, a no-op, clean replay, and a directional positive control (checked 2026-11-19 on gpt2:
all pass; swapped targets fail as they should). Exit 1 means fix the setup before reading any effect.
For other sites or libraries, apply the same five checks by hand:

On a public or synthetic prompt: match a plain Hugging Face forward pass, confirm the hook fires
the expected number of times at the named site (module, layer, pass, generation step) and print the
tensor's type, shape, dtype and axes. Print the rendered token ids with the attention mask and the
positions you will patch; align on token spans, never on characters. Run a no-op intervention (no
change), then a known positive intervention that must move the target in the predicted direction,
and confirm that patching clean activations back in reproduces the clean output. For SAEs, check that
the latent cache has `d_sae` columns and that the spliced model's loss is in a sane range. Label
anything before the full checks as exploratory.

## 3. Before interpreting a result

Use `references/checks.md` for the controls and report fields of each method (patching, SAEs and
transcoders, feature interpretation, probes, steering, safety repair). The rules that matter most:

- Verify hook firing, alignment and clean replay, and include a positive control, before reading
  a null or an effect.
- Report raw clean, corrupted and patched scores. Normalised recovery needs a minimum baseline gap.
- Compare SAE architectures on the same activations and tokens, across operating points or at
  matched width and sparsity. Reconstruction and downstream usefulness are different targets.
- A feature label is a hypothesis until an ablation or steering effect beats a matched control on
  prompts that played no part in finding it.
- Compare SAE-based detection with a plain linear probe on the same data.

- Before choosing a method for a decision-grade question (patching variant, attribution method,
  SAE or transcoder family, probe type), run `~/.skills-library/skills/ml-experiment/references/method-scan.md`: the
  incumbent, a task-only query, and the newest compatible method, compared on a matched pilot.
- For SAE interventions, report base, clean splice, splice with the declared error-term handling,
  a size-matched random-feature control and the intervention itself.
- Selecting features from thousands of latents is a search: freeze the search space and rule, keep
  discovery, validation and confirmation prompts in separate families, and report the search size.

Training runs and decision-grade evaluations go through `ml-experiment`.

## 4. Report

Separate causal results (effect sizes with n and spread) from correlational ones. Give model,
layer, site, hook name, library versions and numerics mode. State the strongest alternative
explanation.
