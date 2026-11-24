#!/usr/bin/env python3
"""UserPromptSubmit hook: when a prompt clearly matches one of the owner's auto skills, tell the agent
to invoke it. Reason: in the 2026-11-19 pilot (10 headless Sonnet runs, ~100 skills loaded) no skill
fired, 0 of 4, even for "Humanize this paragraph", which matches writing's description word for word.

Reads the hook JSON on stdin; prints JSON with additionalContext naming at most two skills, or
nothing. Never blocks a prompt. Edit ROUTES to change what fires; tests: test_skill_router.py.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from studio_gate import decide as studio_decide  # same rule the project-level studio hook uses
except ImportError:
    def studio_decide(_prompt):
        return False

ROUTES = [
    ("learn-fast", r"\bteach me\b|\bhelp me understand\b|\bi (?:don'?t|do not) (?:get|understand)\b|\beli5\b|"
                   r"\bexplain\b.{0,60}\blike i'?m\b|\bwalk me through how\b|\bexplain how\b|\bi need to learn\b|"
                   r"\bmake (?:me )?an explainer\b|^\s*explain what\b"),
    ("gtm", r"\bgo[- ]to[- ]market\b|\bgtm\b|\bfirst \d* ?(?:customers|users|clients)\b|\bget (?:my )?(?:first )?(?:users|customers|clients)\b|"
            r"\bwhere should i (?:market|promote|launch)\b|\blaunch plan\b|\blead magnets?\b|\blinkedin content\b|\bcontent strategy\b"),
    ("find-buyers", r"\bwhere (?:do|are) (?:my |the )?buyers\b|\bbuyer communities\b|\bwhere (?:do|does) [\w ]{2,40} (?:ask|complain|talk) (?:for|about)\b"),
    ("ml-experiment", r"\bfine[- ]?tun(?:e|ing)\b(?!.{0,40}\?)|\btraining run\b|\b(?:run|train|launch)\w* .{0,30}\b(?:grpo|dpo|rl)\b|\b(?:grpo|dpo) (?:run|training)\b|\bheld[- ]?out set\b|"
                      r"\bevaluat(?:e|ing) (?:the |my |our )?(?:model|checkpoint)s?\b|\bdid (?:the|my|our) (?:run|fine-?tune|training) work\b|"
                      r"\bbenchmark(?:ing)? (?:the |our |my )?models?\b"),
    ("research", r"^\s*(?:please\s+)?(?:do (?:a |some )?)?(?:deep )?research\b|\bdeep research\b|\blook into\b|\bdig into\b|"
                 r"\bresearch question\b|\bcompare\b.{1,80}\b(?:and|vs\.?|versus)\b.{1,80}\b(?:for|which|should)\b|"
                 r"\bis .{1,60} worth it\b|\bstate of the art\b|\bliterature review\b|\brecent work on\b|"
                 r"\bwhat should i use for\b|\bfind the best\b"),
    ("writing", r"\bhumani[sz]e\b|\bunslop\b|\bremove (?:the )?ai tells\b|\bsounds? (?:like )?(?:ai|robotic)\b|\bste ?100\b|"
                r"\bsimplified technical english\b|\b(?:write|draft|rewrite|edit|polish|proofread)\b.{0,40}"
                r"\b(?:readme|docs?|documentation|spec|report|blog|post|email|proposal|pr (?:body|description)|announcement|essay|paragraph|runbook|"
                r"summary|tl;?dr|write-?up|release notes|changelog|cover letter|newsletter|tweet|thread|bio|commit message|slack message|memo|case study)\b|"
                r"\b(?:summari[sz]e|write up)\b.{0,40}\b(?:for|to) (?:the |my |our )?(?:team|manager|boss|client|investors?|stakeholders?)\b|"
                r"\bmake (?:this|it|the|my|our)(?: \w+)? (?:clearer|more readable|readable|fun(?: to read)?|easier to read)\b"),
    ("social-search", r"\bwhat (?:are|do|is) (?:people|devs|developers|users|folks|reddit|twitter|hn) (?:saying|say|think|thinking)\b|"
                      r"\bcommunity (?:opinion|sentiment|take)\b|\b(?:on|from|search) reddit\b|\breddit (?:threads?|posts?|says)\b|"
                      r"\bcomplaints about\b|\bexperiences? (?:with|using)\b|\balternatives people\b|\bis .{1,40} any good\b|"
                      r"\breviews of\b|\bwhat do people use (?:for|to)\b"),
    ("ml-interp", r"\bactivation patching\b|\bsparse autoencoders?\b|\b(?:train|load|evaluat|run|fit)\w* (?:an? |the |my |our )?SAEs?\b|\bsteering vectors?\b|\b(?:train|fit)\w* (?:a |the )?(?:linear )?probes? (?:on|for)\b|"
                  r"\bgemma ?scope\b|\btransformer ?lens\b|\bsae ?lens\b|\bnnsight\b|\btranscoders?\b|\bmech(?:anistic)? interp|"
                  r"\bcircuits? (?:in|for|discovery|analysis)\b|\battribution patching\b|\blogit lens\b"),
    ("diagnosing-bugs", r"\bdiagnose\b|\bdebug (?:this|it|the|why)\b|\bwhy (?:is|does|did|do) (?:this|it|the|my|our)(?: [\w.-]+){0,3} (?:keep )?(?:fail|failing|crash|crashing|"
                        r"hang|hanging|slow|so slow|break|broken|flak[ey])\b|\bflaky (?:test|build|ci)\b|\bintermittent(?:ly)? fail|"
                        r"\bperformance regression\b|\b(?:it|this|the \w+) (?:got|became|is) (?:way |much )?slower\b|\bregressed\b"),
]
WAYFINDER = re.compile(
    r"\bwhere (?:are|were) we\b|\bpick (?:this|it|that) (?:back )?up\b|\bresume (?:the|this|work|where)\b|"
    r"\bcontinue (?:the|this|where|from|with the)\b|^\s*cont(?:in|i|n)u?e\b|\bwhat(?:'s| is| are)? (?:the )?next(?: steps?)?\b|"
    r"\bnext steps\b|\bhow (?:are|is) (?:things|it|everything) (?:looking|going)\b|\bstatus (?:of|on) (?:the|this|my)\b|"
    r"\bmap (?:this|the) project\b|\bwayfinder\b|\bwhat(?:'s| is) (?:done|left)\b",
    re.I,
)
DEEP_TURNS = 12  # owner turns after which a session counts as long
DEEP_EVERY = 6   # in a long session, ask for a map refresh every this many turns
LONG_PROMPT_WORDS = 120


def owner_turns(transcript_path):
    """Count the owner's real messages in a Claude Code transcript; 0 when unreadable (Codex, tests)."""
    try:
        rows = [json.loads(line) for line in open(transcript_path, encoding="utf-8") if line.strip()]
    except (OSError, TypeError, ValueError):
        return 0
    n = 0
    for row in rows:
        content = (row.get("message") or {}).get("content")
        if row.get("type") != "user" or row.get("isMeta"):
            continue
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            continue
        text = content if isinstance(content, str) else " ".join(
            b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")
        if text.strip() and not text.lstrip().startswith(HARNESS):
            n += 1
    return n


RESTATEMENT = re.compile(
    r"^\s*(?:"
    r"(?:ok(?:ay)?[,\s]+(?:but\s+)?)?tl;?dr\b|"
    r"i['’]?m lost\b|i am lost\b|"
    r"what are you (?:actually |even )?(?:doing|trying to (?:fix|do))\b|"
    r"(?:can you |please )?say (?:it|that|this) (?:simply|in plain (?:words|english))\b|"
    r"in plain (?:words|english)\s*(?:[?.!]*$|[:,]?\s*(?:what (?:does|do)|say\b))|"
    r"what do you mean\b|"
    r"explain simply\s*(?:\b(?:it|that|this)\b|[.,?!:\s]*(?:please[.!?]*)?$)|"
    r"(?:i (?:don'?t get|have no idea)|no idea) what you(?: are|['’]re) doing\b|"
    r"wtf\s+(?:are?|r)\s+(?:you|u|eu)[\s.]+doing\b"
    r")",
    re.I,
)
# Confusion said anywhere in the message, after pasted context or with typos (owner, 2026-11-21).
CONFUSED = re.compile(
    r"\bwtf\s+(?:are?|r)\s+(?:you|u|eu)[\s.]+(?:doing|fixing)\b|"
    r"\b(?:i\s+)?(?:have\s+|hav\s+|ahev\s+)?no idea what\s+(?:you|u|r u|are you|you['’]?re|ur)\s+(?:are\s+)?(?:doing|fixing)\b|"
    r"\bi['’]?m (?:so |totally )?lost\b",
    re.I,
)
AGENT_TEXT = re.compile(
    r"^(?:please\s+)?(?:write|draft|rewrite|edit|polish)\s+(?:(?:an?|the|this|our|my)\s+)?"
    r"(?:\x60?(?:AGENTS|CLAUDE|SKILL)\.md\b|(?:subagent\s+)?(?:prompt|brief)\b|tool description\b)",
    re.I,
)
CODE_HINT = re.compile(r"```|\bdef |\bfunction\b|\bclass \w+|\bstack ?trace\b|\btraceback\b|\bbug\b|\bcompile", re.I)
HARNESS = ("<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION", "Context handoff (")


def owner_text(prompt):
    """The owner's own words. Only a recognised context handoff is cut at its last "User message:"
    marker; the same string inside pasted text stays as it is (Sol, 2026-11-21)."""
    p = prompt or ""
    if p.lstrip().startswith("Context handoff (") and "User message:" in p:
        p = p.rsplit("User message:", 1)[1]
    return p


def route(prompt):
    p = owner_text(prompt)
    p = p.strip()
    if not p or p.startswith(HARNESS) or p.startswith("/"):
        return []  # harness text, or the owner already typed a slash command
    if RESTATEMENT.search(p) or CONFUSED.search(p):
        return ["bro"]
    hits = []
    for name, rx in ROUTES:
        if name == "writing" and AGENT_TEXT.search(p):
            continue
        if re.search(rx, p, re.I | re.S):
            if name == "writing" and CODE_HINT.search(p) and not re.search(r"\bhumani[sz]e\b|\bste ?100\b|\bunslop\b", p, re.I):
                continue  # code edits are not writing
            hits.append(name)
    if "diagnosing-bugs" in hits and "ml-experiment" in hits:
        hits.remove("diagnosing-bugs")  # a failing training run belongs to ml-experiment
    if studio_decide(p) and "studio" not in hits:
        hits.append("studio")
    if WAYFINDER.search(p) and "wayfinder" not in hits:
        hits.insert(0, "wayfinder")
    return hits[:2]


def deep(prompt, turns):
    """Long or deep work: the owner wants wayfinder used without being asked."""
    p = owner_text(prompt)
    words = len(p.split())
    long_session = turns >= DEEP_TURNS and (turns - DEEP_TURNS) % DEEP_EVERY == 0
    return long_session or words >= LONG_PROMPT_WORDS


def main():
    if os.environ.get("SKILL_ROUTER_OFF") == "1":  # the skills-off arm of a paired test
        return 0
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    prompt = data.get("prompt", "")
    hits = route(prompt)
    stripped = owner_text(prompt).strip()
    is_deep = bool(stripped) and not stripped.startswith(HARNESS) and not stripped.startswith("/") and deep(
        prompt, owner_turns(data.get("transcript_path")))
    if is_deep and "wayfinder" not in hits:
        hits = (hits + ["wayfinder"])[:2] if len(hits) < 2 else hits
    if not hits:
        return 0
    names = " and ".join(f"`{h}`" for h in hits)
    msg = (f"This request matches the {names} skill{'s' if len(hits) > 1 else ''}. Invoke "
           f"{'them' if len(hits) > 1 else 'it'} with the Skill tool before answering (in Codex, read "
           f"~/.skills-library/skills/<name>/SKILL.md).")
    if hits != ["bro"] and "wayfinder" not in hits:
        msg += " Skip it when the honest answer is one line."
    if "wayfinder" in hits:
        msg += (" For wayfinder: create or update the project's map from the sources, invent nothing, and keep the"
                " recorded next step unless new evidence changes it.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
