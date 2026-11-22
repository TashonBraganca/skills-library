#!/usr/bin/env python3
"""Hard checks for ML experiments. Stdlib only. A failing check exits non-zero so a run
script can stop on it.

  snapshot --files F... --out DIR     copy the evaluator bundle (code, labels, held-out data,
                                      metric spec) to a pristine snapshot outside the workspace
  verify   --snapshot DIR             fail if any workspace copy differs from the snapshot
  score    --snapshot DIR -- CMD...   run the evaluator from a fresh copy of the snapshot, so
                                      edits to the workspace evaluator cannot change the score
  overlap  --train F... --eval F      id, exact-content and near-duplicate overlap across splits
  sanity   --pred F [--pred F ...]    prediction ids, degenerate or identical arms, metric schema
  manifest --run-id ID --out FILE     git state, package versions, data digests, seed, command

Exit codes: 0 pass, 1 fail, 2 bad input or usage, 3 candidates that need a human look.

Local integrity checks. A trusted score also needs the snapshot and the evaluator outside the
agent's write access (another user, another machine, or a read-only mount). Without that,
label results exploratory.

Data files: .jsonl (one object per line), .json (a list of objects, or --records-key naming the
list), .csv (header row required), .txt (one item per line). Fields: dotted paths, list indices
allowed (messages.0.content).
"""
import argparse, csv, datetime, hashlib, json, math, os, re, shlex, shutil, subprocess, sys, tempfile, uuid
from collections import Counter, defaultdict
from importlib import metadata

SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|auth)[=:]\S+|\b(sk-[\w-]{8,}|hf_[\w]{8,}|ghp_[\w]{8,}|xox[bp]-[\w-]{8,})")


class InputError(Exception):
    pass


# ---------- loading ----------

def iter_rows(path, records_key=None):
    """Yield (location, row). Strict: malformed input raises InputError with the location."""
    ext = os.path.splitext(path)[1].lower()
    if not os.path.isfile(path):
        raise InputError(f"{path}: not a file")
    with open(path, encoding="utf-8-sig") as f:
        if ext == ".jsonl":
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    raise InputError(f"{path}:{i}: invalid JSON ({e.msg})")
                if not isinstance(row, dict):
                    raise InputError(f"{path}:{i}: expected a JSON object per line")
                yield f"{path}:{i}", row
        elif ext == ".json":
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise InputError(f"{path}: invalid JSON ({e.msg})")
            if records_key:
                if not isinstance(data, dict) or records_key not in data:
                    raise InputError(f"{path}: no key {records_key!r}")
                data = data[records_key]
            if not isinstance(data, list):
                raise InputError(f"{path}: expected a list of objects (use --records-key for a wrapped list)")
            for i, row in enumerate(data):
                if not isinstance(row, dict):
                    raise InputError(f"{path}[{i}]: expected an object")
                yield f"{path}[{i}]", row
        elif ext == ".csv":
            reader = csv.reader(f)
            header = next(reader, None)
            if not header or any(not h.strip() for h in header) or len(set(header)) != len(header):
                raise InputError(f"{path}: missing, empty or duplicate header names")
            for i, cells in enumerate(reader, 2):
                if not cells:
                    continue
                if len(cells) != len(header):
                    raise InputError(f"{path}:{i}: {len(cells)} cells, header has {len(header)}")
                yield f"{path}:{i}", dict(zip(header, cells))
        elif ext == ".txt":
            for i, line in enumerate(f, 1):
                if line.strip():
                    yield f"{path}:{i}", {"text": line.rstrip("\n")}
        else:
            raise InputError(f"{path}: unsupported extension {ext!r} (use .jsonl, .json, .csv or .txt)")


def get(row, path, loc):
    """Resolve a dotted path with list indices. Missing or incompatible paths raise."""
    v = row
    for part in path.split("."):
        if isinstance(v, dict) and part in v:
            v = v[part]
        elif isinstance(v, list) and part.isdigit() and int(part) < len(v):
            v = v[int(part)]
        else:
            raise InputError(f"{loc}: field {path!r} not found")
    return v


def canonical(v):
    """Exact-equality key for any JSON value (keeps roles and turn boundaries in chat lists)."""
    if isinstance(v, str):
        return re.sub(r"\s+", " ", v).strip()
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def loose(v):
    text = v if isinstance(v, str) else json.dumps(v, sort_keys=True, ensure_ascii=False)
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- snapshot / verify / score ----------

