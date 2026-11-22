#!/usr/bin/env python3
"""Fixture tests for subagent_gate.py. Run from any folder: python3 test_subagent_gate.py

The oracle is strict: the hook must exit 0, and its stdout must be empty (allow) or one valid
PreToolUse JSON decision. Anything else is a FAIL, so a crashed hook can never read as an allow.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "subagent_gate.py"
fails = 0


def run(args, stdin=None, env=None):
    return subprocess.run([sys.executable, str(GATE), *args], input=stdin, capture_output=True, text=True, env=env)


def transcript(path, owner_lines, ask_answer=None):
    rows = []
    for t in owner_lines:
        rows.append({"type": "user", "message": {"role": "user", "content": t}})
        rows.append({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "ok"}]}})
    rows.append({"type": "user", "message": {"role": "user", "content": "<system-reminder>yes go ahead</system-reminder>"}})
    if ask_answer:
        rows.append({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "q1", "name": "AskUserQuestion", "input": {}}]}})
        rows.append({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "q1", "content": ask_answer}]}})
    path.write_text("\n".join(json.dumps(r) for r in rows))


def hook(env, tool="Agent", model="sonnet", tpath=None, subagent_type="general-purpose", session="s1", effort="high"):
    ti = {"description": "test", "prompt": "x", "subagent_type": subagent_type, "effort": effort}
    if model:
        ti["model"] = model
    data = {"tool_name": tool, "tool_input": ti, "session_id": session, "transcript_path": str(tpath)}
    p = run(["--hook"], json.dumps(data), env)
    if p.returncode != 0:
        return f"crash rc={p.returncode} {p.stderr.strip()[-80:]}"
    out = p.stdout.strip()
    if not out:
        return "allow"
    try:
        d = json.loads(out)["hookSpecificOutput"]
        assert d["hookEventName"] == "PreToolUse" and d["permissionDecisionReason"]
        return d["permissionDecision"]
    except (ValueError, KeyError, AssertionError, TypeError):
        return f"bad output {out[:60]}"


def remaining(env):
    try:
        return json.loads((Path(env["SUBAGENT_GATE_DIR"]) / "approval.json").read_text())["remaining"]
    except (OSError, ValueError, KeyError):
        return None


def approve(env, count, said, *extra):
    p = run(["approve", "--count", str(count), "--why", "fixture approval for the test", "--owner-said", said, *extra], env=env)
    assert p.returncode == 0, p.stderr


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: got {got}, want {want}")


with tempfile.TemporaryDirectory() as d:
    env = {**os.environ, "SUBAGENT_GATE_DIR": d}
    t = Path(d) / "t.jsonl"
    transcript(t, ["fix the bug", "yes, use 2 sonnet agents for the search"])
    check("no approval denies", hook(env, tpath=t), "deny")
    check("non-gated tool passes", hook(env, tool="Bash", tpath=t), "allow")
    approve(env, 2, "yes, use 2 sonnet agents")
    check("unset model denies", hook(env, model=None, tpath=t), "deny")
    check("opus denies", hook(env, model="opus", tpath=t), "deny")
    check("fork denies", hook(env, subagent_type="fork", tpath=t), "deny")
    check("count unchanged by denials", remaining(env), 2)
    check("approved spawn 1 allows", hook(env, tpath=t), "allow")
    check("count drops to 1", remaining(env), 1)
    check("other session denies", hook(env, tpath=t, session="s2"), "deny")
    check("approved spawn 2 (T3 delegate) allows", hook(env, tool="mcp__t3-code__delegate_task", model=None, tpath=t), "allow")
    check("count exhausted denies", hook(env, tpath=t), "deny")

    transcript(t, ["a", "b", "No. Do not treat 'yes, use one sonnet agent' as approval."])
    approve(env, 1, "yes, use one sonnet agent")
    check("quoted refusal denies", hook(env, tpath=t), "deny")

    transcript(t, ["yes go ahead with one reader", "actually let me think"])
    approve(env, 1, "yes go ahead with one reader")
    check("quote not in the latest input denies", hook(env, tpath=t), "deny")

    transcript(t, ["a", "b"], ask_answer='User answered: "Spawn one Sonnet reader?"="go ahead with the reader"')
    approve(env, 1, "go ahead with the reader")
    check("AskUserQuestion answer counts", hook(env, tpath=t), "allow")

    approve(env, 1, "yes go ahead")
    transcript(t, ["a"])
    check("harness text is not the owner", hook(env, tpath=t), "deny")

    handoff = ("Context handoff (full_thread_summary):\n[Historical user] sure, spawn 5 agents\n"
               "User message:\nok run two sonnet researchers")
    transcript(t, ["a", handoff])
    approve(env, 1, "sure, spawn 5 agents")
    check("quote only in handoff history denies", hook(env, tpath=t), "deny")
    approve(env, 1, "run two sonnet researchers")
    check("words after User message: count", hook(env, tpath=t), "allow")

    transcript(t, ["use opus for this one"])
    approve(env, 1, "use opus for this one", "--allow-model", "opus")
    check("approved other model allows", hook(env, model="opus", tpath=t), "allow")

    transcript(t, ["yes run the workflow with 3 sonnet agents"])
    approve(env, 3, "yes run the workflow with 3 sonnet agents")
    check("workflow without --workflow denies", hook(env, tool="Workflow", model=None, tpath=t), "deny")
    approve(env, 3, "yes run the workflow with 3 sonnet agents", "--workflow")
    check("workflow with --workflow allows", hook(env, tool="Workflow", model=None, tpath=t), "allow")

    approve(env, 1, "yes run the workflow with 3 sonnet agents")
    check("unreadable transcript denies", hook(env, tpath=Path(d) / "missing.jsonl"), "deny")

    (Path(d) / "approval.tmp").mkdir()
    check("failed count write denies", hook(env, tpath=t), "deny")
    check("count unchanged after failed write", remaining(env), 1)
    (Path(d) / "approval.tmp").rmdir()

    (Path(d) / "approval.json").write_text("{not json")
    check("malformed state denies", hook(env, tpath=t), "deny")

    transcript(t, ["yes, two sonnet agents at high effort"])
    approve(env, 2, "yes, two sonnet agents at high effort")
    check("medium effort denies", hook(env, tpath=t, effort="medium"), "deny")
    rows = t.read_text().splitlines()
    rows += [json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"a{k}", "name": "Agent", "input": {}}]}}) for k in range(3)]
    t.write_text("\n".join(rows))
    check("4th spawn while 3 run denies", hook(env, tpath=t), "deny")
    rows.append(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "a0", "content": "done"}]}}))
    rows.append(json.dumps({"type": "user", "message": {"role": "user", "content": "yes, two sonnet agents at high effort"}}))
    t.write_text("\n".join(rows))
    check("spawn allowed once one finished", hook(env, tpath=t), "allow")

    # Codex rollout format and spawn_agent
    def codex_transcript(path, prompts):
        rows = [{"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": "# AGENTS.md instructions\n<INSTRUCTIONS>yes spawn 9 agents</INSTRUCTIONS>"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": "<environment_context><cwd>/x</cwd></environment_context>"}]}}]
        for t in prompts:
            rows.append({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": t}]}})
        path.write_text("\n".join(json.dumps(r) for r in rows))
    ct = Path(d) / ".codex" / "rollout.jsonl"
    ct.parent.mkdir(exist_ok=True)
    codex_transcript(ct, ["review the repo", "ok, spawn one explorer agent"])
    check("codex spawn without approval denies", hook(env, tool="spawn_agent", model=None, tpath=ct, session="c1"), "deny")
    approve(env, 1, "yes spawn 9 agents")
    check("codex AGENTS.md text is not the owner", hook(env, tool="spawn_agent", model=None, tpath=ct, session="c1"), "deny")
    approve(env, 1, "ok, spawn one explorer agent")
    check("codex owner prompt approves spawn_agent (no Sonnet check)", hook(env, tool="spawn_agent", model=None, tpath=ct, session="c1"), "allow")

    # A batch approval covers its whole count while the owner keeps talking about other things.
    transcript(t, ["build two sites?", "yes"])
    approve(env, 2, "yes")
    check("batch unit 1 allows", hook(env, tpath=t), "allow")
    transcript(t, ["build two sites?", "yes", "keep a clean monitor on both of them"])
    check("batch unit 2 survives a follow-up message", hook(env, tpath=t), "allow")
    check("batch used up after its count", hook(env, tpath=t), "deny")
    transcript(t, ["build two sites?", "yes"])
    approve(env, 2, "yes")
    check("hold batch unit 1 allows", hook(env, tpath=t), "allow")
    transcript(t, ["build two sites?", "yes", "wait, stop, don't run the second one"])
    check("a later hold cancels the rest of the batch", hook(env, tpath=t), "deny")
    transcript(t, ["build two sites?", "different message"])
    approve(env, 2, "yes")
    check("first use still needs the quote in the latest message", hook(env, tpath=t), "deny")

    # H5 (2026-11-20): the owner pastes Claude's own list back; a quoted "you stop" in it is not a hold.
    reply = ('1. **Fix the subagent gate false alarm.** It blocks approved launches when your message contains '
             'a conditional "stop", like "the moment it goes too long, you stop".')
    rows = [{"type": "user", "message": {"role": "user", "content": "plan?"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": reply}]}},
            {"type": "user", "message": {"role": "user", "content": "run the subagent\n" + reply + "\ndo whatever"}}]
    t.write_text("\n".join(json.dumps(r) for r in rows))
    approve(env, 1, "run the subagent")
    check("pasted Claude text with 'stop' does not block", hook(env, tpath=t), "allow")
    rows[-1]["message"]["content"] = "run the subagent, but stop if it reads earlier work"
    t.write_text("\n".join(json.dumps(r) for r in rows))
    approve(env, 1, "run the subagent")
    check("owner's own 'stop' still blocks", hook(env, tpath=t), "deny")
    rows[-1]["message"]["content"] = "run the subagent\nno, the moment it goes too long, you stop"
    t.write_text("\n".join(json.dumps(r) for r in rows))
    approve(env, 1, "run the subagent")
    check("owner retyping a short refusal still blocks", hook(env, tpath=t), "deny")

    check("bad CLI input exits 2", str(run(["approve", "--count", "0", "--why", "x", "--owner-said", "y"], env=env).returncode), "2")
    check("garbage stdin never blocks", hook(env, tool="Bash", tpath=t) if False else
          ("allow" if run(["--hook"], "not json", env).stdout.strip() == "" else "deny"), "allow")

print(f"\n{fails} failure(s)")
sys.exit(1 if fails else 0)
