#!/usr/bin/env python3
"""Smoke test before any interpretability run: does the hook do what you think, on this install?

  python smoke.py --model gpt2 --layer 6
  python smoke.py --model gpt2 --clean "The Eiffel Tower is in the city of" --corrupt "The Colosseum is in the city of" \
                  --clean-target " Paris" --corrupt-target " Rome" --layer 8

Runs with TransformerLens 4 (TransformerBridge, raw Hugging Face numerics) and checks, in order:
  1. versions        transformer-lens, transformers and torch as installed in this interpreter
  2. reference       bridge logits match a plain Hugging Face forward pass on the same tokens
  3. hook fires      blocks.L.hook_resid_post is called exactly once per forward, with the expected shape
  4. no-op           a hook that returns its input leaves the logits unchanged
  5. clean replay    patching every clean resid_post at layer L into the corrupt run reproduces the clean logits
  6. positive ctrl   patching the clean activation at the last position only moves the logit difference
                     (clean target minus corrupt target) toward the clean answer
Expected before running: 2 to 5 pass to float tolerance; 6 moves in the predicted direction for a
layer in the second half of a small model. A failure means fix the setup before reading any effect.
Exit 0 all pass, 1 a check failed, 2 bad input (for example prompts of different token length).
"""
import argparse
import sys
from importlib.metadata import version


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="gpt2")
    ap.add_argument("--layer", type=int, default=8)
    ap.add_argument("--clean", default="The Eiffel Tower is in the city of")
    ap.add_argument("--corrupt", default="The Colosseum is in the city of")
    ap.add_argument("--clean-target", default=" Paris")
    ap.add_argument("--corrupt-target", default=" Rome")
    ap.add_argument("--tol", type=float, default=1e-3)
    ap.add_argument("--eps", type=float, default=0.1, help="minimum logit-difference movement for the positive control")
    a = ap.parse_args()

    import torch
    from transformer_lens.model_bridge import TransformerBridge
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print("1. versions:", {p: version(p) for p in ("transformer-lens", "transformers", "torch")})
    torch.manual_seed(0)
    m = TransformerBridge.boot_transformers(a.model, device="cpu")
    tok = AutoTokenizer.from_pretrained(a.model)
    clean = m.to_tokens(a.clean)
    corrupt = m.to_tokens(a.corrupt)
    if clean.shape != corrupt.shape:
        print(f"INPUT ERROR: clean and corrupt prompts tokenize to {clean.shape[-1]} and {corrupt.shape[-1]} tokens; "
              "align them by token span before patching")
        return 2
    t_clean = tok.encode(a.clean_target)
    t_corrupt = tok.encode(a.corrupt_target)
    if len(t_clean) != 1 or len(t_corrupt) != 1:
        print("INPUT ERROR: each target must be a single token for this check")
        return 2
    t_clean, t_corrupt = t_clean[0], t_corrupt[0]
    n_layers = getattr(m.cfg, "n_layers", None)
    if n_layers is not None and not 0 <= a.layer < n_layers:
        print(f"INPUT ERROR: --layer {a.layer} outside 0..{n_layers - 1}")
        return 2
    site = f"blocks.{a.layer}.hook_resid_post"
    ok = True

    def report(name, passed, detail):
        nonlocal ok
        ok &= passed
        print(f"{name}: {'PASS' if passed else 'FAIL'} ({detail})")

    with torch.no_grad():
        logits_clean = m(clean)
        hf = AutoModelForCausalLM.from_pretrained(a.model).eval()
        ref = hf(clean).logits
        d = (logits_clean - ref).abs().max().item()
        report("2. reference", d < a.tol, f"max |bridge - HF| = {d:.2e}")

        calls = []

        def count(x, hook):
            calls.append(tuple(x.shape))
            return x
        m.run_with_hooks(clean, fwd_hooks=[(site, count)])
        report("3. hook fires", len(calls) == 1 and calls[0][:2] == tuple(clean.shape),
               f"{site} called {len(calls)}x, shape {calls[0] if calls else None}")

        noop = m.run_with_hooks(clean, fwd_hooks=[(site, lambda x, hook: x)])
        d = (noop - logits_clean).abs().max().item()
        report("4. no-op", d < a.tol, f"max change {d:.2e}")

        _, cache = m.run_with_cache(clean, names_filter=lambda n: n == site)
        clean_act = cache[site]
        replay = m.run_with_hooks(corrupt, fwd_hooks=[(site, lambda x, hook: clean_act)])
        d = (replay[:, -1] - logits_clean[:, -1]).abs().max().item()
        report("5. clean replay", d < a.tol, f"last-position max |patched - clean| = {d:.2e}")

        logits_corrupt = m(corrupt)
        diff = lambda lg: (lg[0, -1, t_clean] - lg[0, -1, t_corrupt]).item()

        def patch_last(x, hook):
            x = x.clone()
            x[:, -1] = clean_act[:, -1]
            return x
        patched = m.run_with_hooks(corrupt, fwd_hooks=[(site, patch_last)])
        base, moved, target = diff(logits_corrupt), diff(patched), diff(logits_clean)
        eps = a.eps
        toward = (moved - base) * (1 if target > base else -1) > eps
        closer = abs(moved - target) < abs(base - target) - eps
        report("6. positive ctrl", target - base > eps and toward and closer,
               f"logit diff corrupt {base:.2f} -> patched {moved:.2f} (clean {target:.2f}); needs clean above corrupt, "
               f"a move toward clean and ending closer to clean, each by > {eps}")
    print("ALL PASS: the hook point behaves as expected on this install" if ok else
          "FAILED: fix the setup before interpreting any effect")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