def cmd_snapshot(a):
    root = os.path.realpath(a.root or os.getcwd())
    files = [os.path.realpath(p) for p in a.files]
    if not files:
        raise InputError("snapshot needs at least one file")
    if len(set(files)) != len(files):
        raise InputError("duplicate paths in --files")
    for p in files:
        if not os.path.isfile(p):
            raise InputError(f"{p}: not a regular file")
        if os.path.commonpath([p, root]) != root:
            raise InputError(f"{p} is outside --root {root}; give a --root that contains every evaluator file")
    entry = shlex.split(a.entry) if a.entry else []
    if a.entry and "{candidate}" not in a.entry:
        raise InputError("--entry must contain {candidate}, where the checkpoint path goes")
    out = os.path.abspath(a.out)
    if os.path.exists(out):
        raise InputError(f"{out} already exists; snapshots are never overwritten")
    inside = os.path.commonpath([out, root]) == root or os.path.commonpath([out, os.getcwd()]) == os.getcwd()
    if inside:
        print("WARN: the snapshot is inside the workspace, where the agent can edit it. Scores from it are exploratory.")
    tmp = out + ".partial"
    os.makedirs(os.path.join(tmp, "files"))
    entries = []
    for p in files:
        rel = os.path.relpath(p, root)
        dest = os.path.join("files", rel)
        os.makedirs(os.path.dirname(os.path.join(tmp, dest)), exist_ok=True)
        digest = file_sha(p)
        shutil.copy2(p, os.path.join(tmp, dest))
        if file_sha(os.path.join(tmp, dest)) != digest:
            raise InputError(f"{p} changed while it was being copied; snapshot again")
        entries.append({"source": p, "rel": rel, "copy": dest, "sha256": digest})
    manifest = {"created": datetime.datetime.now().isoformat(timespec="seconds"), "root": root, "entry": entry,
                "metrics": a.metric or [],
                "inside_workspace": inside, "files": entries}
    with open(os.path.join(tmp, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    os.rename(tmp, out)  # publish atomically
    print(f"snapshot of {len(entries)} file(s) at {out}" + ("" if entry else
          "\nWARN: no --entry recorded; `score` will only run with --exploratory and an explicit command"))
    return 0


def load_snapshot(d):
    mpath = os.path.join(d, "manifest.json")
    if not os.path.isfile(mpath):
        raise InputError(f"{d}: no manifest.json; make a snapshot first")
    m = json.load(open(mpath))
    files = m.get("files") if isinstance(m, dict) else None
    if not isinstance(files, list) or not files:
        raise InputError(f"{mpath}: empty or malformed file inventory")
    for e in files:
        if not all(k in e for k in ("source", "copy", "sha256")):
            raise InputError(f"{mpath}: malformed entry {e}")
        if file_sha(os.path.join(d, e["copy"])) != e["sha256"]:
            raise InputError(f"snapshot copy {e['copy']} no longer matches its digest; the snapshot was altered")
    return files


def load_manifest(d):
    load_snapshot(d)
    return json.load(open(os.path.join(d, "manifest.json")))


def cmd_verify(a):
    files = load_snapshot(a.snapshot)
    bad = []
    for e in files:
        if not os.path.isfile(e["source"]):
            bad.append(f"missing in workspace: {e['source']}")
        elif file_sha(e["source"]) != e["sha256"]:
            bad.append(f"changed since snapshot: {e['source']}")
    for b in bad:
        print("FAIL", b)
    print(f"OK: {len(files)} evaluator file(s) unchanged" if not bad else f"FAIL: {len(bad)} evaluator file(s) differ")
    return 1 if bad else 0


def tree_sha(path):
    """Digest of a file, or of every file under a directory (relative path + content)."""
    if os.path.islink(path):
        raise InputError(f"{path}: candidate is a symlink; pass the real path")
    if os.path.isfile(path):
        return file_sha(path)
    h = hashlib.sha256()
    n = 0
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames.sort()
        for d in dirnames:
            if os.path.islink(os.path.join(dirpath, d)):
                raise InputError(f"{os.path.join(dirpath, d)}: symlinked folder inside the candidate; copy the real files")
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            if os.path.islink(fp) or not os.path.isfile(fp):
                raise InputError(f"{fp}: symlink or special file inside the candidate; copy the real file")
            h.update(os.path.relpath(fp, path).encode() + b"\0" + file_sha(fp).encode() + b"\n")
            n += 1
    if n == 0:
        raise InputError(f"{path}: candidate directory has no files")
    return h.hexdigest()


def isolate_cmd(argv, work, tmpd, cand, root, allow_network):
    """Wrap the evaluator in an OS sandbox: no reads of the workspace (except the candidate), writes only
    to the scoring folders, no network unless allowed. macOS: sandbox-exec. Linux: bubblewrap."""
    real = lambda x: os.path.realpath(x)
    if shutil.which("sandbox-exec"):
        rules = ["(version 1)", "(allow default)"]
        if not allow_network:
            rules.append("(deny network*)")
        rules += ['(deny file-write* (subpath "/"))',
                  f'(allow file-write* (subpath "{real(work)}") (subpath "{real(tmpd)}") (literal "/dev/null") '
                  '(literal "/dev/stdout") (literal "/dev/stderr") (literal "/dev/tty") (regex #"^/dev/fd/"))']
        if root:
            rules.append(f'(deny file-read* (subpath "{real(root)}"))')
        rules.append(f'(allow file-read* (subpath "{real(cand)}"))')
        prof = os.path.join(tmpd, "guard.sb")
        open(prof, "w").write("\n".join(rules) + "\n")
        return ["sandbox-exec", "-f", prof] + argv, "sandbox-exec"
    if shutil.which("bwrap"):
        cmd = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
               "--bind", real(work), real(work), "--bind", real(tmpd), real(tmpd)]
        if root:
            cmd += ["--tmpfs", real(root)]
        cmd += ["--ro-bind", real(cand), real(cand)]
        if not allow_network:
            cmd.append("--unshare-net")
        return cmd + ["--chdir", real(work)] + argv, "bwrap"
    raise InputError("--isolate needs sandbox-exec (macOS) or bwrap (Linux: apt install bubblewrap)")


def parse_metrics(stdout, required):
    """The evaluator must print one JSON object (its last stdout line) holding finite numeric metrics,
    including every metric the snapshot declared. A silent or no-op evaluator yields no score."""
    lines = [l for l in stdout.strip().splitlines() if l.strip().startswith("{")]
    if not lines:
        return None, "evaluator printed no JSON metrics line"
    try:
        d = json.loads(lines[-1])
    except ValueError:
        return None, "last JSON line from the evaluator is not valid JSON"
    if not isinstance(d, dict):
        return None, "metrics line is not a JSON object"
    nums = {k: v for k, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)}
    missing = [k for k in required if k not in nums]
    if missing:
        return None, f"declared metric(s) missing or non-numeric: {missing}"
    if not nums:
        return None, "no finite numeric metric in the evaluator output"
    return d, ""


