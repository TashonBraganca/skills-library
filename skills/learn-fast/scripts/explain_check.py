#!/usr/bin/env python3
"""Check that an explainer's default path is easy for a newcomer. Exit 0 pass, 1 fail, 2 bad input.

Why: prose_check.py measures sentence length, and short sentences full of jargon still score as easy.
The AtlasKV page (2026-11-20) passed it at grade 6.2 with 8 technical labels in step 1, a lambda on
screen and 37 diagram labels in step 5. This check counts what makes a page hard. It cannot tell
whether a comparison teaches the right mechanism, whether each step says why the next happens, or
whether the page is fun. Read the default path aloud for those.

Page contract (references/explainer.md):
  <div data-opener>   the answer, why it matters, the scene; holds <p data-takeaway>
  <section data-step="N">   one step of the default path, numbered 1, 2, 3... in order
  <p data-catch>      the limit that changes the takeaway, visible on the default path
  <details>           the deeper layer, closed by default; never counted (an open one fails)
  <dfn>word</dfn>     first use of a word the reader may not know
  data-show="2 3"     on diagram parts: the steps they are visible in (nested scopes intersect);
                      an SVG <text> with no data-show counts in every step
  data-ui             step counters and controls; never counted
  --terms terms.txt   the topic's term list, one per line

FAIL (structure and hard limits)          WARN (reread the page; fix if it reads hard)
  missing takeaway, steps or catch          rare words never introduced with <dfn>
  step ids not 1..N, or over 7 steps        quantities in the opener or steps 1-2
  a <details> open by default               a listed term in step 2
  a listed term in the opener or step 1     an everyday word on the term list (key, head):
                                              check it is used in its technical sense
  2+ new terms (listed or <dfn>) in a step  61 to 80 words in a step; sentences over 16 on average
  6+ visible diagram labels in a step       takeaway over 30 words
  over 80 words in a step                   formulas, symbols or ids, and 3+ numbers in a step:
                                              keep what the answer stands on, explained in place
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser

LIMITS = {"takeaway_words": 30, "step_terms": 1, "step_quantities": 2, "warn_words": 60,
          "max_words": 80, "avg_sentence": 16, "labels": 5, "max_steps": 7, "zipf": 3.4,
          "everyday_zipf": 4.5}
COMMON_CAPS = {"AI", "OK", "US", "UK", "EU", "TV", "PC", "ID", "PDF", "URL", "FAQ", "CEO", "USA", "I", "A"}
SYMBOLS = re.compile(r"[α-ωΑ-Ω∑∏∫√∛∜≈≠≤≥∈∝∞⊕⊗·×÷]|\w_\w|\^\w|\w\(\w\)\s*=|@\d|\b[A-Z]\d+\b|\b\w+\s*=\s*\d")
QUANTITY = re.compile(r"(?<![\w.])[-−]?\d[\d,]*(?:\.\d+)?%?|\b(?:hundreds?|thousands?|millions?|billions?|trillions?)\b", re.I)
YEAR = re.compile(r"^(?:19|20)\d\d$")
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*[A-Za-z]|[A-Za-z]")
SKIP = {"script", "style", "template", "noscript", "button", "nav"}
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "wbr", "path", "rect", "circle", "line",
        "ellipse", "polygon", "polyline", "use", "stop"}

try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []        # (tag, attrs-derived flags)
        self.regions = {}      # "opener", "catch" or step id -> text
        self.dfn = {}
        self.takeaway = []
        self.labels = []       # (set of steps or None, text)
        self.step_ids = []
        self.open_details = 0
        self._dfn = None
        self._label = None

    def flags(self):
        return [f for _, f in self.stack]

    def inside(self, key):
        return any(key in f for f in self.flags())

    def region(self):
        for f in reversed(self.flags()):
            for key in ("step", "opener", "catch"):
                if key in f:
                    return f[key] if key == "step" else key
        return None

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        f = {}
        if tag in SKIP or "data-ui" in a:
            f["skip"] = True
        if tag == "details":
            f["depth"] = True
            if "open" in a:
                self.open_details += 1
        if "data-depth" in a:
            f["depth"] = True
        if "data-opener" in a:
            f["opener"] = True
        if "data-catch" in a:
            f["catch"] = True
        if "data-step" in a and tag in ("section", "article", "div") and not self.inside("depth"):
            f["step"] = a["data-step"].strip()
            self.step_ids.append(f["step"])
        if "data-takeaway" in a:
            f["takeaway"] = True
        if tag == "dfn":
            f["dfn"] = True
            self._dfn = []
        if tag == "svg":
            f["svg"] = True
        if tag == "text":
            f["label"] = True
            self._label = []
        if "data-show" in a:
            f["show"] = set(re.split(r"[\s,]+", a["data-show"].strip()))
        self.stack.append((tag, f))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] != tag:
                continue
            f = self.stack[i][1]
            outer = [g for _, g in self.stack[:i + 1]]
            hidden = any("depth" in g or "skip" in g for g in outer)
            if f.get("dfn") and self._dfn is not None:
                term = " ".join(self._dfn).strip().lower()
                where = self.region()
                if term and where and not hidden:
                    self.dfn.setdefault(where, []).append(term)
                self._dfn = None
            if f.get("label") and self._label is not None:
                text = " ".join(self._label).strip()
                if text and not hidden:
                    shows = [g["show"] for g in outer if "show" in g]
                    steps = set.intersection(*shows) if shows else None
                    self.labels.append((steps, text))
                self._label = None
            del self.stack[i:]
            return

    def handle_data(self, data):
        if self.inside("skip") or self.inside("depth"):
            return
        if self._label is not None:
            self._label.append(data)
            return
        if self.inside("svg"):
            return
        if self._dfn is not None:
            self._dfn.append(data)
        if self.inside("takeaway"):
            self.takeaway.append(data)
        where = self.region()
        if where:
            self.regions.setdefault(where, []).append(data)


def rare(word):
    w = re.sub(r"['’]s?$", "", word)
    forms = {w, re.sub(r"(es|s|ed|ing|er)$", "", w), re.sub(r"(s|d)$", "", w)}
    return max(zipf_frequency(f, "en") for f in forms if f) < LIMITS["zipf"]


def hard_words(text):
    out = []
    for w in WORD.findall(text):
        bare = re.sub(r"['’]s?$", "", w.strip("'’-"))
        if len(bare) < 2:
            continue
        if bare.isupper() and bare not in COMMON_CAPS:
            out.append(bare)
        elif re.search(r"[a-z][A-Z]|[A-Z]{2,}[a-z]", bare):
            out.append(bare)
        elif zipf_frequency and bare.islower() and rare(bare):
            out.append(bare)
    return out


def find_terms(text, terms):
    low, found = " " + text.lower() + " ", []
    for t in sorted(terms, key=len, reverse=True):
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(t) + r"(?:s|es)?(?![a-z0-9])")
        if pat.search(low):
            found.append(t)
            low = pat.sub(" ", low)
    return found


def everyday(term):
    return bool(zipf_frequency) and " " not in term and zipf_frequency(term, "en") >= LIMITS["everyday_zipf"]


def quantities(text):
    return [q for q in QUANTITY.findall(text) if not YEAR.match(q)]


def check(html, terms):
    p = Page()
    p.feed(html)
    reg = {k: re.sub(r"\s+", " ", " ".join(v)).strip() for k, v in p.regions.items()}
    fails, warns, rows = [], [], []
    known_terms, known_words = set(), set()

    def learn(items):
        known_terms.update(items)
        known_words.update(w for d in items for w in WORD.findall(d.lower()))

    def terms_in(text):
        found = [t for t in find_terms(text, terms) if t not in known_terms]
        hard = [t for t in found if not everyday(t)]
        soft = [t for t in found if everyday(t)]
        return hard, soft

    def symbols(where, text):
        s = sorted({m.group(0) for m in SYMBOLS.finditer(text)})
        if s:
            warns.append(f"{where}: symbols, formulas or ids {' '.join(s[:6])}: keep each one that carries the idea, explained in plain words right where it appears; move the rest under Go deeper")

    take = re.sub(r"\s+", " ", " ".join(p.takeaway)).strip()
    if not reg.get("opener"):
        fails.append("opener: missing (a data-opener block: the answer, why it matters, the scene)")
    if not take:
        fails.append("opener: missing takeaway (a data-takeaway sentence inside the opener)")
    elif len(WORD.findall(take)) > LIMITS["takeaway_words"]:
        warns.append(f"opener: takeaway is {len(WORD.findall(take))} words (aim for {LIMITS['takeaway_words']})")
    if not reg.get("catch"):
        fails.append("catch: missing (a visible data-catch line: the limit that changes the takeaway)")
    if p.open_details:
        fails.append(f"page: {p.open_details} <details> open by default (Go deeper starts closed)")
    od = p.dfn.get("opener", [])
    if len(od) > 1:
        fails.append(f"opener: {len(od)} <dfn> terms {od} (only the topic's own name may be one)")
    learn(od[:1])
    if reg.get("opener"):
        hard, soft = terms_in(reg["opener"])
        hw = sorted({w for w in hard_words(reg["opener"]) if w.lower() not in known_words})
        if hard:
            fails.append(f"opener: technical terms before the story starts: {', '.join(hard[:8])}")
        if soft:
            warns.append(f"opener: everyday words on the term list ({', '.join(soft)}): check the sense")
        if hw:
            warns.append(f"opener: rare words {', '.join(hw[:8])}")
        if quantities(reg["opener"]):
            warns.append(f"opener: quantities {' '.join(quantities(reg['opener'])[:6])} (give each a scale the reader can picture, or move it)")
        symbols("opener", reg["opener"])

    ids = p.step_ids
    if not ids:
        fails.append("story: no data-step sections")
    elif ids != [str(k) for k in range(1, len(ids) + 1)]:
        fails.append(f"story: step ids {' '.join(ids)} (want 1 to {len(ids)} in order, each once)")
    if len(ids) > LIMITS["max_steps"]:
        fails.append(f"story: {len(ids)} steps (max {LIMITS['max_steps']}; a bigger topic needs a guided path)")

    for n, key in enumerate(ids, 1):
        text = reg.get(key, "")
        dfns = p.dfn.get(key, [])
        hard, soft = terms_in(text)
        new = sorted(set(hard) | {d for d in dfns if d not in known_terms})
        learn(dfns + hard + soft)
        unexplained = sorted({w for w in hard_words(text) if w.lower() not in known_words})
        words = WORD.findall(text)
        sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if WORD.search(s)]
        avg = len(words) / max(len(sents), 1)
        qs = quantities(text)
        labels = [t for on, t in p.labels if on is None or key in on]
        tag = f"step {key}"
        rows.append({"step": key, "words": len(words), "avg_sentence": round(avg, 1), "quantities": qs,
                     "new_terms": new, "unexplained": unexplained, "labels": len(labels)})
        if n == 1 and new:
            fails.append(f"{tag}: step 1 starts from what the reader knows; found terms {', '.join(new[:8])}")
        elif n == 2 and new:
            warns.append(f"{tag}: a term in step 2 ({', '.join(new[:4])}); is it needed this early?")
        if len(new) > LIMITS["step_terms"]:
            fails.append(f"{tag}: {len(new)} new terms ({', '.join(new[:8])}); max {LIMITS['step_terms']}")
        soft = [t for t in soft if t not in dfns]  # introduced on purpose with <dfn>
        if soft:
            warns.append(f"{tag}: everyday words on the term list ({', '.join(soft)}): check the sense")
        if unexplained:
            warns.append(f"{tag}: rare words never introduced: {', '.join(unexplained[:8])}")
        if len(qs) > LIMITS["step_quantities"]:
            warns.append(f"{tag}: {len(qs)} quantities ({' '.join(qs[:8])}): keep the ones the answer stands on, each with a scale the reader can picture")
        elif n <= 2 and qs:
            warns.append(f"{tag}: quantities {' '.join(qs)} this early; keep only one the reasoning needs, with a scale")
        symbols(tag, text)
        for lab in labels:
            symbols(f"{tag} label '{lab[:30]}'", lab)
        if len(labels) > LIMITS["labels"]:
            fails.append(f"{tag}: {len(labels)} diagram labels visible (max {LIMITS['labels']}; hide what this step does not need)")
        if len(words) > LIMITS["max_words"]:
            fails.append(f"{tag}: {len(words)} words (max {LIMITS['max_words']}, heading and caption included)")
        elif len(words) > LIMITS["warn_words"]:
            warns.append(f"{tag}: {len(words)} words (aim for {LIMITS['warn_words']})")
        if avg > LIMITS["avg_sentence"]:
            warns.append(f"{tag}: average sentence {avg:.1f} words (aim for {LIMITS['avg_sentence']})")
    if reg.get("catch"):
        symbols("catch", reg["catch"])
    return {"steps": rows, "fails": fails, "warns": warns, "terms_listed": len(terms),
            "wordfreq": bool(zipf_frequency)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("page", help="HTML file, or - for stdin")
    ap.add_argument("--terms", help="topic term list, one per line (# comments allowed)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        html = sys.stdin.read() if a.page == "-" else open(a.page, encoding="utf-8").read()
        terms = []
        if a.terms:
            terms = [l.split("#")[0].strip().lower() for l in open(a.terms, encoding="utf-8")]
            terms = [t for t in terms if t]
    except OSError as e:
        print(f"cannot read input: {e}", file=sys.stderr)
        return 2
    r = check(html, terms)
    if a.json:
        print(json.dumps(r, indent=1, ensure_ascii=False))
    else:
        if not r["wordfreq"]:
            print("WARN wordfreq missing: rare words are not checked (pip install wordfreq)")
        if not terms:
            print("WARN no --terms list: the topic's own jargon is only caught when it looks unusual")
        for s in r["steps"]:
            print(f"  step {s['step']}: {s['words']} words, avg sentence {s['avg_sentence']}, "
                  f"quantities {s['quantities'] or '-'}, new terms {s['new_terms'] or '-'}, labels {s['labels']}")
        for w in r["warns"]:
            print("WARN", w)
        for f in r["fails"]:
            print("FAIL", f)
        print("PASS" if not r["fails"] else f"{len(r['fails'])} failure(s)",
              f"({len(r['warns'])} warning(s) to review)" if r["warns"] else "")
    return 1 if r["fails"] else 0


if __name__ == "__main__":
    sys.exit(main())
