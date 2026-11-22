#!/usr/bin/env python3
"""report_check.py: a genuinely supported deep report passes; the fabricated report GPT Sol built on
2026-11-21 (20 invented URLs, no supporting row, the same round copied three times, duplicate
rebuttals, an unregistered link under Why) fails. Each single fault trips its own check."""
import subprocess, sys, tempfile
from pathlib import Path
CHECK = Path(__file__).resolve().parents[1] / "scripts" / "report_check.py"

BRIEF = "Q1: Does vLLM serve an 8B chat model faster than SGLang on one H100 at concurrency 32?\n"
REG = """## Evidence register

| id | ask | claim | URL and version | locator | excerpt or value | fit | stance |
|---|---|---|---|---|---|---|---|
| e1 | Q1 | SGLang p95 lower at c=32 | https://example.org/bench-v2 | Table 3 | p95 1.8 s vs 2.4 s | same GPU, same model | supports |
| e2 | Q1 | vLLM faster at c=8 | https://example.org/vendor | Fig 2 | 20% lower p95 at c=8 | other concurrency | contradicts |
""" + "".join(f"| e{i} | Q1 | context {i} | https://example.org/s{i} | sec {i} | value {i} | partial | context |\n" for i in range(3, 23))
GOOD = """# Which engine for our 8B chat model?

## Answer

Use SGLang. Likely: at concurrency 32 on one H100 it had lower p95 latency ([bench](https://example.org/bench-v2)).

## Why

- The independent benchmark measured p95 at our concurrency.

---

# Appendix: audit trail

## Did we answer what was asked

| Ask | Outcome | Population | Comparator | Constraints | Evidence type | Disposition |
|---|---|---|---|---|---|---|
| Q1: faster at c=32 | match | match | match | match | match | answered |

## Refute pass

| Claim | How we tried | What it says | Verdict |
|---|---|---|---|
| Q1 SGLang faster | searched vLLM wins at c=32 | vendor run is c=8 only | survives |

## Strongest case against

- The vendor report favours vLLM at low concurrency.

## Null results and coverage

- Searched "vLLM beats SGLang concurrency 32 contradicts" on HN: nothing new. Forum search timed out (partial).

""" + REG
LOG = "".join(f"## Round {n}\nQueries run: web: engine benchmark {n}\nRegister rows added: e{n}\nDecision: continue\n\n" for n in (1, 2, 3))

FAKE_REG = """## Evidence register

| id | ask | claim | URL and version | locator | excerpt or value | fit | stance |
|---|---|---|---|---|---|---|---|
| x1 | Q1 contradicts | """ + " ".join(f"https://fake{i}.example" for i in range(20)) + """ | | | | | |
"""
FAKE = GOOD.replace(REG, FAKE_REG).replace("- The independent benchmark measured p95 at our concurrency.",
       "- See [this](https://unregistered.example/post).").replace(
       "| Q1 SGLang faster | searched vLLM wins at c=32 | vendor run is c=8 only | survives |",
       "| Q1 a | b q1 | ccc | survives |\n| Q1 a | b q1 | ccc | survives |")
FAKE_LOG = "## Round 1\nQueries run: none\nRegister rows added: none\n\n" * 3


def run(report, log, *extra):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "r.md").write_text(report); (d / "b.md").write_text(BRIEF); (d / "l.md").write_text(log)
        p = subprocess.run([sys.executable, str(CHECK), str(d / "r.md"), "--brief", str(d / "b.md"),
                            "--depth", "deep", "--log", str(d / "l.md"), *extra], capture_output=True, text=True)
        return p.returncode, p.stdout


cases = [
    ("supported deep report passes", run(GOOD, LOG), lambda rc, out: rc in (0, 3) and "FAIL" not in out),
    ("Sol's fabricated report fails", run(FAKE, FAKE_LOG), lambda rc, out: rc == 1 and "no register row for it has stance supports" in out
     and "unregistered.example" in out and "round numbers repeat" in out),
    ("unregistered link under Why fails", run(GOOD.replace("measured p95 at our concurrency.", "measured p95 ([post](https://other.example/x))."), LOG),
     lambda rc, out: rc == 1 and "other.example" in out),
    ("log row id not in register fails", run(GOOD, LOG.replace("Register rows added: e2", "Register rows added: e99")),
     lambda rc, out: rc == 1 and "e99" in out),
    ("'none (reason)' round is allowed", run(GOOD, LOG.replace("Register rows added: e2", "Register rows added: none (all hits were duplicates)")),
     lambda rc, out: "FAIL" not in out),
    ("no refute row for Q1 fails", run(GOOD.replace("| Q1 SGLang faster |", "| SGLang faster |"), LOG),
     lambda rc, out: rc == 1 and "names Q1" in out),
    ("--claims without --evidence is bad input", run(GOOD, LOG, "--claims", "/dev/null"), lambda rc, out: rc == 2),
]
fails = 0
for name, (rc, out), ok in cases:
    good = ok(rc, out)
    fails += not good
    print(f"{'ok  ' if good else 'FAIL'} {name}: rc {rc}" + ("" if good else "\n" + out))
print(f"{len(cases) - fails}/{len(cases)} cases correct")
sys.exit(1 if fails else 0)