def cmd_score(a):
    m = load_manifest(a.snapshot)
    files = m["files"]
    root = m.get("root")
    if not os.path.exists(a.candidate):
        raise InputError(f"{a.candidate}: candidate checkpoint not found")
    cand = os.path.abspath(a.candidate)
    if m.get("entry") and not a.cmd:
        argv = [t.replace("{candidate}", cand) for t in m["entry"]]
    elif a.cmd and a.exploratory:
        argv = [t.replace("{candidate}", cand) for t in a.cmd if t != "--"]
    elif a.cmd:
        raise InputError("this snapshot has a recorded --entry; a command after -- is only allowed with --exploratory")
    else:
        raise InputError("snapshot has no recorded --entry: re-snapshot with --entry, or pass --exploratory -- CMD")
    # Every path an argument names must be the candidate, a file from the frozen copy (relative, not
    # escaping it), or an interpreter. Anything else could run or read evaluator code outside the bundle.
    rel_ok = {os.path.normpath(e.get("rel") or os.path.basename(e["source"])) for e in files}
    for t in argv[1:] if argv and not os.sep in argv[0] else argv:
        for piece in re.split(r"[=,]", t):
            if not piece or piece.startswith("-") or "{candidate}" in piece:
                continue
            if os.path.isabs(piece):
                rp = os.path.realpath(piece)
                if rp == os.path.realpath(cand) or rp.startswith(os.path.realpath(cand) + os.sep):
                    if rp.endswith((".py", ".sh", ".js")):
                        raise InputError(f"argument {t!r} runs a script from the candidate; the candidate is data, not code")
                    continue
                if os.path.exists(piece):
                    if os.path.isfile(rp) and os.access(rp, os.X_OK) and not rp.endswith((".py", ".sh", ".js")):
                        continue  # an interpreter or tool binary
                    raise InputError(f"argument {t!r} names {piece} outside the frozen copy; the evaluator must run "
                                     "only from snapshot files (relative paths) and the candidate")
            elif ("/" in piece or "." in piece) and not re.fullmatch(r"[\d.eE+-]+", piece):
                norm = os.path.normpath(piece)
                if norm.startswith(".."):
                    raise InputError(f"argument {t!r} escapes the frozen copy")
                if os.path.splitext(norm)[1] in (".py", ".sh", ".js") and norm not in rel_ok:
                    raise InputError(f"argument {t!r} names a script that is not in the snapshot")
    # Not isolated: same user, same machine. Decision-grade trust needs a separate user, machine or a
    # read-only mount, which this script cannot provide.
    if a.plan:
        lock = a.plan + ".lock.json"
        if not os.path.exists(lock) or json.load(open(lock)).get("sha256") != file_sha(a.plan):
            raise InputError("plan is not locked or changed since plan-check; run plan-check (or --relock for a recorded revision) before scoring")
    tier = "exploratory" if (a.exploratory or m.get("inside_workspace")) else "local-snapshot-not-isolated"
    before = tree_sha(cand)
    work = tempfile.mkdtemp(prefix="ml-guard-score-")
    for e in files:
        dest = os.path.join(work, e.get("rel") or os.path.basename(e["source"]))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(a.snapshot, e["copy"]), dest)
    keep = ("PATH", "HOME", "LANG", "LC_ALL", "CUDA_VISIBLE_DEVICES", "HF_HOME", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
    env = {k: v for k, v in os.environ.items() if k in keep}
    tmpd = tempfile.mkdtemp(prefix="ml-guard-tmp-")
    env.update(GUARD_EVAL_DIR=work, GUARD_CANDIDATE=cand, PYTHONPATH=work, TMPDIR=tmpd, PYTHONNOUSERSITE="1")
    if a.isolate:
        argv, iso_note = isolate_cmd(argv, work, tmpd, cand, root, a.allow_network)
        tier = ("exploratory+" if tier == "exploratory" else "") + "isolated-sandbox" + ("+network" if a.allow_network else "")
    p = subprocess.run(argv, cwd=work, env=env, capture_output=True, text=True)
    after = tree_sha(cand)
    changed = before != after
    run_id = f"{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
    metrics, why = parse_metrics(p.stdout, m.get("metrics") or [])
    plan_sha = None
    if a.plan:
        plan_sha = file_sha(a.plan)
        lock = a.plan + ".lock.json"
        if not os.path.exists(lock) or json.load(open(lock)).get("sha256") != plan_sha:
            why = (why + "; " if why else "") + "plan changed since plan-check approved it (or was never approved)"
    def _typed(v):
        try:
            return json.loads(v)
        except ValueError:
            return v
    keys = {k: _typed(v) for k, v in (kv.split("=", 1) for kv in (a.run_key or []))}
    valid = (not changed) and p.returncode == 0 and metrics is not None and not why
    record = {"run_id": run_id, "valid": valid, "status": "complete" if valid else "failed",
              "invalid_reason": why or ("candidate changed" if changed else (f"exit {p.returncode}" if p.returncode else "")),
              "metrics": metrics, "plan_sha256": plan_sha, "snapshot_manifest_sha256": file_sha(os.path.join(a.snapshot, "manifest.json")), **keys,
              "time": datetime.datetime.now().isoformat(timespec="seconds"), "trust": tier,
              "command": redact(argv), "exit_code": p.returncode,
              "candidate": {"path": cand, "sha256_before": before, "sha256_after": after, "changed_during_scoring": changed},
              "evaluator_digests": {e.get("rel") or e["source"]: e["sha256"] for e in files},
              "stdout_tail": p.stdout[-4000:], "stderr_tail": p.stderr[-2000:]}
    outdir = os.path.abspath(a.out_dir) if a.out_dir else os.path.join(a.snapshot, "scores")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, run_id + ".json")
    with open(out + ".tmp", "w") as f:
        json.dump(record, f, indent=2)
    os.rename(out + ".tmp", out)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    print(f"\nscore record: {out} (trust: {tier}; evaluator ran from a fresh copy of the snapshot in {work})")
    if changed:
        print("FAIL: the candidate changed while it was being scored; the score is void")
        return 1
    if not valid:
        print(f"FAIL: score record is invalid: {record['invalid_reason']}")
        return 1
    return 0


