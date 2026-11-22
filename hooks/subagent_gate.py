#!/usr/bin/env python3
"""Owner rule: ask before ANY subagent. PreToolUse gate for Claude Code, plus the approval CLI.

Hook mode (wired by install_hooks.py: Claude Code matcher Agent|Task|Workflow|mcp__t3-code__delegate_task,
Codex matcher spawn_agent|Agent in ~/.codex/hooks.json, which Codex runs only after you trust it in /hooks):
  python3 subagent_gate.py --hook < hook-json
  Denies the call unless a live approval exists whose --owner-said quote appears word for word in
  the owner's LATEST input (typed message or AskUserQuestion answer) in this transcript, and that
  input carries no refusal ("no", "don't", "do not", "not now", "stop", "never", "decline").
  An approval binds to the first session that uses it. Each spawn uses one unit of the approved
  count, consumed under a file lock; Claude Agent calls must set effort "high"; a 4th spawn while 3
  are still running (no tool result yet in the transcript) is denied; an unreadable transcript, bad state or a failed write denies.
  Workflow calls (opaque fan-out) need an approval made with --workflow. Agent and Task calls must also set model "sonnet"
  (owner's hard rule) unless the approval names another model with --allow-model.
  A hook "ask" is not used: it is reported to be auto-approved under bypassPermissions, while
  "deny" holds in every mode.

Approval CLI (run only AFTER the owner said yes, quoting their words):
  python3 subagent_gate.py approve --count N --why "<what each agent does>" --owner-said "<their exact words>"
          [--allow-model opus] [--minutes 30]
  python3 subagent_gate.py status
  python3 subagent_gate.py revoke

Files: ~/.cache/skills-subagent-gate/approval.json (live approval), log.jsonl (every decision).
Exit codes: hook always exits 0 (the decision is in its JSON); CLI exits 0 ok, 2 bad input.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import sys
from pathlib import Path

STATE = Path(os.environ.get("SUBAGENT_GATE_DIR", Path.home() / ".cache" / "skills-subagent-gate"))
APPROVAL = STATE / "approval.json"
LOG = STATE / "log.jsonl"
GATED = re.compile(r"^(Agent|Task|Workflow|spawn_agent|mcp__t3-code__delegate_task)$")
MODEL_TOOLS = {"Agent", "Task"}
SPAWN_NAMES = {"Agent", "Task", "spawn_agent", "mcp__t3-code__delegate_task"}
MAX_PARALLEL = 3  # owner, 2026-11-19: never more than 2 or 3 subagents at once
HARNESS = ("<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION", "Context handoff (",
           "<command-name>", "<local-command", "Caveat:",
           "# AGENTS.md instructions", "<environment_context>", "<user_instructions>", "<INSTRUCTIONS>", "<turn_aborted>")
REFUSAL = re.compile(r"(^|[.!?]\s*)no\b|\bdon'?t\b|\bdo not\b|\bnot now\b|\bstop\b|\bnever\b|\bdecline|\brefuse|\bnope\b|\bwait\b", re.I)
HOW = ("Ask the owner first, in plain words or with AskUserQuestion: how many agents, which model "
       "(Sonnet unless they say otherwise), what each one does, and why it cannot be done inline. "
       "After they agree, record it and retry:\n"
       "  python3 ~/.skills-library/hooks/subagent_gate.py approve --count N --why \"...\" "
       "--owner-said \"<their exact words>\"\n"
       "If they decline or have not answered, do the work inline.")


def now():
    return dt.datetime.now(dt.timezone.utc)


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def log(entry):
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps({"at": now().isoformat(timespec="seconds"), **entry}) + "\n")
    except OSError:
        pass


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            out.append(block.get("text", ""))
    return "\n".join(out)


def owner_part(t):
    """The owner's own words in a user turn: drop system reminders, and when a harness (T3) prepended a
    context handoff with historical messages, keep only what follows its last "User message:" marker."""
    t = re.sub(r"<system-reminder>.*?</system-reminder>", " ", t or "", flags=re.S)
    if "User message:" in t:
        t = t.rsplit("User message:", 1)[1]
    t = t.strip()
    return "" if not t or t.startswith(HARNESS) else t


def owner_inputs(transcript_path, keep=1):
    """The owner's last `keep` inputs: typed messages and AskUserQuestion answers. None if unreadable."""
    try:
        lines = open(transcript_path, encoding="utf-8").read().splitlines()
    except (OSError, TypeError):
        return None
    ask_ids, found = set(), []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        pl = row.get("payload") or {}
        if row.get("type") == "response_item" and pl.get("type") == "message" and pl.get("role") == "user":
            # Codex rollout: the owner's prompt is a user message item after Codex's own context blocks
            t = owner_part("\n".join(c.get("text", "") for c in pl.get("content") or [] if isinstance(c, dict)))
            if t:
                found.append(t)
            continue
        msg = row.get("message") or {}
        content = msg.get("content")
        if row.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                    ask_ids.add(b.get("id"))
        if row.get("type") != "user" or row.get("isMeta") or row.get("isSidechain"):
            continue
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in ask_ids:
                    found.append(text_of(b.get("content")) if not isinstance(b.get("content"), str) else b["content"])
            continue
        t = owner_part(text_of(content))
        if t:
            found.append(t)
    return found[-keep:]


