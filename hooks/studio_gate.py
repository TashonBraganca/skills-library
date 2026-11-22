#!/usr/bin/env python3
"""Project-level UserPromptSubmit hook installed by packs/install_pack.py.

A reminder, not an enforcer: when a request clause asks for UI, design, motion, 3D or video work,
it points the agent at the `studio` conductor. The primary trigger is the routing block the
installer writes into the project's CLAUDE.md and AGENTS.md. Never blocks a prompt.
"""
import json
import os
import re
import sys

TARGET_RE = re.compile(
    r"\b(website|web ?site|site|landing page|homepage|home page|pricing page|page|screen|portfolio|ui|ux|"
    r"interface|component|button|form|modal|dialog|navbar|nav|header|footer|hero|card|dashboard|"
    r"design system|layout|typography|font|colou?rs?|palette|theme|animation|motion|transition|scroll|"
    r"parallax|gsap|three\.?js|r3f|webgl|shader|3d|remotion|hyperframes|video|explainer|promo|reel)\b", re.I)
REQUEST_RE = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+|let'?s\s+|i (?:want|need) (?:you )?to\s+|we need to\s+)?"
    r"(build|make|create|design|redesign|add|improve|polish|restyle|style|animate|ship|prototype|"
    r"implement|rework|refresh|render|generate|fix up)\b", re.I)
LOOK_RE = re.compile(r"\bmake (?:it|this|the \w+) look (?:good|better|nicer|great|modern|premium|clean)\b", re.I)
NEG_RE = re.compile(r"\b(do not|don'?t|never|leave .{0,40} alone|without touching)\b", re.I)
BACKEND_RE = re.compile(r"\b(api|endpoint|backend|database|sql|query|pagination|server|cron|webhook|migration)\b", re.I)
HARNESS = ("<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION", "Context handoff (")
HARNESS_RE = re.compile(r"Delegated task \S+ \(.*?\) \[(completed|failed|cancelled|interrupted)\]")

MESSAGE = (
    "If this request changes shipped UI or produces a media asset, route it through the `studio` "
    "skill (its scoped-edit path for small changes). Load each specialist it names before using it."
)


def clauses(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)          # ignore fenced code
    text = re.sub(r"[\"“][^\"”]{0,300}[\"”]", " ", text)          # ignore quoted material
    return [c for c in re.split(r"[.!?;\n]+|\b(?:and then|then|but)\b", text) if c.strip()]


def decide(prompt):
    p = prompt.strip()
    if not p or p.startswith("/") or p.startswith(HARNESS) or HARNESS_RE.match(p):
        return False
    for c in clauses(p):
        neg = NEG_RE.search(c)
        if neg:
            c = c[: neg.start()]  # the negation covers what follows it; judge only what comes before
        if BACKEND_RE.search(c) and not LOOK_RE.search(c):
            continue
        if LOOK_RE.search(c) or (REQUEST_RE.search(c) and TARGET_RE.search(c)):
            return True
    return False


def main():
    if os.environ.get("SKILL_HOOKS_OFF") == "1":  # the skills-off arm of a paired test
        return 0
    try:
        data = json.load(sys.stdin)
        prompt = data.get("prompt") or data.get("user_prompt") or ""
        if isinstance(prompt, str) and decide(prompt):
            json.dump({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                              "additionalContext": MESSAGE}}, sys.stdout)
    except (ValueError, AttributeError) as exc:
        json.dump({"systemMessage": f"Studio hook skipped ({type(exc).__name__})."}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