# ---------- overlap ----------

def shingles(text, n):
    w = text.split()
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)} if len(w) >= n else set()


def cmd_overlap(a):
    if a.ngram < 0 or not (0 < a.near_threshold <= 1) or a.max_candidates <= 0:
        raise InputError("--ngram must be >= 0, --near-threshold in (0, 1], --max-candidates > 0")
    ev = list(iter_rows(a.eval, a.records_key))
    if not ev:
        raise InputError(f"{a.eval}: no eval rows")
    e_ids = {}
    e_exact, e_loose, e_sh = defaultdict(list), defaultdict(list), {}
    index = defaultdict(set)
    for loc, row in ev:
        val = get(row, a.text_field, loc)
        if a.id_field:
            e_ids[str(get(row, a.id_field, loc))] = loc
        e_exact[sha(canonical(val))].append(loc)
        e_loose[sha(loose(val))].append(loc)
        if a.ngram:
            s = shingles(loose(val), a.ngram)
            e_sh[loc] = len(s)
            for g in s:
                index[g].add(loc)
    report = {"eval_rows": len(ev), "train_rows": 0, "id_overlap": [], "exact_overlap": [],
              "loose_overlap": [], "near_duplicate_candidates": [],
              "duplicates_inside_eval": [locs for locs in e_exact.values() if len(locs) > 1]}
    pair_hits = Counter()
    for tpath in a.train:
        n = 0
        for loc, row in iter_rows(tpath, a.records_key):
            n += 1
            val = get(row, a.text_field, loc)
            if a.id_field:
                tid = str(get(row, a.id_field, loc))
                if tid in e_ids:
                    report["id_overlap"].append([e_ids[tid], loc])
            for el in e_exact.get(sha(canonical(val)), []):
                report["exact_overlap"].append([el, loc])
            if not e_exact.get(sha(canonical(val))):
                for el in e_loose.get(sha(loose(val)), []):
                    report["loose_overlap"].append([el, loc])
            if a.ngram and index:
                ts = shingles(loose(val), a.ngram)
                hits = Counter(el for g in ts if g in index for el in index[g])
                for el, c in hits.items():
                    contain = c / e_sh[el]
                    if contain >= a.near_threshold:
                        pair_hits[(el, loc)] = (c, round(contain, 3), round(c / max(len(ts), 1), 3))
        if n == 0:
            raise InputError(f"{tpath}: no train rows")
        report["train_rows"] += n
    report["near_duplicate_candidates"] = [
        {"eval": el, "train": tl, "shared_ngrams": v[0], "eval_containment": v[1], "train_containment": v[2]}
        for (el, tl), v in sorted(pair_hits.items(), key=lambda kv: -kv[1][1])[: a.max_candidates]]
    print(json.dumps({k: (v if not isinstance(v, list) else {"count": len(v), "examples": v[:10]})
                      if k not in ("eval_rows", "train_rows") else v for k, v in report.items()}, indent=2))
    confirmed = report["id_overlap"] or report["exact_overlap"]
    if confirmed:
        print("FAIL: confirmed overlap between train and eval. Fix the split before any score counts.")
        return 1
    if report["loose_overlap"] or report["near_duplicate_candidates"]:
        print("REVIEW: near-identical or near-duplicate candidates. Open each pair and decide; record the decision.")
        return 3
    print("OK: no overlap found by these checks. They cannot see contamination in data you did not pass in.")
    return 0


