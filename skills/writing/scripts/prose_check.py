#!/usr/bin/env python3
"""Mechanical check for prose meant for people: AI tells plus readability numbers.

  prose_check.py FILE [--json] [--allow-dashes] [--audience general|expert] [--html]
  cat draft.md | prose_check.py -

It skips YAML frontmatter, fenced code, inline code and URLs. For an .html file (or --html) it reads
static HTML text with selected elements dropped (script, style, SVG, code, pre, template); it does
not check what CSS hides, so confirm visibility in a browser. It finds what a regex can find:
dashes, curly quotes, chatbot residue, stock AI words, not-X-but-Y frames, staged openers and
closers, filler phrases, bold-label lists and title-case headings. It also prints sentence counts,
the average sentence length, the longest sentences, a passive-voice count and a Flesch-Kincaid
grade. It cannot judge staging, inflation, a wrong reader or whether a sentence is true: a person
still reads the text (references/humanize.md).

Exit 0: no hard flags. Exit 1: hard flags (dashes, curly quotes, chatbot residue). Exit 2: bad input.
Strong and weak flags never change the exit code; they are for the reader to judge.
"""
import argparse
import json
import re
import sys

AI_WORDS = [
    "delve", "delves", "delving", "tapestry", "testament", "pivotal", "showcase", "showcases",
    "showcasing", "underscore", "underscores", "underscoring", "vibrant", "intricate", "interplay",
    "garner", "garnered", "fostering", "foster", "enhance", "enhances", "crucial", "additionally",
    "seamless", "seamlessly", "robust", "leverage", "leveraging", "utilize", "utilizes", "utilizing",
    "facilitate", "facilitates", "realm", "embark", "elevate", "elevates", "unleash", "unlock",
    "unlocks", "game-changer", "game-changing", "cutting-edge", "nestled", "boasts", "groundbreaking",
    "revolutionary", "transformative", "empower", "empowers", "streamline", "streamlines", "holistic",
    "synergy", "paradigm", "landscape", "ever-evolving", "meticulous", "meticulously", "commendable",
    "noteworthy", "invaluable", "bustling", "breathtaking", "renowned", "enduring", "multifaceted",
]
AI_WORD_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in AI_WORDS) + r")\b", re.I)

RESIDUE = [r"I hope this helps", r"great question", r"\bcertainly!", r"\bof course!",
           r"as an AI\b", r"I'd be happy to", r"feel free to", r"happy to help", r"I apologi[sz]e for",
           r"you're absolutely right", r"as of my (last|knowledge) (update|cutoff)"]
RESIDUE_RE = re.compile("|".join(RESIDUE), re.I)
SOFT_RESIDUE_RE = re.compile(r"let me know if|hope (?:this|that) (?:makes sense|clarifies)", re.I)  # fine in a real request
ACRO_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}s?\b")
COMMON_CAPS = {"I", "A", "OK", "AI", "US", "UK", "EU", "TV", "PC", "ID", "PDF", "URL", "FAQ", "CEO", "API", "UI", "CPU", "GPU", "OS"}
try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None

NOT_X_BUT_Y = [
    r"\bnot (just|only|merely|simply)\b[^.!?\n]{0,90}\bbut\b",
    r"\b(it'?s|it is|this is|that'?s|that is) not (about )?[^.!?\n]{1,60}[,;.:\u2014\u2013]\s*(it'?s|it is|this is|that'?s|that is)\b",
    r"\bnot because\b[^.!?\n]{0,80}\bbut because\b",
    r"\b(it'?s|this is|that'?s|he'?s|she'?s|they'?re) not just\b",
    r"\bisn'?t just\b", r"\baren'?t just\b", r"\bmore than just\b",
    r"\bthis (doesn'?t|does not) mean\b[^.!?\n]{0,80}[.]\s*it means\b",
]
NXBY_RE = re.compile("|".join(NOT_X_BUT_Y), re.I)

STAGED = [r"\bhere'?s the thing\b", r"\bthe truth is\b", r"\blet'?s dive in\b", r"\blet'?s break (it|this) down\b",
          r"\blet that sink in\b", r"\bread that again\b", r"\bthat'?s the real (win|story|point)\b",
          r"\bthe (result|answer|catch|kicker)\?\s", r"\bspoiler:", r"\bin today'?s (fast-paced|digital|ever)",
          r"\bat the end of the day\b", r"\bmake no mistake\b", r"\bbuckle up\b", r"\bwhat'?s more,",
          r"\bserves as\b", r"\bstands as\b", r"\bplays a (crucial|pivotal|key|vital) role\b"]
