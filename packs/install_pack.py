#!/usr/bin/env python3
"""Install skill packs into ONE project, for Claude Code and Codex, so they load only there.

  python3 install_pack.py fetch web 3d video          download and verify sources (no project)
  python3 install_pack.py add web 3d --project DIR    link packs into DIR (default: cwd)
  python3 install_pack.py add web --dry-run           print the plan, write nothing (no fetch)
  python3 install_pack.py remove --project DIR        undo exactly what this script added
  python3 install_pack.py status --project DIR        check every recorded change on disk

Manifest lines in packs/<pack>/sources.txt:
  <repo> <commit> <folder> <name>          a skill folder, linked into .claude/skills and .agents/skills
  agent <repo> <commit> <file> <name>      a Claude agent file, linked into .claude/agents/<name>.md

Sources are fetched once per full commit into packs/.cache (git-ignored; some sources have no
licence for redistribution) with a sparse checkout, and the checked-out HEAD is verified. `add`
plans everything first, then applies it with the record written before each change, so a failure
part-way can always be undone. It also adds a short routing block to the project's CLAUDE.md and
AGENTS.md, and, for the web, 3d or video packs, the studio reminder hook in .claude/settings.json.
`remove` deletes a link only if it still points where this script put it, removes only this
script's hook handler, and only this script's instruction block.
"""
import argparse, fcntl, json, os, shlex, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
CACHE = os.path.join(HERE, ".cache")
GATE_CMD = f"python3 {shlex.quote(os.path.join(LIB, 'hooks', 'studio_gate.py'))}"
HOOK_HANDLER = {"type": "command", "command": GATE_CMD}
STUDIO_PACKS = {"web", "3d", "video"}
RECORD = ".skill-packs.json"
BEGIN, END = "<!-- skill-packs:begin -->", "<!-- skill-packs:end -->"
ROUTES = {
    "web": "UI, design or motion work: use the `studio` skill (its scoped-edit path for small changes).",
    "3d": "Interactive 3D: use the `studio` skill, 3D section.",
    "video": "Video or motion-graphics assets: use the `studio` skill, video section.",
    "ml": "Experiments, training and evals: `ml-experiment`. Interpretability: `ml-interp`. Papers: `scientific-writing`.",
    "market": "Users, customers, launch or marketing: use the `gtm` skill.",
}
HOME = os.path.expanduser("~")
GLOBAL_DIRS = [os.path.join(HOME, d, "skills") for d in
               (".claude", ".claude-work", ".claude-personal", ".claude-personal-mind", ".claude-work-mine", ".codex", ".agents")]


class Abort(Exception):
    pass


def say(*a):
    print(*a, flush=True)


# ---------- manifests and cache ----------

