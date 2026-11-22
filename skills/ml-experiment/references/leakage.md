# Leakage review

The first eight rows follow Kapoor and Narayanan's leakage taxonomy ("Leakage and the
reproducibility crisis in ML-based science", arXiv 2207.07048; type names quoted verbatim). Their
reproduction result concerns the papers in their civil-war prediction review. The LLM rows below
are additions for this owner's work.

Mark each row in the plan: ruled out (say how), possible, or present.

| Code | Type | What it looks like | How to check |
|---|---|---|---|
| L1.1 | No test set | Training and evaluating on the same data. | Confirm a separate held-out file exists and the eval script reads only it. |
| L1.2 | Pre-processing on training and test set | Normalisation, imputation, tokenizer training, over or under sampling fit on all data. | Fit every transform on train only; read the code path, not the comment. |
| L1.3 | Feature selection on training and test set | Choosing features, layers, SAE latents or probe directions using the test set. | Selection uses a validation split. Re-run selection without the test set and compare. |
| L1.4 | Duplicates in datasets | The same or near-same item in train and test. | `guard.py overlap` (ids, normalised content, 13-gram near-duplicates). |
| L2 | Model uses features that are not legitimate | A feature that would not exist at prediction time, or encodes the label. | For each input, ask whether it exists when the model is used for real. |
| L3.1 | Temporal leakage | Test data earlier than training data for a claim about the future. | Split by time; check max(train date) < min(test date). |
| L3.2 | Nonindependence between train and test samples | Same user, document, repo, patient or prompt template on both sides. | Split by the unit the claim is about; check that unit's overlap. |
| L3.3 | Sampling bias in test distribution | Test set does not match the distribution the claim is about. | State the target distribution and how the test set was drawn from it. |

## LLM and post-training additions

| Type | What it looks like | How to check |
|---|---|---|
| Benchmark contamination | Eval items in pretraining, fine-tuning or derived data. | Trace dataset and artifact lineage. Run `guard.py overlap` on every materialised input and derived dataset. Record unavailable lineage as unknown, and use a private or newer confirmation set where contamination would change the claim. |
| Method built from the test set | A safety vector, steering direction or repair set built from the benchmark used to score it. | Trace where every artifact's data came from; overlap check against it. |
| Tuning on the test set | Checkpoint, prompt template, decoding settings or threshold chosen by test score. | Every choice made on a validation split; log which split each choice used. |
| Judge leakage | The candidate influences the rubric or judge instructions, or judge calibration used final items. | Freeze the judge and rubric, delimit candidate output, allow references only when the protocol calls for them, and check agreement and prompt-injection sensitivity on separate labelled cases. |
| Evaluator tampering | Agent edits the metric, the eval script or the labels. | Score with `guard.py score` from a snapshot outside the agent's write access; bind the score to the candidate and evaluator digests. |
| Shortcut artifacts | Downloading a finished model, reading answers from the web, using found credentials. | Sandbox the run; no network to model hubs during a "train it yourself" task; no unapproved keys. |
| Selection over seeds or runs | Reporting the best of N runs as the result. | Report all runs, or the pre-registered selection rule, with the spread. |
