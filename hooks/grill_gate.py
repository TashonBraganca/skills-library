#!/usr/bin/env python3
"""UserPromptSubmit hook for Claude Code and Codex.

Reads the hook JSON on stdin. If the prompt looks like a build, plan or
research task, prints JSON that adds grill-contract.md as additional context.
The hook never blocks a prompt. Input and contract read errors produce a warning.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "grill-contract.md"

# Matches an action verb at the start of a clause (so "Do not train..." does not fire, but
# "How do we train a 7B model?" does). Edit the verb list to change what fires the hook.
VERBS = (r"(?:build|make|create|implement|add|refactor|migrate|design|plan|research|compare|"
         r"evaluate|benchmark|train|fine[- ]tune|experiment|set up|install|fix|investigate|reproduce|"
         r"find\s+(?:out|the\s+best|a\s+(?:way|better)|better|alternatives|options|sources|papers|evidence|why|how|whether|which)|"
         r"(?:write|draft)\s+(?:up\s+)?(?:a|an|the|our|my)?\s*(?:[\w-]+\s+){0,2}(?:plan|spec|proposal|design|pipeline|experiment|protocol|roadmap))")
ACTION_RE = re.compile(
    r"(?:^|[.!?]\s+|\n)\s*(?:[-*]\s+|\d+[.)]\s+)?"
    r"(?:then\s+)?(?:please\s+)?"
    r"(?:(?:can|could|would|will|should)\s+(?:you|we|i)\s+"
    r"|how\s+(?:do|can|should)\s+(?:you|we|i)\s+"
    r"|(?:i\s+(?:need|want)\s+(?:you\s+)?to|help\s+me|let'?s|we\s+(?:need|have)\s+to)\s+)?"
    + VERBS + r"\b"
    r"|(?:^|[.!?]\s+|\n)\s*(?:which|what)\b[^?\n]*\bshould\s+(?:we|i)\s+(?:use|choose|run|train|compare)\b"
    r"|(?:^|[.!?]\s+|\n)\s*(?:training|evaluation|benchmark|migration|research)\s+plan\s+for\b"
    r"|\b(?:choosing|deciding|picking)\s+between\b",
    re.IGNORECASE,
)
# Settled one-line edits: the grill contract would only add noise.
# Exempt only when the primary task is a local correction ("fix the typo in X", "rename foo to bar").
TRIVIAL_RE = re.compile(r"^\s*(?:please\s+)?(?:fix|correct|replace)\s+(?:the\s+|a\s+|this\s+)?(?:typo|spelling)|^\s*rename\s+\S+\s+to\s+\S+\s*\.?\s*$", re.IGNORECASE)
# Slash commands that start substantive work get the contract too.
SUBSTANTIVE_COMMANDS = ("research", "grilling", "ml-experiment", "ml-interp", "studio", "gtm", "find-buyers", "learn-fast")
HARNESS_PREFIXES = ("<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION", "Context handoff (")
HARNESS_RE = re.compile(r"Delegated task \S+ \(.*?\) \[(completed|failed|cancelled|interrupted)\]")


def strip_quoted(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)           # fenced code is material, not a request
    text = re.sub(r"^>.*$", " ", text, flags=re.M)                 # quoted lines
    return re.sub(r"[\"“][^\"”\n]{0,300}[\"”]", " ", text)        # quoted strings


FOLLOWUP_RE = re.compile(r"^\s*(?:please\s+)?(?:fix|do|apply|make|change)\s+(?:it|that|this|them)\b", re.I)
PUNCT_RE = re.compile(r"^\s*(?:please\s+)?(?:add|remove|fix)\s+(?:a|the)\s+(?:missing\s+)?(?:period|comma|full stop|space|newline)\b", re.I)


def decide(prompt):
    """Return True when the prompt asks for build, plan, research or experiment work."""
    p = prompt.strip()
    if not p:
        return False
    if p.startswith("/"):
        cmd = p[1:].split(None, 1)[0].lower() if len(p) > 1 else ""
        return cmd in SUBSTANTIVE_COMMANDS
    if p.startswith(HARNESS_PREFIXES) or HARNESS_RE.match(p):
        return False
    p = strip_quoted(p)
    # Judge each sentence: a trivial correction in one sentence must not hide real work in the next.
    prev_trivial = False
    for sent in re.split(r"(?<=[.!?])\s+|\n+", p):
        if not sent.strip():
            continue
        if TRIVIAL_RE.search(sent) or PUNCT_RE.search(sent):
            prev_trivial = True
            continue
        if prev_trivial and FOLLOWUP_RE.search(sent):
            continue  # "Fix it and change nothing else" right after a typo request refers to that typo
        prev_trivial = False
        if ACTION_RE.search(sent):
            return True
    return False


def main():
    if os.environ.get("SKILL_HOOKS_OFF") == "1":  # the skills-off arm of a paired test
        return 0
    try:
        data = json.load(sys.stdin)
        prompt = data.get("prompt") or data.get("user_prompt") or ""
        if not isinstance(prompt, str):
            raise ValueError("Expected a string prompt")
        if not decide(prompt):
            return 0
        text = CONTRACT.read_text(encoding="utf-8").strip()
        json.dump({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                          "additionalContext": text}}, sys.stdout)
    except (OSError, ValueError, AttributeError) as exc:
        # Never block the prompt, but say the hook failed instead of failing silently.
        json.dump({"systemMessage": f"Grill hook skipped ({type(exc).__name__})."}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
