#!/usr/bin/env python3
"""Fixture tests for skill_router.py: should-fire prompts from each skill's tests/cases.md, plus
stay-quiet prompts. Run from any folder."""
import json
import subprocess
import sys
from pathlib import Path

ROUTER = Path(__file__).resolve().parent / "skill_router.py"
CASES = [
    ("What are people saying about Cursor's new agent mode?", ["social-search"]),
    ("Is Linear any good for a 3-person team?", ["social-search"]),
    ("Any complaints about Supabase auth lately?", ["social-search"]),
    ("Run activation patching on layer 12 of Gemma 2 2B for the IOI task.", ["ml-interp"]),
    ("Load the Gemma Scope SAEs and find features for refusal.", ["ml-interp"]),
    ("Train an SAE on the residual stream of our 1B model.", ["ml-interp"]),
    ("Why is this test failing only on CI?", ["diagnosing-bugs"]),
    ("Diagnose why the export endpoint got way slower after Tuesday's deploy.", ["diagnosing-bugs"]),
    ("We have a flaky test in the auth suite, debug it.", ["diagnosing-bugs"]),
    ("Build a landing page for the walkability grader with lots of motion.", ["studio"]),
    ("Make it look premium.", ["studio"]),
    ("Fit a linear regression on rent vs distance.", []),
    ("Add pagination to the users API endpoint.", []),
    ("ok but tldr?", ["bro"]),
    ("Earlier you said the patch passed 12 tests.\n\nwtf ar eu. doing i ahev no idea what r u fixing", ["bro"]),
    ("I'm lost. What are you actually trying to fix?", ["bro"]),
    ("TL;DR this for me: the bot log says User message: restart the worker, then it hung.", ["bro"]),
    ("Humanize this paragraph for our blog: Our pipeline isn't just a tool...", ["writing"]),
    ("Rewrite these deploy steps in STE100 simplified technical English: ...", ["writing"]),
    ("Write a README for the walkability grader in this repo.", ["writing"]),
    ("Make this report fun to read", ["writing"]),
    ("Rewrite this function to use async with aiohttp:\n\ndef fetch(urls): ...", []),
    ("Fix the typo in line 3.", []),
    ("Research question: as of late 2026, is DPO still competitive with GRPO-style RL?", ["research"]),
    ("Compare vLLM and SGLang for serving an 8B instruct model on one H100. Which should I use?", ["research"]),
    ("Do a deep research on whether SAE probes beat linear probes at matched sparsity.", ["research"]),
    ("What year was the paper 'Attention Is All You Need' published?", []),
    ("Explain how attention works in transformers.", ["learn-fast"]),
    ("I don't get KL divergence, teach me.", ["learn-fast"]),
    ("What does the --since flag do in papers.py?", []),
    ("How do I get my first 10 customers for this tool?", ["gtm"]),
    ("Make me a LinkedIn content plan for the agency.", ["gtm"]),
    ("Where do bookkeepers complain about reconciliation tools?", ["find-buyers"]),
    ("Fine-tune Qwen on our street-view captions and tell me if it beats the base.", ["ml-experiment"]),
    ("Explain what GRPO is.", ["learn-fast"]),
    ("Launch a GRPO run on the pod with the new reward.", ["ml-experiment"]),
    ("Change the API timeout to 30s.", []),
    ("Draft release notes for v0.4.", ["writing"]),
    ("Write a LinkedIn post about the walkability launch.", ["writing"]),
    ("Summarize this thread for my manager.", ["writing"]),
    ("Write a commit message for these changes.", ["writing"]),
    ("Write a unit test for parse_date.", []),
    ("TL;DR", ["bro"]),
    ("say that simply", ["bro"]),
    ("Say this simply:\n\nOur estimate is still uncertain.", ["bro"]),
    ("In plain words, what does that mean?", ["bro"]),
    ("What do you mean by that result?", ["bro"]),
    ("Explain simply, please.", ["bro"]),
    ("I don't get what you're doing", ["bro"]),
    ("wtf are you doing, I have no idea", ["bro"]),
    ("wtf ar eu. doing i ahev no idea", ["bro"]),
    ("Draft a TL;DR for my team.", ["writing"]),
    ("Explain how TL;DR summaries bias readers.", ["learn-fast"]),
    ("Explain simply how attention works.", []),
    ("What do you mean by the word 'bro' in this quote?", ["bro"]),
    ("Write an AGENTS.md for our repo. Make it clearer.", []),
    ("Write a prompt for the reviewer. Make it clearer.", []),
    ("Write a README that explains how to write a prompt.", ["writing"]),
    ("/bro", []),
    ("/writing make this clearer", []),
    ("<system-reminder>humanize</system-reminder>", []),
    ("Context handoff (x):\n[Historical user] humanize this\nUser message:\nthanks, that's all", []),
    ("Where are we on the walkability project?", ["wayfinder"]),
    ("Continue and tell me what is done and what are the next things forward", ["wayfinder"]),
    ("contiue", ["wayfinder"]),
    ("btw how are things looking ???", ["wayfinder"]),
    ("Pick this back up from yesterday.", ["wayfinder"]),
    ("What are the next steps for the GRPO run?", ["ml-experiment", "wayfinder"]),
    ("Add a next button to the carousel.", ["studio"]),  # a UI change goes through studio; wayfinder stays quiet
    ("Continue.", ["wayfinder"]),
    ("The function should continue on error.", []),
]
fails = 0
for prompt, want in CASES:
    out = subprocess.run([sys.executable, str(ROUTER)], input=json.dumps({"prompt": prompt}), capture_output=True, text=True)
    got = []
    if out.stdout.strip():
        msg = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
        got = sorted(n for n in ("writing", "research", "learn-fast", "gtm", "find-buyers", "ml-experiment", "bro", "wayfinder",
                                "social-search", "ml-interp", "diagnosing-bugs", "studio") if f"`{n}`" in msg)
    ok = out.returncode == 0 and got == sorted(want)
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {prompt[:60]!r}: got {got}, want {sorted(want)}")
# Deep work: a long prompt, or a long session, adds wayfinder without being asked.
import tempfile
def run(data):
    out = subprocess.run([sys.executable, str(ROUTER)], input=json.dumps(data), capture_output=True, text=True)
    return json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"] if out.stdout.strip() else ""