STAGED_RE = re.compile("|".join(STAGED), re.I)

FILLER = [r"\bin order to\b", r"\bdue to the fact that\b", r"\bit is important to note\b", r"\bit'?s worth noting\b",
          r"\bit should be noted\b", r"\bneedless to say\b", r"\bin the event that\b", r"\bfor all intents and purposes\b",
          r"\bat this point in time\b", r"\bthe fact that\b"]
FILLER_RE = re.compile("|".join(FILLER), re.I)

DASH_RE = re.compile(r"[—–]|(?<=\s)--(?=\s)")
CURLY_RE = re.compile(r"[‘’“”]")
BOLD_LABEL_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*]{1,60}:\*\*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
SMALL = {"a", "an", "the", "and", "or", "but", "for", "nor", "on", "at", "to", "from", "by", "of", "in",
         "with", "vs", "via", "as", "is", "it"}
PASSIVE_RE = re.compile(r"\b(is|are|was|were|be|been|being|gets|got)\s+(\w+ly\s+)?(\w+ed|built|done|made|"
                        r"given|taken|seen|shown|known|written|found|run|set|kept|held|left|put|sent|told)\b", re.I)


def clean_lines(text):
    """Yield (line_number, prose_text) with frontmatter, fences, inline code and URLs removed."""
    lines = text.splitlines()
    i, out, in_fence = 0, [], False
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                i = j + 1
                break
    fence = None  # (char, length) of the open fence
    prev_blank = True
    for n in range(i, len(lines)):
        raw = lines[n]
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})", raw)
        if m:
            tok = m.group(1)
            if fence is None:
                fence = (tok[0], len(tok))
            elif tok[0] == fence[0] and len(tok) >= fence[1] and not raw.strip()[len(tok):].strip():
                fence = None
            continue
        if fence:
            continue
        # an indented code block needs a blank line before it and is not a list item or its continuation
        if raw.startswith("    ") and prev_blank and not re.match(r"^\s+([-*+]|\d+[.)])\s", raw) and not in_fence:
            in_fence = True
        if in_fence:
            if raw.strip() and not raw.startswith("    "):
                in_fence = False
            else:
                prev_blank = not raw.strip()
                continue
        prev_blank = not raw.strip()
        s = re.sub(r"`[^`]*`", " ", raw)
        s = re.sub(r"https?://\S+|\]\([^)]*\)", " ", s)
        out.append((n + 1, s))
    return out


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def sentences_of(prose_lines):
    text = " ".join(s for _, s in prose_lines if not HEADING_RE.match(s) and not s.strip().startswith("|"))
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text)
    return [p.strip() for p in parts if len(re.findall(r"[A-Za-z]+", p)) >= 3]


