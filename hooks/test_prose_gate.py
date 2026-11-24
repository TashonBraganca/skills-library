#!/usr/bin/env python3
"""Fixture tests for prose_gate.py. Run from any folder."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parent / "prose_gate.py"
fails = 0


def call(mode, data):
    p = subprocess.run([sys.executable, str(GATE), mode], input=json.dumps(data), capture_output=True, text=True)
    if p.returncode != 0:
        return f"crash {p.returncode}"
    if not p.stdout.strip():
        return "pass"
    return json.loads(p.stdout).get("decision", "?")


def check(name, got, want):
    global fails
    fails += got != want
    print(f"{'ok  ' if got == want else 'FAIL'} {name}: got {got}, want {want}")


def transcript(path, reply, owner="write me a summary"):
    rows = [{"type": "user", "message": {"role": "user", "content": owner}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "x — y"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": reply}]}}]
    path.write_text("\n".join(json.dumps(r) for r in rows))


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    t = d / "t.jsonl"
    transcript(t, "The run finished. Accuracy rose from 71% to 74% on 404 items.")
    check("clean reply passes", call("--stop", {"transcript_path": str(t)}), "pass")
    transcript(t, "It's not just faster — it's better. I hope this helps!")
    check("dash and residue block", call("--stop", {"transcript_path": str(t)}), "block")
    check("already retried never loops", call("--stop", {"transcript_path": str(t), "stop_hook_active": True}), "pass")
    transcript(t, "Here is the code:\n```\na — b\n```\nDone, tests pass.")
    check("dash inside code block passes", call("--stop", {"transcript_path": str(t)}), "pass")
    check("tool output dashes are not the reply", call("--stop", {"transcript_path": str(t)}), "pass")
    rows = [json.loads(l) for l in t.read_text().splitlines()]
    rows.insert(3, {"type": "user", "isMeta": True, "message": {"role": "user", "content": "<system-reminder>note</system-reminder>"}})
    rows[-1] = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Done \u2014 shipped."}]}}
    t.write_text("\n".join(json.dumps(r) for r in rows))
    check("system-reminder row mid-turn does not hide the reply", call("--stop", {"transcript_path": str(t)}), "block")
    check("unreadable transcript passes", call("--stop", {"transcript_path": str(d / "nope.jsonl")}), "pass")

    doc = d / "report.md"
    doc.write_text("# Results\n\nThe cache cut costs — a lot. Great question!\n")
    check("prose file with dash blocks", call("--post-tool", {"tool_input": {"file_path": str(doc)}}), "block")
    clean = d / "notes.md"
    clean.write_text("# Results\n\nThe cache cut costs from $8,200 to $4,100.\n")
    check("clean prose file passes", call("--post-tool", {"tool_input": {"file_path": str(clean)}}), "pass")
    skill = d / "skills" / "x" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("use — here")
    check("agent file skipped", call("--post-tool", {"tool_input": {"file_path": str(skill)}}), "pass")
    code = d / "a.py"
    code.write_text("# a — b\n")
    check("code file skipped", call("--post-tool", {"tool_input": {"file_path": str(code)}}), "pass")
    check("codex last_assistant_message with dash blocks", call("--stop", {"last_assistant_message": "Done \u2014 shipped."}), "block")
    check("codex clean reply passes", call("--stop", {"last_assistant_message": "Done. Shipped v0.4."}), "pass")
    check("long reply with no opener passes (opener rule removed 2026-11-24)", call("--stop", {"last_assistant_message": "Detail sentence here. " * 300}), "pass")
    import json as _j, subprocess as _sp, sys as _s, os as _o
    _r = _sp.run([_s.executable, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "prose_gate.py"), "--stop"],
                 input=_j.dumps({"last_assistant_message": "A long answer \u2014 with a dash. " * 80}), capture_output=True, text=True)
    _reason = (_j.loads(_r.stdout or "{}").get("reason") or "")
    check("dash block demands the full reply, never a summary", "pass" if "Do not summarize" in _reason and "full" in _reason else "block", "pass")
    check("short reply without opener passes", call("--stop", {"last_assistant_message": "Detail sentence here. " * 40}), "pass")
    check("mostly-code long reply passes", call("--stop", {"last_assistant_message": "Here:\n```python\n" + "x = 1\n" * 400 + "```"}), "pass")
    check("stop_hook_active never blocks", call("--stop", {"last_assistant_message": "Detail sentence here. " * 120, "stop_hook_active": True}), "pass")
    patch = f"*** Begin Patch\n*** Update File: {doc.name}\n@@\n-x\n+y\n*** End Patch"
    check("codex apply_patch on a prose file blocks", call("--post-tool", {"cwd": str(d), "tool_input": {"command": patch}}), "block")

    # learning rule: learn-fast and writing must both run on a learning request
    def learn_t(path, owner, skills, reply):
        rows = [{"type": "user", "message": {"role": "user", "content": owner}}]
        for k, sk in enumerate(skills):
            rows.append({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"s{k}", "name": "Skill", "input": {"skill": sk}}]}})
            rows.append({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": f"s{k}", "content": "loaded"}]}})
        rows.append({"type": "assistant", "message": {"content": [{"type": "text", "text": reply}]}})
        path.write_text("\n".join(json.dumps(r) for r in rows))
    long_reply = "KL divergence measures how one distribution differs from another. " * 12
    learn_t(t, "I don't get KL divergence, teach me.", [], long_reply)
    check("learning request with no skills blocks", call("--stop", {"transcript_path": str(t)}), "block")
    learn_t(t, "I don't get KL divergence, teach me.", ["learn-fast"], long_reply)
    check("learn-fast without writing blocks", call("--stop", {"transcript_path": str(t)}), "block")
    learn_t(t, "I don't get KL divergence, teach me.", ["learn-fast", "writing"], long_reply)
    check("learn-fast and writing both ran passes", call("--stop", {"transcript_path": str(t)}), "pass")
    learn_t(t, "I don't get KL divergence, teach me.", [], "It measures how one distribution differs from another.")
    check("short learning answer is exempt", call("--stop", {"transcript_path": str(t)}), "pass")
    learn_t(t, "Change the API timeout to 30s.", [], long_reply)
    check("non-learning request is untouched", call("--stop", {"transcript_path": str(t)}), "pass")
    check("garbage stdin passes", "pass" if subprocess.run([sys.executable, str(GATE), "--stop"], input="nope",
          capture_output=True, text=True).stdout.strip() == "" else "block", "pass")

print(f"\n{fails} failure(s)")
sys.exit(1 if fails else 0)
