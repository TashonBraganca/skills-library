# AI and ML field map

Starting points by subfield, checked 2026-11-19. They are where claims are owned and contested, not
a list of truths. Open the release, benchmark revision or code behind any claim you use, and add the
names you discover. `S=~/.skills-library/skills/research/scripts`.

## How to use it

1. Pick the subfield rows that own your claim.
2. Owner route: the lab index or repo that published it (`fetch.py <index> --links ...`).
3. People route: `papers.py author "<name>" --since 90d`, `social.py x search "<topic>" --from <handle> --since 90d`.
4. Venue route: `papers.py reviews "<title>"` for OpenReview venues, `social.py lesswrong "<topic>"`
   for alignment and interpretability debate.
5. Benchmark route: the benchmark owner's repo and methodology page, its version, its known
   contamination or saturation reports.

## Agentic AI and agent evaluation

- Owners: METR (time-horizon reports, task suites, human baselines), benchmark repos (SWE-bench,
  Terminal-Bench, OSWorld, tau-bench, MLE-bench, PaperBench, RE-Bench), UK AISI Inspect tasks.
- Integrity: ImpossibleBench (Zhong, Raghunathan, Carlini; arXiv 2510.20270) for test exploitation,
  OpenAI's SWE-bench Verified retirement note for contamination, RewardHackingAgents (2603.11337),
  "Beyond Execution" (2608.26753) and "Beyond fabrication" (2610.38691) for research-agent failures.
- Venues: ICLR and NeurIPS agent workshops, COLM, arXiv cs.AI, cs.SE.

## Post-training (SFT, preference training, RL for LLMs)

- Owners: Ai2 (OLMo and Tülu releases, open data and recipes), Hugging Face TRL docs and issues,
  vLLM and verl repos, Thinking Machines blog (inference numerics, LoRA studies), DeepSeek and Qwen
  technical reports, Nathan Lambert (Interconnects, RLHF book).
- Controls and pitfalls: Spurious Rewards (arXiv 2506.10947), "Reasoning or Memorization?"
  (2507.10532), "A Sober Look at Progress in LM Reasoning" (2504.07086), vLLM train-inference
  consistency reports.
- Venues: ICML, NeurIPS, COLM, ACL and EMNLP, TMLR. Small benchmarks (AIME, AMC, MATH-500) need
  many seeds; look for fresh held-out transfer.

## Alignment, control and model behaviour

- Owners: Anthropic Alignment Science blog (alignment.anthropic.com) and system cards, OpenAI
  safety and system cards, Google DeepMind safety papers, Apollo Research, Redwood Research (AI
  control), UK AISI, METR, MATS scholar outputs, Transluce, Goodfire.
- Debate and objections: Alignment Forum and LessWrong posts and comments, OpenReview safety
  workshops.
- Check: whether scenarios are synthetic, whether the model knows it is tested, the grader code and
  threat model, released transcripts.

## Mechanistic interpretability

- Owners: Transformer Circuits (transformer-circuits.pub), Google DeepMind Gemma Scope releases and
  cards, Neel Nanda and collaborators, EleutherAI, Goodfire, Transluce, Apollo interpretability.
- Tools and data: TransformerLens, SAELens, nnsight and their changelogs; Neuronpedia for released
  SAE features; SAEBench (arXiv 2503.09532) for multi-metric SAE comparison; activation patching
  best practices (Heimersheim and Nanda, arXiv 2404.15255).
- Venues: ICML and NeurIPS mechanistic interpretability workshops, Alignment Forum, OpenReview.

## Evaluation, benchmarks and LLM judges

- Owners: Stanford CRFM HELM, UK AISI Inspect, Hugging Face LightEval, Epoch AI (benchmark hubs and
  compute data), LMArena methodology posts, MT-Bench and judge studies (arXiv 2306.05685).
- Check: dataset hash and revision, parser fixtures, judge validation against humans, order and
  length bias, model version drift.

## General discovery

- Hugging Face daily papers (`papers.py hf --daily`), arXiv listings (cs.LG, cs.CL, cs.AI, cs.CR),
  Semantic Scholar recommendations (`papers.py similar <anchor>`), alphaXiv discussions, GitHub
  trending for implementations, Kaggle competition write-ups for what wins in practice.
- paperswithcode.com now redirects to Hugging Face trending papers; its old leaderboards are not a current state-of-the-art source.
