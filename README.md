# skills-library

Agent skills for Claude Code, Codex and Cursor, installed from one source into every tool with a
single command.

## Install

```bash
npx github:tashonbraganca/skills-library
```

Clones into `~/.skills-library`, fetches the third-party skill repos this vendors, then symlinks
everything into whichever of `~/.claude-work`, `~/.claude-personal`, `~/.codex` and
`~/.cursor` exist on the machine. Safe to re-run: it updates in place and unlinks anything removed
from `skills.txt`.

## What's here

Auto-loaded: `research` (deep cited research with scripts for papers, citations, reviews, Reddit,
X, HN, YouTube, LessWrong and more), `social-search`, `grilling`, `ml-experiment` (with `guard.py`),
`ml-interp`, `studio` (conductor for the per-project web, 3d and video packs), `learn-fast`,
`writing` (drafting guide, humanizer from blader/humanizer, MIT, and ASD-STE100), `bro` (plain
restatements), `wayfinder` (one map of a long project), `gtm`, `find-buyers` and `diagnosing-bugs`
(mattpocock/skills, MIT).

Manual (no context cost until typed): `improve-skill`, `second-opinion`,
`improve-codebase-architecture` (forked from mattpocock/skills).

## Hooks make the skills fire

Without help, a skill rarely fires: in clean headless tests, Sonnet skipped `research` even on
prompts that began "Research whether...". So `install.sh` wires these hooks into every Claude Code
profile and into Codex:

| Hook | What it does |
|---|---|
| `skill_router.py` | Matches the prompt and tells the agent which skill to invoke (12 auto skills; adds `wayfinder` in long sessions) |
| `grill_gate.py` | Adds the `grilling` rules to build, plan and research prompts |
| `prose_gate.py` | Checks replies and prose files for AI tells; long replies must open with a plain summary |
| `subagent_gate.py` | Blocks a subagent unless the owner approved it in their latest message |
| `social_fetch_guard.py` | Sends Reddit, X and YouTube lookups to `social-search` instead of a raw fetch |

Tests sit beside each hook (`hooks/test_*.py`). Codex runs a hook only after you trust it: start
`codex`, type `/hooks`, and trust the four hooks listed there.

Per-project packs (`packs/`) pin third-party skills (impeccable, taste-skill, Emil Kowalski's
skills, GSAP, three.js, Remotion, HyperFrames, Corey Haines' marketing skills, ML writing and eval
skills) to exact commits and link them only into the projects that need them.

`skills.txt` is the manifest and the single source of truth for what installs. Edit it, re-run
`./install.sh`, and anything removed gets unlinked everywhere.

## Structure

```
skills/            skills authored in this repo
vendor/             gitignored; cloned on first run, not committed
commands/           generated slash-command wrapper per installed skill
hooks/              the hooks above, with their tests
install.sh          reads skills.txt, links + prunes across every tool it finds
bin/cli.mjs         the npx entry point
```

## License

MIT for everything authored here. `LICENSE-THIRD-PARTY.md` covers the absorbed material from Emil
Kowalski's skills.