# ---------- sanity ----------

def cmd_sanity(a):
    problems, warnings, arms = [], [], {}
    expected = None
    if a.expected_ids:
        expected = [str(get(r, a.id_field, loc)) for loc, r in iter_rows(a.expected_ids)]
    for p in a.pred:
        rows = list(iter_rows(p))
        if not rows:
            problems.append(f"{p}: no rows")
            continue
        ids = [str(get(r, a.id_field, loc)) for loc, r in rows] if a.id_field else None
        vals = [canonical(get(r, a.field, loc)) for loc, r in rows]
        if ids is not None:
            dup = [i for i, c in Counter(ids).items() if c > 1]
            if dup:
                problems.append(f"{p}: duplicate prediction ids, e.g. {dup[:3]}")
            if expected is not None and set(ids) != set(expected):
                problems.append(f"{p}: ids do not match the expected set (missing {len(set(expected) - set(ids))}, extra {len(set(ids) - set(expected))})")
            arms[p] = sha(json.dumps(sorted(zip(ids, vals))))
        else:
            arms[p] = sha(json.dumps(vals))
        if a.categorical and len(vals) >= a.min_n:
            top, cnt = Counter(vals).most_common(1)[0]
            if cnt == len(vals):
                problems.append(f"{p}: every prediction is {top[:40]!r} (constant output)")
            elif cnt / len(vals) >= a.max_share:
                warnings.append(f"{p}: {cnt}/{len(vals)} predictions are {top[:40]!r}; check for majority-class collapse")
    seen = {}
    for p, h in arms.items():
        if h in seen:
            problems.append(f"{p} and {seen[h]} have identical predictions: two different arms gave the same output")
        seen[h] = p
    if a.metrics:
        m = json.load(open(a.metrics))
        if not isinstance(m, dict):
            problems.append(f"{a.metrics}: expected an object of metric values")
        else:
            spec = json.load(open(a.spec)) if a.spec else {k: {} for k in m}
            if set(m) != set(spec):
                problems.append(f"metric keys {sorted(m)} do not match the declared spec {sorted(spec)}")
            for name, s in spec.items():
                v = m.get(name)
                if type(v) not in (int, float) or not math.isfinite(v):
                    problems.append(f"{name}: expected a finite number, got {v!r}")
                    continue
                b = s.get("bounds")
                if b is not None and not b[0] <= v <= b[1]:
                    problems.append(f"{name}: {v} outside declared bounds {b}")
                if v in s.get("endpoints", ()):
                    warnings.append(f"{name}: {v} is a declared endpoint; recompute it independently before reporting")
    for w in warnings:
        print("WARN", w)
    for pr in problems:
        print("FAIL", pr)
    print("OK: no problems found by these checks" if not problems else f"FAIL: {len(problems)} problem(s)")
    return 1 if problems else 0


# ---------- manifest ----------

def redact(argv):
    return [SECRET_RE.sub("<redacted>", x) for x in argv]


