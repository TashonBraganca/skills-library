# Preflight before an expensive run, and watching it while it runs

A run that dies at hour 9, or finishes "successfully" on the wrong data, costs more than every check
below combined. Run them on the real code path, at tiny scale, before spending the budget.

## Preflight (each line: check, expected result, what a failure usually means)

| Check | Expected | Failure usually means |
|---|---|---|
| Open one batch: shapes, dtypes, a decoded example, label distribution | What the plan says | Wrong file, wrong split, template or tokenizer mismatch |
| Loss at step 0 | Classification from scratch: about ln(classes). Fine-tune: the base model's known loss on this data | Wrong labels, wrong loss mask, double softmax |
| Overfit one small batch (32 to 64 items) | Training loss goes near zero within a few hundred steps | Broken gradients, frozen layers, LR far off, mask zeroes the loss |
| Step-0 eval through the frozen evaluator | Reproduces the baseline number in the plan within noise | The eval harness, parser or template differs from the baseline's |
| The smallest end-to-end dry run that exercises checkpoint save, reload and the eval | Completes; the reloaded checkpoint scores the same | Partial loads, resume resets the scheduler, eval cannot read the checkpoint |
| Throughput and utilisation (tokens or items per second, GPU memory, GPU busy %) | Matches the budget estimate | Data loader bottleneck, CPU-bound preprocessing, wrong batch size |
| Time and cost estimate: steps x seconds per step, plus eval time | Inside the budget with 20% margin | The plan must change before the run, not during it |
| Logging | Loss, LR, grad norm, tokens per second, eval metric, (RL) reward, KL, length, success, each per step or interval | You will not be able to tell a dead run from a slow one |
| Disk and memory headroom for all checkpoints and logs | Enough with margin | The run dies at the first big checkpoint |
| NaN and divergence guard | The run stops itself on NaN loss or a grad-norm spike over a set threshold | Hours of wasted compute after the run already broke |

Record each result in the plan's Pilot section. A failed preflight check is a plan change, not a
footnote.

## Watching a long run

- Check it is alive by evidence: the process exists, the log grows, the step counter advances, and
  the steps per minute match the preflight number. "Started" is not "running".
- Alarm lines to watch: loss NaN or flat, grad norm spikes, eval metric moving the wrong way, RL
  reward rising while independently scored success falls, response length running away, KL
  exploding or collapsing to zero.
- Never report a run as finished until its final checkpoint, logs and score records exist with sane
  sizes and fresh timestamps.

## Remote GPUs (the owner's RunPod)

- Never edit, move, overwrite or delete anything already on the pod (owner's hard rule). Upload new
  files only: a new run folder per run, new scripts beside the old ones.
- Write every output into that run's own folder. Pull results back (`rsync -avz runpod:<run>/ ./`)
  and run `guard.py` and `stats.py` locally on the pulled copy.
- Record the pod's GPU type, driver, CUDA, and package versions in the run manifest.
- The pod's address can change after a restart: "Connection refused" usually means that.