def transcript(n):
    t = Path(tempfile.mkdtemp()) / "t.jsonl"
    rows = []
    for k in range(n):
        rows.append({"type": "user", "message": {"role": "user", "content": f"owner message {k}"}})
        rows.append({"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "x"}]}})
        rows.append({"type": "user", "message": {"role": "user", "content": "<task-notification>done</task-notification>"}})
    t.write_text("\n".join(json.dumps(r) for r in rows))
    return str(t)
DEEP = [
    ("long prompt adds wayfinder", {"prompt": "word " * 130}, ["`wayfinder`"]),
    ("short prompt, short session stays quiet", {"prompt": "Change the API timeout to 30s.", "transcript_path": transcript(3)}, None),
    ("12th owner turn triggers the map", {"prompt": "Change the API timeout to 30s.", "transcript_path": transcript(12)}, ["`wayfinder`"]),
    ("13th owner turn stays quiet (only every 6)", {"prompt": "Change the API timeout to 30s.", "transcript_path": transcript(13)}, None),
    ("18th owner turn triggers again", {"prompt": "Change the API timeout to 30s.", "transcript_path": transcript(18)}, ["`wayfinder`"]),
    ("harness text never counts as deep", {"prompt": "<task-notification>" + "word " * 200}, None),
    ("deep prompt keeps its matched skill", {"prompt": "Do a deep research on SAE probes. " + "detail " * 130}, ["`research`", "`wayfinder`"]),
    ("wayfinder hint forbids invention", {"prompt": "Where are we?"}, ["invent nothing"]),
]
for name, data, want in DEEP:
    msg = run(data)
    ok = (msg == "") if want is None else all(w in msg for w in want)
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} deep: {name}")
total = len(CASES) + len(DEEP)
print(f"\n{total - fails}/{total} cases correct")
sys.exit(1 if fails else 0)