def cmd_manifest(a):
    if os.path.exists(a.out):
        raise InputError(f"{a.out} exists; manifests are never overwritten")
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        git = ({"state": "repository", "commit": commit.stdout.strip(), "dirty": bool(status.stdout.strip())}
               if commit.returncode == 0 else {"state": "no-repository-or-error", "error": commit.stderr.strip()[:200]})
    except (OSError, subprocess.TimeoutExpired) as e:
        git = {"state": "no-repository-or-error", "error": type(e).__name__}
    packages = {}
    for dist in ("torch", "transformers", "datasets", "trl", "peft", "accelerate", "vllm", "unsloth",
                 "transformer-lens", "sae-lens", "nnsight", "numpy", "scikit-learn"):
        try:
            packages[dist] = metadata.version(dist)
        except metadata.PackageNotFoundError:
            packages[dist] = None
    data = {}
    for p in a.data:
        if not os.path.isfile(p):
            raise InputError(f"{p}: data file not found")
        data[os.path.abspath(p)] = file_sha(p)
    out = {"run_id": a.run_id, "time": datetime.datetime.now().isoformat(timespec="seconds"),
           "cwd": os.getcwd(), "git": git, "python": sys.version.split()[0], "packages": packages,
           "data_sha256": data, "seed": a.seed, "command": redact(a.cmd) if a.cmd else None,
           "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}
    tmp = a.out + ".partial"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=2)
    os.rename(tmp, a.out)
    if git["state"] != "repository":
        print("WARN: no git commit recorded; the code version of this run is unknown")
    elif git["dirty"]:
        print("WARN: uncommitted changes; the commit does not fully describe this run")
    print(f"wrote {a.out}")
    return 0


# ---------- reconcile ----------

def cmd_reconcile(a):
    """Every planned run must be accounted for: complete, failed, or not run. A summary over a subset is the
    'incomplete execution claimed complete' failure."""
    plan = json.load(open(a.plan))
    planned = plan.get("runs") if isinstance(plan, dict) else plan
    keys = plan.get("keys") if isinstance(plan, dict) and plan.get("keys") else sorted({k for r in planned for k in r})
    if not planned or not keys:
        raise InputError(f"{a.plan}: needs {{\"keys\": [...], \"runs\": [{{...}}, ...]}}")
    for r in planned:
        if any(r.get(k) is None for k in keys):
            raise InputError(f"{a.plan}: planned run {r} lacks a value for one of {keys}")
    want = {tuple(json.dumps(r.get(k), sort_keys=True) for k in keys): r for r in planned}
    if len(want) != len(planned):
        raise InputError(f"{a.plan}: duplicate planned runs on keys {keys}")
    lock_doc = json.load(open(a.lock)) if a.lock else {}
    lock_sha = lock_doc.get("sha256")
    if not a.loose and not a.allow_unisolated and not (lock_sha and lock_doc.get("matrix_sha256")):
        raise InputError("strict reconcile needs --lock from `plan-check --plan plan.md --matrix plan.json` "
                         "(plan and run matrix locked together); use --allow-unisolated only for exploratory work")
    if lock_doc.get("matrix_sha256") and file_sha(a.plan) != lock_doc["matrix_sha256"]:
        raise InputError(f"{a.plan} differs from the run matrix locked with the plan")
    seen = defaultdict(list)
    for path in a.results:
        try:
            rec = json.load(open(path))
        except (OSError, ValueError) as e:
            raise InputError(f"{path}: unreadable result record ({e})")
        for r in (rec if isinstance(rec, list) else [rec]):
            st = r.get(a.status_field)
            ec, vd = r.get("exit_code", 0), r.get("valid", True)
            problems = []
            if lock_sha and r.get("plan_sha256") != lock_sha:
                problems.append("plan digest differs from the lock")
            mets = r.get("metrics")
            ok_num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
            if not a.loose:
                if not isinstance(mets, dict) or not any(ok_num(v) for v in mets.values()):
                    problems.append("not a guard score record with finite numeric metrics")
                if r.get("valid") is not True:
                    problems.append("record not marked valid")
                cand = r.get("candidate") or {}
                if not (cand.get("sha256_before") and cand.get("sha256_before") == cand.get("sha256_after")):
                    problems.append("no matching candidate digests before and after scoring")
                if not r.get("evaluator_digests") or not r.get("snapshot_manifest_sha256"):
                    problems.append("no evaluator digests or snapshot manifest digest")
                if not str(r.get("trust", "")).startswith("isolated-sandbox") and not a.allow_unisolated:
                    problems.append(f"trust tier {r.get('trust')!r} is not isolated (use --allow-unisolated for exploratory work)")
            if a.require_metric and not all(ok_num((mets or {}).get(mm)) for mm in a.require_metric):
                problems.append("required metric missing or not a finite number")
            if str(r.get("trust", "")).startswith("exploratory") and not a.allow_exploratory:
                problems.append("exploratory record")
            if any(r.get(k) is None for k in keys):
                st = "missing run key (counts as failed)"
            elif problems:
                st = "invalid: " + ", ".join(problems)
            elif st is None:
                st = "no status (counts as failed)"
            elif not (type(ec) is int and ec == 0) or vd is not True:
                st = f"{st} but exit_code={ec!r} valid={vd!r}"
            seen[tuple(json.dumps(r.get(k), sort_keys=True) for k in keys)].append((path, str(st)))
    missing = [k for k in want if k not in seen]
    extra = [k for k in seen if k not in want]
    dup = [k for k, v in seen.items() if len(v) > 1 and k in want]
    failed = [k for k, v in seen.items() if k in want and any(st not in ("complete", "ok", "success") for _, st in v)]
    fmt = lambda k: ", ".join(f"{n}={v}" for n, v in zip(keys, k))  # values shown as JSON: "1" and 1 differ
    print(f"planned {len(want)} | complete {len(want) - len(missing) - len(failed)} | failed {len(failed)} | "
          f"not run {len(missing)} | unplanned {len(extra)} | duplicates {len(dup)}")
    for k in missing:
        print("NOT RUN", fmt(k))
    for k in failed:
        print("FAILED ", fmt(k), [st for _, st in seen[k]])
    for k in extra:
        print("UNPLANNED", fmt(k), "(a run outside the plan: report it, never swap it in)")
    for k in dup:
        print("DUPLICATE", fmt(k), [p for p, _ in seen[k]], "(which one is reported must follow the plan's selection rule)")
    if missing or failed or dup:
        print("FAIL: the planned matrix is not complete; a summary over these results covers a subset only")
        return 1
    return 3 if extra else 0


