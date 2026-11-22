# How to write skills that actually help

Researched 2026-11-21. Sources opened this session are linked inline.

## The answer

A skill helps when it gives the model knowledge or a workflow it does not already have, in a short,
focused file, and it is proven by a with-and-without test before anyone trusts it. In SkillsBench,
curated skills raised task pass rates by about 16 percentage points on average, but skills written by
a model showed no consistent benefit ([SkillsBench, arXiv 2602.12670](https://arxiv.org/abs/2602.12670);
[O'Reilly summary](https://oreilly.com/radar/agent-skills-work-but-the-research-shows-most-teams-are-building-them-wrong)).
Most of our library was written by Claude and reviewed by GPT, so that second number is the strongest
evidence against how we built it.

## What the evidence says

- **Focused beats complete.** SkillsBench found skills with at most three modules beat larger or
  exhaustive bundles. More coverage in one skill did not help.
- **Gains depend on the domain.** Software engineering tasks gained about 4.5 points; healthcare
  tasks gained about 52. Skills help most where the work follows strict conventions the base model
  does not know (O'Reilly summary of SkillsBench).
- **Only add what the model lacks.** Anthropic's guide says to challenge every paragraph: "Does
  Claude really need this explanation?" It also sets a 500-line ceiling for SKILL.md and says to
  keep reference files one level deep
  ([Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- **Write tests before the skill.** Anthropic calls this evaluation-driven development: run the
  model on real tasks with no skill, write down what goes wrong, then write only what fixes it.
- **A tie means retire.** Anthropic's skill-creator now runs blind with-and-without comparisons. If
  the pass rate is the same with and without, "the skill isn't broken; it's just no longer
  necessary" ([skill-creator post](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)).
- **The description decides whether it fires.** Too narrow and it never triggers; too broad and it
  fires on the wrong things. Tune it on a held-out set of should-fire and should-not-fire prompts
  ([Agent Skills: optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)).
  Write it in the third person.
- **Treat a skill as software.** One job per skill, the interface (description) separate from the
  body, low coupling between skills, and behaviour tests instead of exact-output tests
  ([Destefanis, arXiv 2607.25032](https://arxiv.org/abs/2607.25032)).
- **Big libraries collide.** As skill count grows, similar descriptions get confused at selection
  time (O'Reilly summary).

## What this means for our library

| Finding | Our library today | Change |
|---|---|---|
| Owner-specific knowledge helps; generic advice doesn't | `bro` and `learn-fast` encode your taste and won their tests. `writing` and `studio` mostly restate what Sonnet already does, and tied | Keep encoding your preferences. Cut generic advice. Retire a skill that keeps tying |
| Focused beats exhaustive | `research` has 171 lines and 18 helper files; `ml-experiment` 153 lines and 8 files | Split or trim the two big ones first |
| A skill that never fires can't help | In today's clean Sonnet run, `bro` didn't fire on "ok but tldr?" without the router hook | Tune descriptions on held-out prompts, so firing doesn't depend only on the hook |
| Tests before writing | Most skills were written first and tested after | For each new or changed skill, record the plain model's failures first |
| Model-written skills don't help on average | Ours were drafted by Claude and reviewed by GPT | Trust only measured wins. Prefer rules taken from your own corrections |

## Limits

SkillsBench version numbers and headline figures differ across its versions; check the latest arXiv
PDF before quoting exact numbers. The domain split (4.5 and 52 points) comes from the O'Reilly
write-up, which I read, not from the paper's table directly.