def html_text(raw):
    import html as _html
    t = re.sub(r"(?is)<(script|style|svg|code|pre|template)\b.*?</\1>", " ", raw)
    t = re.sub(r"(?is)<br\s*/?>|</(p|div|li|h[1-6]|tr|section|figcaption|caption)>", "\n", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = _html.unescape(t)
    return "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in t.splitlines() if line.strip())


def jargon(sentence):
    """Acronyms and rare words in one sentence: the load a grade formula cannot see."""
    out = [w for w in ACRO_RE.findall(sentence) if w.rstrip("s") not in COMMON_CAPS]
    if zipf_frequency:
        out += [w for w in re.findall(r"\b[a-z][a-z-]{3,}\b", sentence) if zipf_frequency(w, "en") < 2.8]
    return out


def check(text, allow_dashes=False, allow=()):
    for lit in allow:  # exact literals the author must keep (a quoted title, a log line)
        text = text.replace(lit, " ")
    prose = clean_lines(text)
    flags = {"hard": [], "strong": [], "weak": []}

    def add(level, n, kind, frag):
        flags[level].append({"line": n, "kind": kind, "text": frag.strip()[:80]})

    for n, s in prose:
        quoted = s.lstrip().startswith(">")  # a Markdown block quote is someone else's words
        level = "weak" if quoted else "hard"
        tag = " (in a block quote: keep if verbatim)" if quoted else ""
        if not allow_dashes:
            for m in DASH_RE.finditer(s):
                add(level, n, "dash" + tag, s[max(0, m.start() - 30):m.end() + 30])
        for m in CURLY_RE.finditer(s):
            add(level, n, "curly quote" + tag, s[max(0, m.start() - 20):m.end() + 20])
        for m in RESIDUE_RE.finditer(s):
            add(level, n, "chatbot residue" + tag, m.group(0))
        for m in SOFT_RESIDUE_RE.finditer(s):
            add("weak", n, "possible chatbot closer (fine in a real request)", m.group(0))
        for m in NXBY_RE.finditer(s):
            add("strong", n, "not X but Y", m.group(0))
        for m in STAGED_RE.finditer(s):
            add("strong", n, "staged opener or closer", m.group(0))
        for m in AI_WORD_RE.finditer(s):
            add("weak", n, "stock AI word", m.group(0))
        for m in FILLER_RE.finditer(s):
            add("weak", n, "filler", m.group(0))
        if BOLD_LABEL_RE.match(s):
            add("weak", n, "bold-label list item", s)
        h = HEADING_RE.match(s)
        if h:
            words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", h.group(2))]
            content = [w for w in words if w.lower() not in SMALL]
            caps = [w for w in content[1:] if w[0].isupper() and not w.isupper()]
            if len(content) >= 3 and len(caps) >= max(2, len(content) - 2):
                add("weak", n, "title-case heading", h.group(2))

    sents = sentences_of(prose)
    for sent in sents:
        j = jargon(sent)
        if len(j) >= 2:
            add("weak", 0, "dense jargon (define or cut)", f"{', '.join(j[:5])}: {sent}")
    words = [re.findall(r"[A-Za-z][A-Za-z'-]*", s) for s in sents]
    nw = sum(len(w) for w in words)
    nsyl = sum(syllables(x) for w in words for x in w)
    stats = {"sentences": len(sents), "words": nw}
    if nw:
        stats["jargon_per_100_words"] = round(100 * sum(len(jargon(x)) for x in sents) / nw, 1)
    if sents and nw:
        stats["avg_sentence_words"] = round(nw / len(sents), 1)
        stats["fk_grade"] = round(0.39 * nw / len(sents) + 11.8 * nsyl / nw - 15.59, 1)
        longest = sorted(zip((len(w) for w in words), sents), reverse=True)
        stats["over_30_words"] = sum(1 for k, _ in longest if k > 30)
        stats["longest"] = [f"{k} words: {s[:90]}" for k, s in longest[:3] if k > 25]
        stats["passive_hits"] = sum(len(PASSIVE_RE.findall(s)) for s in sents)
    return flags, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="a text or Markdown file, or - for stdin")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-dashes", action="store_true", help="the writer's own sample uses dashes")
    ap.add_argument("--audience", choices=["general", "expert"], default="general")
    ap.add_argument("--html", action="store_true", help="read visible text from HTML")
    ap.add_argument("--allow", action="append", default=[], help="an exact literal to skip (repeatable)")
    a = ap.parse_args()
    try:
        text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {a.file}: {e}", file=sys.stderr)
        return 2
    if a.html or a.file.lower().endswith((".html", ".htm")):
        text = html_text(text)
    if not text.strip():
        print("empty input", file=sys.stderr)
        return 2
    flags, stats = check(text, a.allow_dashes, a.allow)
    if a.json:
        print(json.dumps({"flags": flags, "stats": stats}, indent=1))
    else:
        for level in ("hard", "strong", "weak"):
            if flags[level]:
                print(f"{level.upper()} ({len(flags[level])})")
                for f in flags[level][:40]:
                    print(f"  line {f['line']}: {f['kind']}: {f['text']}")
        print("STATS " + ", ".join(f"{k} {v}" for k, v in stats.items() if k != "longest"))
        for s in stats.get("longest", []):
            print("  long: " + s)
        if stats.get("avg_sentence_words", 0) > 20:
            print("  average sentence over 20 words: reread the long ones")
        print("  (grade and length are signals for rereading, not a pass mark: jargon can score as easy)")
    return 1 if flags["hard"] else 0


if __name__ == "__main__":
    sys.exit(main())