def md_norm(s):
    """Normalise for paste matching: drop markdown marks and list numbers, then collapse spaces."""
    s = re.sub(r"[*`#>_]", "", s or "")
    s = re.sub(r"^\s*(\d+\.|[-+])\s+", "", s, flags=re.M)
    return norm(s)


def assistant_text(transcript_path, last=6):
    """Text of the last few assistant messages, for spotting lines the owner pasted back."""
    try:
        lines = open(transcript_path, encoding="utf-8").read().splitlines()
    except (OSError, TypeError):
        return ""
    out = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("type") == "assistant" and not row.get("isSidechain"):
            t = text_of((row.get("message") or {}).get("content"))
            if t.strip():
                out.append(t)
    return md_norm("\n".join(out[-last:]))


def own_words(text, pasted_from):
    """The owner's message minus lines copied from Claude's own recent replies. A pasted line that
    quotes a refusal ("you stop") is Claude's text, not the owner holding the launch (2026-11-20)."""
    keep = []
    for line in (text or "").splitlines():
        n = md_norm(line)
        if len(n) >= 25 and pasted_from and n in pasted_from:
            continue
        keep.append(line)
    return norm("\n".join(keep))


def in_flight(transcript_path, current_id=None):
    """Spawn calls in this transcript that have no result yet (still running). None if unreadable."""
    try:
        lines = open(transcript_path, encoding="utf-8").read().splitlines()
    except (OSError, TypeError):
        return None
    calls, done = set(), set()
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (row.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and b.get("name") in SPAWN_NAMES:
                calls.add(b.get("id"))
            elif b.get("type") == "tool_result":
                done.add(b.get("tool_use_id"))
    return len(calls - done - {current_id})


def load_approval():
    try:
        return json.loads(APPROVAL.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def deny(reason, event):
    log({"decision": "deny", **event, "reason": reason.splitlines()[0]})
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


def hook():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # not our input; never break the session on a parse error
    tool = data.get("tool_name", "")
    if not GATED.match(tool):
        return 0
    ti = data.get("tool_input") or {}
    event = {"tool": tool, "session": data.get("session_id"), "description": ti.get("description", "")[:80]}
    lockf = None
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        lockf = open(STATE / ".lock", "w")
        fcntl.flock(lockf, fcntl.LOCK_EX)
    except OSError:
        return deny("Blocked: the approval state could not be locked, so the approval cannot be safely used.\n" + HOW, event)
    try:
        return verify_and_consume(data, tool, ti, event)
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except OSError:
            pass


def verify_and_consume(data, tool, ti, event):
    ap = load_approval()
    if not ap:
        return deny("Blocked: the owner's rule is to ask before using any subagent, and no approval is recorded.\n" + HOW, event)
    try:
        expires = dt.datetime.fromisoformat(ap["expires"])
        remaining = int(ap["remaining"])
    except (KeyError, ValueError, TypeError):
        return deny("Blocked: the approval record is malformed. Ask the owner again.\n" + HOW, event)
    if remaining <= 0 or expires <= now():
        return deny("Blocked: the last subagent approval is used up or expired. Ask the owner again.\n" + HOW, event)
    sess = data.get("session_id")
    if ap.get("session") and sess and ap["session"] != sess:
        return deny("Blocked: this approval was given in another session. Ask the owner here.\n" + HOW, event)
    if tool == "Workflow" and not ap.get("workflow"):
        return deny("Blocked: a Workflow fans out to an unknown number of agents. Tell the owner the fan-out and model, "
                    "and record the approval with --workflow.\n" + HOW, event)
    codex = "turn_id" in data or "/.codex/" in str(data.get("transcript_path", "")) or tool == "spawn_agent"
    if tool in MODEL_TOOLS and not codex:  # the Sonnet rule is for Claude subagents; Codex spawns GPT agents
        model = (ti.get("model") or "").lower()
        allowed = {"sonnet"} | {m.lower() for m in ap.get("allow_models", [])}
        if ti.get("subagent_type") == "fork" and "fork" not in allowed:
            return deny("Blocked: a fork runs on the session model, but the owner's hard rule is Sonnet for every "
                        "subagent. Start a fresh agent with model \"sonnet\" and a full brief instead.", event)
        if ti.get("subagent_type") != "fork" and model not in allowed:
            return deny(f"Blocked: model is {model or 'unset (inherits the session model)'}, but the owner's hard rule "
                        "is model \"sonnet\" for every subagent. Retry with model: \"sonnet\".", event)
        if (ti.get("effort") or "").lower() != "high" and not ap.get("any_effort"):
            return deny("Blocked: the owner wants every subagent at high reasoning effort. Retry with effort: \"high\".", event)
    running = in_flight(data.get("transcript_path"), data.get("tool_use_id"))
    if running is not None and running >= MAX_PARALLEL:
        return deny(f"Blocked: {running} subagents are still running; the owner allows at most {MAX_PARALLEL} at once. "
                    "Wait for one to finish, then retry.", event)
    inputs = owner_inputs(data.get("transcript_path"), keep=10_000)
    if inputs is None:
        return deny("Blocked: the transcript could not be read, so the owner's approval cannot be checked.\n" + HOW, event)
    quote = norm(ap.get("owner_said"))
    anchor = ap.get("anchor")  # number of owner inputs when the first unit of this batch was used
    if not quote:
        return deny("Blocked: the approval record has no owner quote. Ask the owner again.\n" + HOW, event)
    if anchor is None:
        # First use: the owner's latest message must contain the quote.
        latest = norm(inputs[-1]) if inputs else ""
        if quote not in latest:
            return deny("Blocked: the recorded approval quotes words that are not in the owner's latest message. "
                        "Ask the owner now and record their exact reply.\n" + HOW, event)
        own = own_words(inputs[-1], assistant_text(data.get("transcript_path")))
        if REFUSAL.search(own.replace(quote, " ")) or REFUSAL.search(quote):
            return deny("Blocked: the owner's latest message reads as a refusal or a hold. Do the work inline, or ask again.", event)
        ap["anchor"] = len(inputs)
    else:
        # Later units of the same batch: the approving message is still on record, and nothing the owner
        # said since reads as a refusal or a hold. Follow-up messages on other topics do not cancel it.
        anchor = int(anchor)
        if anchor < 1 or anchor > len(inputs) or quote not in norm(inputs[anchor - 1]):
            return deny("Blocked: the approving message is no longer in this transcript. Ask the owner again.\n" + HOW, event)
        pasted = assistant_text(data.get("transcript_path"))
        if any(REFUSAL.search(own_words(t, pasted)) for t in inputs[anchor:]):
            return deny("Blocked: the owner said something since the approval that reads as a refusal or a hold. "
                        "Ask again before using the rest of this approval.", event)
    ap["remaining"] = remaining - 1
    ap["session"] = ap.get("session") or sess
    try:
        tmp = APPROVAL.with_suffix(".tmp")
        tmp.write_text(json.dumps(ap, indent=1))
        os.replace(tmp, APPROVAL)
    except OSError:
        return deny("Blocked: the approval count could not be updated, so a one-use approval could be reused.", event)
    log({"decision": "allow", **event, "remaining": ap["remaining"], "why": ap.get("why", "")[:120]})
    return 0


def cli():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("approve")
    a.add_argument("--count", type=int, required=True)
    a.add_argument("--why", required=True)
    a.add_argument("--owner-said", required=True, help="the owner's exact words of approval")
    a.add_argument("--allow-model", action="append", default=[], help="a model other than sonnet the owner approved")
    a.add_argument("--minutes", type=int, default=30)
    a.add_argument("--workflow", action="store_true", help="the owner approved a Workflow fan-out")
    a.add_argument("--any-effort", action="store_true", help="the owner approved an effort other than high")
    sub.add_parser("status")
    sub.add_parser("revoke")
    args = p.parse_args()
    STATE.mkdir(parents=True, exist_ok=True)
    if args.cmd == "approve":
        if args.count < 1 or args.count > 20 or len(args.owner_said.strip()) < 2 or len(args.why.strip()) < 10:
            print("need --count 1..20, --owner-said with the owner's words, and a real --why", file=sys.stderr)
            return 2
        ap = {"remaining": args.count, "why": args.why, "owner_said": args.owner_said,
              "allow_models": args.allow_model, "workflow": args.workflow, "any_effort": args.any_effort, "granted": now().isoformat(timespec="seconds"),
              "expires": (now() + dt.timedelta(minutes=args.minutes)).isoformat(timespec="seconds")}
        APPROVAL.write_text(json.dumps(ap, indent=1))
        log({"decision": "approved", "count": args.count, "why": args.why[:120], "owner_said": args.owner_said[:120]})
        print(f"approved {args.count} subagent(s) until {ap['expires']}")
    elif args.cmd == "status":
        print(json.dumps(load_approval() or {"approval": None}, indent=1))
    else:
        APPROVAL.unlink(missing_ok=True)
        log({"decision": "revoked"})
        print("revoked")
    return 0


if __name__ == "__main__":
    sys.exit(hook() if "--hook" in sys.argv else cli())
