# Current APIs (checked 2026-11-19)

Versions on that date: transformer-lens 4.4.0, sae-lens 6.55.5, nnsight 0.8.2. Each section names
its source. If your installed version differs, re-check that source before relying on a snippet.

## TransformerLens 4

Source: PyPI README and https://TransformerLensOrg.github.io/TransformerLens/content/migrating_to_v4.html

```python
from transformer_lens.model_bridge import TransformerBridge

bridge = TransformerBridge.boot_transformers("gpt2", device="cpu")
logits, activations = bridge.run_with_cache("Hello World")
```

Legacy default processing (to compare with numbers from HookedTransformer-era papers):

```python
model = TransformerBridge.boot_transformers("gpt2")
model.enable_compatibility_mode()  # LayerNorm folding, center_writing_weights, center_unembed
```

- Removed in 4.0: `HookedTransformer`, `HookedEncoder`, `HookedEncoderDecoder`,
  `HookedTransformerConfig`, `transformer_lens.utils`, `.loading`, `.components`, `.train`,
  `.pretrained`. Importing one raises an `ImportError` naming the replacement.
- Without compatibility mode, weights such as `W_pos` are raw Hugging Face weights.
- `hasattr` on a removed name raises instead of returning False.
- Compatibility mode reproduces legacy default processing on supported architectures. It does not
  reproduce a paper's checkpoint, tokenizer, dtype or preprocessing; match those and compare
  reference activations.
- Hook names: the 4.0 guide defers to the 3.0 migration guide and the model-structure docs
  (legacy alias table). Resolve each alias there, and confirm the hook fires with a smoke test.
  Listing hook names does not show that a hook fires.
- Gated models (Llama, Gemma, Mistral) need `HF_TOKEN`.
- Old code that imports `HookedTransformer` needs the version it was written for; pin it exactly.

## SAELens 6

Source: https://decoderesearch.github.io/SAELens/latest/migrating/

- `SAE.from_pretrained(...)` returns the SAE.
- `SAE.load_from_pretrained_with_cfg_and_sparsity(...)` returns the old (sae, cfg, sparsity) tuple.
- Training: nested runner config with `sae=StandardTrainingSAEConfig(...)` (or
  `JumpReLUTrainingSAEConfig`, `TopKTrainingSAEConfig`, `GatedTrainingSAEConfig`) and
  `logger=LoggingConfig(...)`. JumpReLU uses `l0_coefficient`; TopK sets `k` directly.
  Default JumpReLU bandwidth is 0.05 and starting threshold 0.01 (changed from 0.001).
- `SAETrainingRunner` is now `LanguageModelSAETrainingRunner`. CLI:
  `python -m sae_lens.llm_sae_training_runner`.
- Pretrained release ids: https://decoderesearch.github.io/SAELens/latest/pretrained_saes/
- Attaching SAEs to a TransformerLens 4 model (source: https://decoderesearch.github.io/SAELens/latest/usage/,
  "Using SAETransformerBridge"; `HookedSAETransformer` requires `transformer-lens<4.0`):

```python
from sae_lens import SAE, SAETransformerBridge

model = SAETransformerBridge.boot_transformers("google/gemma-3-4b-it", device="cuda")
sae = SAE.from_pretrained(release="gemma-scope-2-4b-it-res",
                          sae_id="layer_17_width_16k_l0_medium", device="cuda")
logits, cache = model.run_with_cache_with_saes("A public smoke-test prompt.", saes=[sae])
# model.add_sae(sae) attaches permanently; model.reset_saes() removes it. A forgotten permanent
# attachment contaminates the next baseline.
```

- Gemma Scope 2 release ids for Gemma 3 4B IT (source: SAELens pretrained list,
  https://decoderesearch.github.io/SAELens/latest/pretrained_saes/google_gemma-3-4b-it/):
  `gemma-scope-2-4b-it-res`, `-mlp`, `-att`, `-transcoders`, each also with an `-all` variant.
  Example: `layer_17_width_16k_l0_medium` in `-res` hooks `blocks.17.hook_resid_post`. Other model
  sizes have their own pages. Use the instruction-tuned model with `-it` releases.
- For a transcoder, check both its input and output hook sites.

## nnsight 0.8

Source: PyPI README (https://github.com/ndif-team/nnsight)

```python
with model.trace("The Eiffel Tower is in the city of"):
    model.transformer.h[0].output[:] = 0          # intervene
    hidden = model.transformer.h[6].output.save()  # keep a value after the block
    logits = model.output.logits.save()
```

- Export values with `x = value.save()` or `x = nnsight.save(value)` inside the trace.
- Output types change with the `transformers` version: the README says a GPT-2 block's `.output`
  is a plain tensor in current versions while attention returns a tuple. On a tensor, `[0]` selects
  the first batch row instead of the hidden state. Print the type and shape inside a trace before
  indexing. `print(model)` shows structure, not runtime shapes.
- Generation: `with model.generate(prompt, max_new_tokens=3) as tracer: ids = tracer.result.save()`;
  step through tokens with `tracer.iter[:n]`.
- Batching: `with model.trace() as tracer:` then one `with tracer.invoke(prompt):` per prompt;
  each invoke sees only its own rows.
- `remote=True` runs the trace on NDIF, which receives your trace code and inputs. Send only
  inputs you are allowed to share, on a hosted checkpoint.
