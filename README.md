# skills-library

Agent skills for Claude Code, Codex and Cursor, installed from one source into every tool with a
single command.

## Install

```bash
npx github:tashonbraganca/skills-library
```

Clones into `~/.skills-library`, fetches the third-party skill repos this vendors, then symlinks
everything into whichever of `~/.claude`, `~/.claude-work`, `~/.claude-personal`, `~/.codex` and
`~/.cursor` exist on the machine. Safe to re-run: it updates in place and unlinks anything removed
from `skills.txt`.

## What's here

Two design skills built from measurement, not taste: `design-craft` derives its colour rule from
scoring ten generated pages against a real reviewer's verdicts, and its motion technique from Emil
Kowalski's `apple-design` and `emil-design-eng` (MIT). `design-review` judges existing UI against ten
motion standards. `research`, `grilling`, `working-with-agents` and `improve-skill` are original.
`wayfinder` and `wizard` come from mattpocock/skills; the rest of the process skills (debugging,
TDD, plans, worktrees, code review) come from obra/superpowers.

`skills.txt` is the manifest and the single source of truth for what installs. Edit it, re-run
`./install.sh`, and anything removed gets unlinked everywhere.

## Structure

```
skills/            skills authored in this repo
vendor/             gitignored; cloned on first run, not committed
commands/           generated slash-command wrapper per installed skill
install.sh          reads skills.txt, links + prunes across every tool it finds
bin/cli.mjs         the npx entry point
```

## License

MIT for everything authored here. `LICENSE-THIRD-PARTY.md` covers the absorbed material from Emil
Kowalski's skills.
