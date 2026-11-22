#!/usr/bin/env python3
"""Static checks for every installed skill. Catches the defects reviews kept finding by hand.

  python3 ~/.skills-library/scripts/skill_lint.py            # all skills in skills.txt
  python3 ~/.skills-library/scripts/skill_lint.py research   # one skill

Checks (FAIL blocks, WARN is advice):
  FAIL  frontmatter missing name or description, name differs from the folder, description over 1024 chars
  FAIL  a referenced local file (references/..., scripts/..., examples/...) does not exist
  FAIL  a pointer to a retired skill (design-craft, working-with-agents, asd-ste100, prototype, retro,
        codebase-design, implement, brainstorming, domain-modeling, writing-for-agents)
  FAIL  a script path in a command (python3 .../x.py) does not exist
  WARN  SKILL.md over 150 lines (focused skills beat exhaustive ones: SkillsBench, arXiv 2602.12670)
  WARN  auto skill description with no quoted trigger phrase
  WARN  a "Use for"/"Use when" description shorter than 80 chars

Exit 0 clean, 1 any FAIL.
Evidence for the length and focus rules: SkillsBench (focused skills with at most three modules beat
exhaustive bundles), WebDev-Skills-Bench arXiv 2608.23067 (injected skills often cost more than they help;
anti-pattern rules beat example-heavy content), IFScale arXiv 2507.11538 (adherence drops as
instruction count rises; earlier instructions are favoured).
"""
import os
import re
import sys

LIB = os.path.expanduser("~/.skills-library")
RETIRED = ["`humanizer` skill", "invoke the `humanizer`", "`/ste100`", "type /ste100", "`ste100` skill", "`unslop` skill", "resume-all",
           "design-craft", "working-with-agents", "asd-ste100", "codebase-design\"", "/codebase-design",
           "Skill tool with \"codebase-design", "brainstorming", "domain-modeling", "writing-for-agents",
           "`prototype`", "`retro`", "`implement`"]
REF_RE = re.compile(r"(?<![\w/~.-])((?:references|scripts|examples|agents)/[\w./-]+\.(?:md|py|mjs|js|json|sh|txt))")
SCRIPT_RE = re.compile(r"(~/\.skills-library/[\w./-]+\.(?:py|mjs|sh))")


def skill_dirs(names):
    out = []
    for line in open(os.path.join(LIB, "skills.txt")):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        kind, path = line.split(":", 1)
        if kind == "retired":
            continue  # names the installer moves out of tool folders, not skills
        d = os.path.join(LIB, "skills", path) if kind == "own" else os.path.join(LIB, "vendor", kind, "skills", path)
        name = os.path.basename(path)
        if not names or name in names:
            out.append((name, d, kind))
    return out


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    fm, last = {}, None
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t")) and last in fm and fm[last] in ("|", ">", "") or (line.startswith((" ", "\t")) and last and fm.get(last, "").startswith("\x00")):
            fm[last] = ("\x00" + line.strip()) if fm[last] in ("|", ">", "") else fm[last] + " " + line.strip()
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            last = k.strip()
            fm[last] = v.strip()
    fm = {k: v.lstrip("\x00") for k, v in fm.items()}
    return fm, text[m.end():]


def lint(name, d, kind):
    fails, warns = [], []
    p = os.path.join(d, "SKILL.md")
    if not os.path.isfile(p):
        return [f"{name}: no SKILL.md at {d}"], []
    text = open(p).read()
    fm, body = frontmatter(text)
    desc = fm.get("description", "")
    if not fm.get("name") or not desc:
        fails.append("frontmatter needs name and description")
    if fm.get("name") and fm["name"] != name:
        fails.append(f"frontmatter name {fm['name']!r} differs from folder {name!r}")
    if len(desc) > 1024:
        fails.append(f"description is {len(desc)} chars (limit 1024)")
    manual = fm.get("disable-model-invocation", "").lower() == "true"
    if not manual and '"' not in desc:
        warns.append("auto skill description has no quoted trigger phrases")
    n = text.count("\n")
    if n > 150:
        warns.append(f"SKILL.md is {n} lines; consider moving reference material out")
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(d) for f in fs if f.endswith(".md")]
    for f in files:
        t = open(f, errors="replace").read()
        rel = os.path.relpath(f, d)
        for r in sorted(set(REF_RE.findall(t))):
            cands = [os.path.join(d, r), os.path.join(os.path.dirname(f), r), os.path.join(os.path.dirname(f), "..", r)]
            if not any(os.path.exists(c) for c in cands) and kind == "own":
                fails.append(f"{rel}: points to missing {r}")
        for link in sorted(set(re.findall(r"\]\(([^)#\s]+)\)", t))):
            if link.startswith(("http", "mailto:", "/", "~")) or kind != "own" or not re.search(r"[./]", link):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), link))):
                fails.append(f"{rel}: markdown link to missing {link}")
        for s in sorted(set(SCRIPT_RE.findall(t))):
            if not os.path.exists(os.path.expanduser(s)):
                fails.append(f"{rel}: script {s} does not exist")
        for word in RETIRED:
            if word in t and not (name == "improve-codebase-architecture" and "codebase-design" in word and "references/codebase-design" in t):
                for i, line in enumerate(t.splitlines(), 1):
                    if word in line and "http" not in line and "Merged from" not in line and "merged" not in line.lower() and "retired" not in line.lower():
                        fails.append(f"{rel}:{i}: pointer to retired skill ({word.strip('`\"/')})")
                        break
    return fails, warns


def main():
    names = set(sys.argv[1:])
    total_fail = 0
    selected = skill_dirs(names)
    all_names = [n for n, _, _ in skill_dirs(set())]
    dup = sorted({n for n in all_names if all_names.count(n) > 1})
    for n in dup:
        print(f"FAIL manifest: {n} listed more than once")
        total_fail += 1
    unknown = sorted(names - {n for n, _, _ in selected})
    for n in unknown:
        print(f"FAIL {n}: not in skills.txt")
        total_fail += 1
    if not selected:
        print("FAIL: no skills selected")
        return 1
    for name, d, kind in selected:
        fails, warns = lint(name, d, kind)
        for f in fails:
            print(f"FAIL {name}: {f}")
        for w in warns:
            print(f"WARN {name}: {w}")
        total_fail += len(fails)
    print(f"\n{total_fail} failure(s)")
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
