#!/usr/bin/env python3
"""Force the writing skill's mechanical checks everywhere in Claude Code (owner, 2026-11-19: "the
writing skill needs to be forced and globally used in the Claude sessions always").

  --stop       Stop hook: checks the final reply of the turn with prose_check.py. HARD flags (dashes,
               curly quotes, chatbot residue) block the stop once, with the flags as the reason, so the
               agent rewrites. stop_hook_active (already retried) lets it finish, never loops.
  --post-tool  PostToolUse hook on Write|Edit|MultiEdit: a prose file for people (.md .mdx .txt .rst
               .html) that has HARD flags gets them fed back to the agent to fix. Agent-instruction
               files (SKILL.md, CLAUDE.md, AGENTS.md, anything under skills/, .claude/, .codex/,
               commands/, references/) and code are skipped: the humanize pass does not apply to them.

Never crashes the session: bad input exits 0 silently.
"""
import json
import os
import re
import subprocess
import sys

CHECK = os.path.expanduser("~/.skills-library/skills/writing/scripts/prose_check.py")
PROSE_EXT = (".md", ".mdx", ".txt", ".rst", ".html", ".htm")
AGENT_FILES = {"skill.md", "claude.md", "agents.md", "gemini.md"}
HARNESS = ("<system-reminder>", "<task-notification>", "[SYSTEM NOTIFICATION", "<command-name>", "<local-command", "Caveat:")
AGENT_DIRS = ("/skills/", "/templates/", "/.claude", "/.codex/", "/commands/", "/references/", "/.agents/", "/hooks/")


def hard_flags(text, html=False):
    if not text.strip():
        return []
    args = [sys.executable, CHECK, "-", "--json"] + (["--html"] if html else [])
    try:
        p = subprocess.run(args, input=text, capture_output=True, text=True, timeout=20)
        return json.loads(p.stdout)["flags"]["hard"] if p.stdout.strip() else []
    except (subprocess.SubprocessError, ValueError, KeyError, OSError):
        return []


def last_reply(transcript_path):
    try:
        rows = [json.loads(l) for l in open(transcript_path, encoding="utf-8") if l.strip()]
    except (OSError, TypeError, ValueError):
        return ""
    parts = []
    for row in reversed(rows):
        msg = row.get("message") or {}
        content = msg.get("content")
        if row.get("type") == "user" and not row.get("isMeta") and not (isinstance(content, list) and any(
                isinstance(b, dict) and b.get("type") == "tool_result" for b in content)):
            text = content if isinstance(content, str) else " ".join(
                b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")
            if text.strip() and not text.lstrip().startswith(HARNESS):
                break  # reached the owner's message: the turn's reply is everything after it
        if row.get("type") == "assistant" and isinstance(content, list):
            texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
            if texts and not parts:
                parts = texts  # the final text block(s) of the turn are what the owner reads last
    return "\n".join(parts)


def turn_info(transcript_path):
    """(owner's last message, skills invoked since it) for the turn that is ending."""
    try:
        rows = [json.loads(l) for l in open(transcript_path, encoding="utf-8") if l.strip()]
    except (OSError, TypeError, ValueError):
        return "", set()
    skills = set()
    for row in reversed(rows):
        content = (row.get("message") or {}).get("content")
        if row.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill":
                    skills.add(str((b.get("input") or {}).get("skill", "")).split(":")[-1])
        if row.get("type") == "user" and not row.get("isMeta") and not (isinstance(content, list) and any(
                isinstance(b, dict) and b.get("type") == "tool_result" for b in content)):
            text = content if isinstance(content, str) else " ".join(
                b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")
            if text.strip() and not text.lstrip().startswith(HARNESS):
                return text, skills
    return "", skills


def learning_gap(transcript_path, reply):
    """Owner's rule (2026-11-20): whenever the owner wants to learn something, learn-fast AND writing both run."""
    if len(reply or "") < 400:
        return None  # a one-line definition or quick fact needs neither
    owner, skills = turn_info(transcript_path)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from skill_router import route
        wants_learning = "learn-fast" in route(owner)
    except Exception:
        wants_learning = False
    if not (wants_learning or "learn-fast" in skills):
        return None
    missing = [s for s in ("learn-fast", "writing") if s not in skills]
    return missing or None


def summary(flags):
    return "; ".join(f"line {f['line']}: {f['kind']} ({f['text'][:50]})" for f in flags[:8])


# Every Stop block forces a second message under the first, and that is what the reader ends up with.
# So each block reason demands the whole reply again; without this the model wrote a short summary.
FULL_RESEND = (" The reader treats your next message as the answer, so send the complete reply again at full "
               "length: every section, list, table, code block, number and caveat. Do not summarize, shorten or "
               "condense it, and do not mention this check.")
def stop(data):
    if data.get("stop_hook_active"):
        return 0
    reply = data.get("last_assistant_message")  # Codex passes the reply; Claude Code needs the transcript
    reply = reply if isinstance(reply, str) else last_reply(data.get("transcript_path"))
    flags = hard_flags(reply)
    if flags:
        print(json.dumps({"decision": "block", "reason":
              "Writing gate (owner's rule): your final reply has AI tells the writing skill bans: " + summary(flags) +
              ". Rewrite the reply without them (no em or en dashes, straight quotes, no chatbot phrases). "
              "Keep every fact and number." + FULL_RESEND}))
    elif not isinstance(data.get("last_assistant_message"), str) and learning_gap(data.get("transcript_path"), reply):
        missing = learning_gap(data.get("transcript_path"), reply)
        print(json.dumps({"decision": "block", "reason":
              "Learning rule (owner's): when the owner wants to learn something, both learn-fast and writing must run. "
              f"Not run this turn: {', '.join(missing)}. Invoke {' and '.join(missing)} with the Skill tool now, apply "
              "them to the explanation (step ladder, plain fun English, prose_check.py on the page), then give the explanation in full." + FULL_RESEND}))
    return 0


def post_tool(data):
    ti = data.get("tool_input") or {}
    cmd = str(ti.get("command") or "")
    if "*** Begin Patch" in cmd:  # Codex apply_patch: check every added or updated file
        rc = 0
        for path in re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", cmd, re.M):
            full = path if os.path.isabs(path) else os.path.join(data.get("cwd") or "", path)
            rc = post_tool({"tool_input": {"file_path": full}}) or rc
        return rc
    path = str(ti.get("file_path") or "")
    low = path.lower()
    if not low.endswith(PROSE_EXT) or os.path.basename(low) in AGENT_FILES or any(d in low for d in AGENT_DIRS):
        return 0
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return 0
    flags = hard_flags(text, html=low.endswith((".html", ".htm")))
    if flags:
        print(json.dumps({"decision": "block", "reason":
              f"Writing gate: {os.path.basename(path)} has AI tells: {summary(flags)}. Fix them in editable prose "
              "(verbatim quotes, titles and code stay as they are; say so if one of these is a literal). "
              "For a full pass use the writing skill.",
              "hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
    return 0


def main():
    if os.environ.get("SKILL_HOOKS_OFF") == "1":  # the skills-off arm of a paired test
        return 0
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if "--stop" in sys.argv:
        return stop(data)
    if "--post-tool" in sys.argv:
        return post_tool(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