def manifest(pack):
    path = os.path.join(HERE, pack, "sources.txt")
    if not os.path.isfile(path):
        raise Abort(f"unknown pack {pack!r}: no {path}")
    out = []
    for n, line in enumerate(open(path), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        kind = "skill"
        if parts[0] == "agent":
            kind, parts = "agent", parts[1:]
        if len(parts) != 4 or len(parts[1]) != 40:
            raise Abort(f"{path}:{n}: expected '<repo> <full 40-char commit> <path> <name>'")
        out.append({"kind": kind, "repo": parts[0], "commit": parts[1], "path": parts[2], "name": parts[3], "pack": pack})
    return out


def all_paths(repo, commit):
    paths = set()
    for pack in sorted(os.listdir(HERE)):
        if os.path.isfile(os.path.join(HERE, pack, "sources.txt")):
            paths |= {e["path"] for e in manifest(pack) if e["repo"] == repo and e["commit"] == commit}
    return sorted(paths)


def cache_dir(repo, commit):
    return os.path.join(CACHE, repo.replace("/", "__") + "@" + commit)


def checkout(repo, commit):
    """Fetch repo@commit once (sparse), serialised per key, verified, published atomically."""
    d = cache_dir(repo, commit)
    os.makedirs(CACHE, exist_ok=True)
    with open(d + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        paths = all_paths(repo, commit)
        if os.path.isdir(d):
            head = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            missing = [p for p in paths if p != "." and not os.path.exists(os.path.join(d, p))]
            if head == commit and not missing:
                return d
            raise Abort(f"cache {d} is at {head[:12] or '?'} or lacks {missing[:3]}; move it aside and fetch again")
        tmp = tempfile.mkdtemp(prefix=os.path.basename(d) + ".", dir=CACHE)
        run = lambda *c: subprocess.run(c, check=True, capture_output=True, text=True)
        say(f"  fetching {repo} @ {commit[:12]}" + ("" if "." in paths else f" ({len(paths)} path(s))"))
        try:
            run("git", "init", "-q", tmp)
            run("git", "-C", tmp, "remote", "add", "origin", f"https://github.com/{repo}.git")
            if "." not in paths:
                run("git", "-C", tmp, "sparse-checkout", "set", "--no-cone", *[f"/{p}" if p.endswith(".md") else f"/{p}/" for p in paths])
            run("git", "-C", tmp, "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit)
            run("git", "-C", tmp, "checkout", "-q", "FETCH_HEAD")
            head = run("git", "-C", tmp, "rev-parse", "HEAD").stdout.strip()
            if head != commit:
                raise Abort(f"{repo}: fetched {head[:12]}, expected {commit[:12]}")
        except subprocess.CalledProcessError as e:
            shutil.rmtree(tmp, ignore_errors=True)
            raise Abort(f"could not fetch {repo}@{commit[:12]}: {(e.stderr or '').strip()[:200]}")
        except Abort:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        os.rename(tmp, d)
        return d


def source_path(e):
    p = os.path.normpath(os.path.join(checkout(e["repo"], e["commit"]), e["path"]))
    need = os.path.join(p, "SKILL.md") if e["kind"] == "skill" else p
    if not os.path.isfile(need):
        raise Abort(f"{e['repo']}@{e['commit'][:12]}: missing {need}")
    return p


# ---------- record ----------

def rec_path(proj):
    return os.path.join(proj, RECORD)


def load_record(proj):
    p = rec_path(proj)
    if os.path.islink(p):
        raise Abort(f"{p} is a symlink; refusing")
    return json.load(open(p)) if os.path.isfile(p) else {"version": 2, "packs": [], "links": [], "hook": None, "blocks": []}


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def save_record(proj, rec):
    atomic_write(rec_path(proj), json.dumps(rec, indent=2) + "\n")


# ---------- plan ----------

def plan_add(proj, packs, fetch):
    if not os.path.isdir(proj):
        raise Abort(f"{proj} is not a directory")
    for sub in (".claude", ".agents"):
        if os.path.islink(os.path.join(proj, sub)):
            raise Abort(f"{os.path.join(proj, sub)} is a symlink; refusing")
    links, collisions = [], []
    for pack in packs:
        for e in manifest(pack):
            cached = os.path.isdir(cache_dir(e["repo"], e["commit"]))
            target = source_path(e) if (fetch or cached) else f"<pending fetch {e['repo']}@{e['commit'][:12]}>"
            dests = ([".claude/skills/" + e["name"], ".agents/skills/" + e["name"]] if e["kind"] == "skill"
                     else [".claude/agents/" + e["name"] + ".md"])
            for rel in dests:
                full = os.path.join(proj, rel)
                if os.path.islink(full) and os.readlink(full) == target:
                    continue
                if os.path.lexists(full):
                    raise Abort(f"{full} already exists and is not this pack's link; move it or remove it first")
                links.append({"rel": rel, "target": target})
            if e["kind"] == "skill":
                g = [d for d in GLOBAL_DIRS if os.path.exists(os.path.join(d, e["name"], "SKILL.md"))]
                if g:
                    collisions.append(f"{e['name']}: also installed globally in {', '.join(x.replace(HOME, '~') for x in g)}")
    settings = os.path.join(proj, ".claude", "settings.json")
    if set(packs) & STUDIO_PACKS:
        if os.path.islink(settings):
            raise Abort(f"{settings} is a symlink; refusing")
        if os.path.isfile(settings):
            data = json.load(open(settings))
            if not isinstance(data, dict) or not isinstance(data.get("hooks", {}), dict) \
                    or not isinstance(data.get("hooks", {}).get("UserPromptSubmit", []), list):
                raise Abort(f"{settings}: unexpected hooks shape; fix it by hand first")
    return {"links": links, "collisions": collisions, "settings": settings}


# ---------- apply ----------

def write_block(proj, fname, packs, rec):
    path = os.path.join(proj, fname)
    if os.path.islink(path):
        raise Abort(f"{path} is a symlink; refusing")
    lines = [ROUTES[p] for p in sorted(packs) if p in ROUTES]
    block = BEGIN + "\n## Skill packs in this project\n" + "\n".join(f"- {l}" for l in lines) + "\n" + END + "\n"
    existed = os.path.isfile(path)
    text = open(path).read() if existed else ""
    if BEGIN in text and END in text:
        a, b = text.index(BEGIN), text.index(END) + len(END)
        new = text[:a] + block.rstrip("\n") + text[b:]
    else:
        new = text + ("\n" if text and not text.endswith("\n") else "") + ("\n" if text else "") + block
    if not any(x["file"] == fname for x in rec["blocks"]):
        rec["blocks"].append({"file": fname, "created_file": not existed})
    atomic_write(path, new)


def add_hook(proj, settings, rec):
    data = json.load(open(settings)) if os.path.isfile(settings) else {}
    groups = data.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
    if any(h == HOOK_HANDLER for g in groups for h in g.get("hooks", [])):
        return
    if os.path.isfile(settings) and not os.path.exists(settings + ".bak-skill-packs"):
        shutil.copy2(settings, settings + ".bak-skill-packs")
    groups.append({"hooks": [dict(HOOK_HANDLER)]})
    os.makedirs(os.path.dirname(settings), exist_ok=True)
    rec["hook"] = {"settings": os.path.relpath(settings, proj), "handler": HOOK_HANDLER}
    atomic_write(settings, json.dumps(data, indent=2) + "\n")


def cmd_add(a):
    proj = os.path.abspath(a.project)
    plan = plan_add(proj, a.packs, fetch=not a.dry_run)
    for l in plan["links"]:
        say(f"  link   {l['rel']}")
    for c in plan["collisions"]:
        say(f"  NOTE   {c} (both copies will load; consider removing the global one)")
    if a.dry_run:
        say("  block  skill-packs routing in CLAUDE.md and AGENTS.md")
        if set(a.packs) & STUDIO_PACKS:
            say(f"  hook   studio reminder in {plan['settings']}")
        say("dry run: nothing written, nothing fetched")
        return
    lockpath = rec_path(proj) + ".lock"
    with open(lockpath, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        rec = load_record(proj)
        for l in plan["links"]:
            rec["links"].append({"rel": l["rel"], "target": l["target"]})
            save_record(proj, rec)                     # record first, then mutate
            full = os.path.join(proj, l["rel"])
            os.makedirs(os.path.dirname(full), exist_ok=True)
            os.symlink(l["target"], full)
        rec["packs"] = sorted(set(rec["packs"]) | set(a.packs))
        save_record(proj, rec)
        for fname in ("CLAUDE.md", "AGENTS.md"):
            write_block(proj, fname, rec["packs"], rec)
            save_record(proj, rec)
        if set(rec["packs"]) & STUDIO_PACKS:
            add_hook(proj, plan["settings"], rec)
            save_record(proj, rec)
    os.remove(lockpath)
    say(f"done. Record: {rec_path(proj)}. Restart the agent session to load the skills.")


def cmd_remove(a):
    proj = os.path.abspath(a.project)
    rec = load_record(proj)
    conflicts, keep = [], []
    for l in rec["links"]:
        full = os.path.join(proj, l["rel"])
        if os.path.islink(full) and os.readlink(full) == l["target"]:
            os.unlink(full)
            say(f"  unlink {l['rel']}")
        elif os.path.lexists(full):
            conflicts.append(f"{l['rel']} was changed after install; left in place")
            keep.append(l)
    h = rec.get("hook")
    if h:
        settings = os.path.join(proj, h["settings"])
        if os.path.isfile(settings) and not os.path.islink(settings):
            data = json.load(open(settings))
            groups = data.get("hooks", {}).get("UserPromptSubmit", [])
            hits = [(g, i) for g in groups for i, x in enumerate(g.get("hooks", [])) if x == h["handler"]]
            if len(hits) == 1:
                g, i = hits[0]
                del g["hooks"][i]
                if not g["hooks"]:
                    groups.remove(g)
                atomic_write(settings, json.dumps(data, indent=2) + "\n")
                say(f"  hook   removed from {h['settings']}")
            elif len(hits) > 1:
                conflicts.append("studio hook appears more than once; left in place")
    for b in rec.get("blocks", []):
        path = os.path.join(proj, b["file"])
        if os.path.isfile(path) and not os.path.islink(path):
            text = open(path).read()
            if BEGIN in text and END in text:
                s, e = text.index(BEGIN), text.index(END) + len(END)
                new = (text[:s].rstrip("\n") + "\n" + text[e:].lstrip("\n")).strip("\n")
                if b.get("created_file") and not new.strip():
                    os.remove(path)
                    say(f"  remove {b['file']} (created by this script, now empty)")
                else:
                    atomic_write(path, new + "\n" if new else "")
                    say(f"  block  removed from {b['file']}")
    for c in conflicts:
        say(f"  KEEP   {c}")
    if keep:
        rec.update(links=keep, hook=None, blocks=[], packs=[])
        save_record(proj, rec)
        say("done with conflicts; the record keeps the entries left in place.")
    elif os.path.isfile(rec_path(proj)):
        os.remove(rec_path(proj))
        say("done.")


def cmd_status(a):
    proj = os.path.abspath(a.project)
    rec = load_record(proj)
    counts = {"ok": 0, "missing": 0, "wrong_target": 0, "dangling": 0}
    for l in rec["links"]:
        full = os.path.join(proj, l["rel"])
        if not os.path.lexists(full):
            counts["missing"] += 1
        elif not os.path.islink(full) or os.readlink(full) != l["target"]:
            counts["wrong_target"] += 1
        elif not os.path.exists(full):
            counts["dangling"] += 1
        else:
            counts["ok"] += 1
    hook_ok = False
    if rec.get("hook"):
        s = os.path.join(proj, rec["hook"]["settings"])
        if os.path.isfile(s):
            d = json.load(open(s))
            hook_ok = any(x == rec["hook"]["handler"] for g in d.get("hooks", {}).get("UserPromptSubmit", []) for x in g.get("hooks", []))
    blocks = {}
    for b in rec.get("blocks", []):
        p = os.path.join(proj, b["file"])
        blocks[b["file"]] = os.path.isfile(p) and BEGIN in open(p).read()
    say(json.dumps({"packs": rec["packs"], "links": counts, "hook_present": hook_ok, "routing_blocks": blocks}, indent=2))


def cmd_fetch(a):
    for pack in a.packs:
        es = manifest(pack)
        for e in es:
            source_path(e)
        say(f"{pack}: {len(es)} entries fetched and verified")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("fetch"); s.add_argument("packs", nargs="+"); s.set_defaults(fn=cmd_fetch)
    s = sub.add_parser("add"); s.add_argument("packs", nargs="+"); s.add_argument("--project", default=".")
    s.add_argument("--dry-run", action="store_true"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("remove"); s.add_argument("--project", default="."); s.set_defaults(fn=cmd_remove)
    s = sub.add_parser("status"); s.add_argument("--project", default="."); s.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    try:
        a.fn(a)
    except Abort as e:
        sys.exit(f"ABORT: {e}")
    except json.JSONDecodeError as e:
        sys.exit(f"ABORT: invalid JSON ({e.msg}); nothing changed by this step")


if __name__ == "__main__":
    main()