# ---------- plan-check ----------

PLAN_FIELDS = ["Question and hypothesis", "Decision rule", "Metric", "Baseline and controls", "Data", "Leakage review",
               "Uncertainty", "Method scan", "Predictions", "Failure modes", "Pilot", "Budget",
               "What would make this result untrustworthy"]


def first_commit_time(path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ct", "--", os.path.basename(path)],
                             cwd=os.path.dirname(os.path.abspath(path)), capture_output=True, text=True, timeout=20).stdout.split()
        return int(out[-1]) if out else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def cmd_plan_check(a):
    """Validate the plan and lock its digest. `score --plan` refuses a plan edited after the lock, so a
    plan rewritten after seeing results cannot pass as pre-registered."""
    if not os.path.isfile(a.plan):
        raise InputError(f"{a.plan}: no plan file; write it from references/plan-template.md before the run")
    text = open(a.plan).read()
    tpl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "plan-template.md")
    tpl = open(tpl_path).read() if os.path.exists(tpl_path) else ""
    bad = []
    for f in PLAN_FIELDS:
        pat = r"\*\*" + re.escape(f) + r"[^*]*\*\*(.*?)(?=\n\*\*|\Z)"
        m, tm = re.search(pat, text, re.S), re.search(pat, tpl, re.S)
        body = " ".join((m.group(1) if m else "").split())
        if not m:
            bad.append(f"missing section: {f}")
        elif tm and body == " ".join(tm.group(1).split()):
            bad.append(f"unfilled section: {f} (identical to the template)")
        elif len(body) < 15 or re.search(r"<[^>]+>|\bTBD\b|\bTODO\b|^\?+$", body, re.I):
            bad.append(f"unfilled section: {f} (placeholder, TBD or too short)")
    for b in bad:
        print("FAIL", b)
    if bad:
        print(f"FAIL: {len(bad)} problem(s); plan not locked")
        return 1
    lock = a.plan + ".lock.json"
    digest = file_sha(a.plan)
    matrix_sha = file_sha(a.matrix) if a.matrix else None
    if os.path.exists(lock):
        old = json.load(open(lock))
        if old.get("sha256") == digest and (not a.matrix or old.get("matrix_sha256") == matrix_sha):
            print(f"OK: plan unchanged since it was locked at {old.get('locked')}"
                  + ("" if old.get("matrix_sha256") else " (WARNING: no run matrix locked with it)"))
            return 0
        if old.get("sha256") == digest and not a.relock:
            what = "was not locked with the plan" if not old.get("matrix_sha256") else "changed since the lock"
            print(f"FAIL: the run matrix {what}. A matrix added or edited after the lock is a protocol revision: "
                  "use --relock and report it.")
            return 1
        if not a.relock:
            print(f"FAIL: plan changed since it was locked at {old.get('locked')}; scores bound to the old plan stay "
                  "bound to it. Re-lock only with --relock and report the change as a protocol revision.")
            return 1
        history = old.get("history", []) + [{"sha256": old.get("sha256"), "locked": old.get("locked")}]
    else:
        history = []
    with open(lock, "w") as f:
        json.dump({"sha256": digest, "matrix_sha256": matrix_sha, "locked": datetime.datetime.now().isoformat(timespec="seconds"),
                   "history": history}, f, indent=2)
    print(f"OK: plan complete; locked at {lock} ({digest[:12]})" + (" as a REVISION" if history else ""))
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd_name", required=True)
    s = sub.add_parser("snapshot"); s.add_argument("--files", nargs="+", required=True); s.add_argument("--out", required=True)
    s.add_argument("--root", help="workspace folder the files live under (default: cwd); relative paths are kept")
    s.add_argument("--entry", help='evaluator command with {candidate}, e.g. "python3 eval.py --model {candidate}"')
    s.add_argument("--metric", action="append", help="metric the evaluator must print in its final JSON line (repeat)"); s.set_defaults(fn=cmd_snapshot)
    s = sub.add_parser("verify"); s.add_argument("--snapshot", required=True); s.set_defaults(fn=cmd_verify)
    s = sub.add_parser("score"); s.add_argument("--snapshot", required=True); s.add_argument("--candidate", required=True, help="checkpoint file or directory")
    s.add_argument("--out-dir", help="where score records go (default: <snapshot>/scores)")
    s.add_argument("--exploratory", action="store_true", help="allow an explicit command after --; the score is labelled exploratory")
    s.add_argument("--plan", help="approved plan.md; its digest must match the lock written by plan-check")
    s.add_argument("--run-key", action="append", help="planned run key, e.g. arm=grpo (repeat); recorded for reconcile")
    s.add_argument("--isolate", action="store_true", help="run the evaluator in an OS sandbox (no workspace reads, no network)")
    s.add_argument("--allow-network", action="store_true", help="with --isolate: keep network (API judges); recorded in the tier")
    s.add_argument("cmd", nargs=argparse.REMAINDER); s.set_defaults(fn=cmd_score)
    s = sub.add_parser("reconcile"); s.add_argument("--plan", required=True, help='JSON {"keys": [...], "runs": [...]}')
    s.add_argument("--results", nargs="+", required=True, help="run record JSON files (one run or a list each)")
    s.add_argument("--status-field", default="status")
    s.add_argument("--lock", help="plan.md.lock.json: every record must carry this plan digest and be a guard score record")
    s.add_argument("--require-metric", action="append", help="metric every record must contain (repeat)")
    s.add_argument("--allow-exploratory", action="store_true")
    s.add_argument("--allow-unisolated", action="store_true", help="accept records scored without --isolate (exploratory work)")
    s.add_argument("--loose", action="store_true", help="accept plain status records from other tools (never for decisions)"); s.set_defaults(fn=cmd_reconcile)
    s = sub.add_parser("plan-check"); s.add_argument("--plan", required=True)
    s.add_argument("--matrix", help="plan.json run matrix; its digest is locked with the plan")
    s.add_argument("--relock", action="store_true", help="accept an edited plan as a recorded protocol revision"); s.set_defaults(fn=cmd_plan_check)
    s = sub.add_parser("overlap")
    s.add_argument("--train", nargs="+", required=True); s.add_argument("--eval", required=True)
    s.add_argument("--id-field"); s.add_argument("--text-field", default="text"); s.add_argument("--records-key")
    s.add_argument("--ngram", type=int, default=13, help="shingle size for near-duplicate candidates; 0 to skip")
    s.add_argument("--near-threshold", type=float, default=0.8, help="share of an eval item's shingles shared with ONE train item")
    s.add_argument("--max-candidates", type=int, default=200)
    s.set_defaults(fn=cmd_overlap)
    s = sub.add_parser("sanity")
    s.add_argument("--pred", action="append", required=True); s.add_argument("--field", default="prediction")
    s.add_argument("--id-field"); s.add_argument("--expected-ids", help="file whose rows carry the expected ids (same --id-field)")
    s.add_argument("--categorical", action="store_true", help="enable constant-output checks (classification outputs)")
    s.add_argument("--min-n", type=int, default=20); s.add_argument("--max-share", type=float, default=0.95)
    s.add_argument("--metrics"); s.add_argument("--spec", help='JSON: {"metric": {"bounds": [lo, hi], "endpoints": [0, 1]}}')
    s.set_defaults(fn=cmd_sanity)
    s = sub.add_parser("manifest")
    s.add_argument("--run-id", required=True); s.add_argument("--out", required=True)
    s.add_argument("--data", action="append", default=[]); s.add_argument("--seed")
    s.add_argument("cmd", nargs=argparse.REMAINDER); s.set_defaults(fn=cmd_manifest)
    a = ap.parse_args()
    if getattr(a, "cmd", None) and a.cmd[:1] == ["--"]:
        a.cmd = a.cmd[1:]
    try:
        return a.fn(a)
    except InputError as e:
        print(f"INPUT ERROR: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"INPUT ERROR: invalid JSON ({e.msg})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
