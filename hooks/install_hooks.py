#!/usr/bin/env python3
"""Install grill_gate, social_fetch_guard and subagent_gate into Claude Code profiles; grill_gate into Codex.

Idempotent. Backs up each settings file once as <name>.bak-2026-11-18, adds
entries only if the script path is not already in a hook command, keeps every
other key, re-loads the result to confirm valid JSON. Never deletes anything.
Usage: install_hooks.py [--dry-run]
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRILL = str(HERE / "grill_gate.py")
GUARD = str(HERE / "social_fetch_guard.py")
SUBAGENT = str(HERE / "subagent_gate.py")
ROUTER = str(HERE / "skill_router.py")
PROSE = str(HERE / "prose_gate.py")
SUBAGENT_MATCHER = "Agent|Task|Workflow|mcp__t3-code__delegate_task"
EXTRA_ARGS = {SUBAGENT: " --hook"}
PROSE_STOP, PROSE_POST = PROSE + " --stop", PROSE + " --post-tool"
BACKUP_SUFFIX = ".bak-2026-11-18"
HOME = Path.home()

CLAUDE_PROFILES = [".claude-work", ".claude-personal", ".claude-personal-mind"]
CODEX_HOOKS = HOME / ".codex" / "hooks.json"

DRY = "--dry-run" in sys.argv


def has_command(groups, script):
    for g in groups:
        for h in g.get("hooks", []):
            if script in (h.get("command") or ""):
                return True
    return False


def add_entry(doc, event, script, matcher=None, status=None, timeout=10):
    hooks = doc.setdefault("hooks", {})
    groups = hooks.setdefault(event, [])
    if has_command(groups, script):
        return False
    handler = {"type": "command", "command": f"python3 {script}{EXTRA_ARGS.get(script, '')}", "timeout": timeout}
    if status:
        handler["statusMessage"] = status
    group = {"hooks": [handler]}
    if matcher:
        group = {"matcher": matcher, **group}
    groups.append(group)
    return True


def process(path, wants):
    """wants: list of (event, script, matcher, status). Returns summary string."""
    notes = []
    if path.exists():
        bak = path.with_name(path.name + BACKUP_SUFFIX)
        if not bak.exists():
            if not DRY:
                shutil.copy2(path, bak)
            notes.append("backup made")
        else:
            notes.append("backup already existed")
        doc = json.loads(path.read_text(encoding="utf-8"))
    else:
        doc = {}
        notes.append("file did not exist, creating")
    before_keys = {k: json.dumps(v, sort_keys=True) for k, v in doc.items() if k != "hooks"}
    added = []
    for event, script, matcher, status in wants:
        if add_entry(doc, event, script, matcher, status):
            added.append(f"{event}:{Path(script).name}")
    if added and not DRY:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        re = json.loads(path.read_text(encoding="utf-8"))
        after_keys = {k: json.dumps(v, sort_keys=True) for k, v in re.items() if k != "hooks"}
        assert before_keys == after_keys, "non-hook keys changed"
        for event, script, _, _ in wants:
            assert has_command(re["hooks"][event], script), f"{event} missing after write"
        notes.append("rewritten, re-load OK")
    perms = doc.get("permissions", {}).get("allow", [])
    wf = [a for a in perms if "WebFetch" in a]
    if wf:
        notes.append(f"WARNING permissions.allow has WebFetch entries: {wf}")
    return f"{path}: added={added or 'nothing (already present)'}; " + "; ".join(notes)


DEFAULT_RULES = str(HOME / ".claude" / "CLAUDE.md")


def exclude_default_rules(path):
    """~/.claude/CLAUDE.md also loads as a parent-folder project file in every session under ~, so a non-default
    profile would read the global rules twice (once as its own CLAUDE.md, once from ~/.claude). Exclude it there."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    ex = doc.setdefault("claudeMdExcludes", [])
    if DEFAULT_RULES in ex:
        return f"{path}: claudeMdExcludes already set"
    if not DRY:
        ex.append(DEFAULT_RULES)
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        assert DEFAULT_RULES in json.loads(path.read_text(encoding="utf-8"))["claudeMdExcludes"]
    return f"{path}: claudeMdExcludes += {DEFAULT_RULES}"


def main():
    for prof in CLAUDE_PROFILES:
        if (HOME / prof / "settings.json").exists():
            print(exclude_default_rules(HOME / prof / "settings.json"))
        p = HOME / prof / "settings.json"
        if not p.exists():
            print(f"{p}: missing, skipped")
            continue
        print(process(p, [
            ("UserPromptSubmit", GRILL, None, "Checking whether to grill"),
            ("UserPromptSubmit", ROUTER, None, "Routing to a skill"),
            ("PreToolUse", GUARD, "WebFetch", None),
            ("PreToolUse", SUBAGENT, SUBAGENT_MATCHER, None),
            ("Stop", PROSE_STOP, None, None),
            ("PostToolUse", PROSE_POST, "Write|Edit|MultiEdit", None),
        ]))
    print(process(CODEX_HOOKS, [
        ("UserPromptSubmit", GRILL, None, "Checking whether to grill"),
        ("UserPromptSubmit", ROUTER, None, "Routing to a skill"),
        ("PreToolUse", SUBAGENT, "spawn_agent|Agent", None),
        ("Stop", PROSE_STOP, None, None),
        ("PostToolUse", PROSE_POST, "apply_patch|Edit|Write", None),
    ]))
    print("Codex: hooks need review and trust. Run codex, then /hooks, and trust grill_gate.py, skill_router.py, subagent_gate.py and prose_gate.py.")


if __name__ == "__main__":
    main()
