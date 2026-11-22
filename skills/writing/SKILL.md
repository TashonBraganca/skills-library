---
name: writing
description: Write, edit or humanize prose people will read. Make it easy and enjoyable from the first line, then use the humanizer and prose checker to catch AI tells. Use for "write a doc/README/spec/report/post", "draft an email", "edit this doc", "make this clearer", "make it fun", "make it readable", "humanize", "unslop", "remove AI tells", "sounds like AI", "STE100", "simplify the English", and "disambiguate". Covers documents, proposals, research reports, PR bodies and procedures people follow. Teaching a topic goes to learn-fast.
---

# Writing

Lead with the most interesting true point. Write for what the reader needs to know or do. Make the
draft easy to follow and worth reading from its first line.

## Choose the task

- **Write or edit prose:** follow the drafting and final checks below. For style-only edits, keep
  the author's voice, meaning and level of certainty.
- **Humanize or unslop existing prose:** follow `references/humanize.md` and preserve every fact,
  number, link and qualifier. Use the drafting guide as you rewrite, within the requested scope.
- **Write a procedure, runbook or error message, or use STE100:** follow `references/ste100.md`.
  Put the action and its conditions first. Use the technical lint check and preserve literal commands,
  units and field names.
- **Write a paper or research report:** use `scientific-writing` if the ML pack provides it. Tie each
  claim to its source, and follow the drafting and final checks below.

## Draft for the reader

1. Find who will read it, what they know and what they need next. Collect the real numbers,
   examples and sources before drafting. For a longer document, outline the reader's questions in
   the order they will ask them.
2. Answer in the first sentence. For an explanation or recommendation, follow with one verified
   case, result or consequence the reader cares about: the detail that makes them read on. Define
   an unfamiliar term when the reader first needs it. In a procedure, put the action and its trigger
   first. Lead each paragraph with its point; use short, plain sentences and the same word for the
   same thing. Headings say the point. End a paragraph on a real question only when the next one
   answers it. `references/fun.md` has before-and-after examples if the opening is flat;
   `references/tech-writing.md` covers technical docs.
3. Use the material you have. Match the author's voice and certainty. Keep procedures brisk and bad
   news direct. Use wit only where it fits the reader and the facts. Never invent a fact.

## Check what the reader gets

1. Ask one question this reader needs the draft to answer. Answer it using only the draft. For a
   procedure, walk through an allowed case and a case where the reader must stop. Fix any answer
   that needs guessing.
2. Humanize: read the whole draft for repeated sentence patterns, inflated claims and chatbot
   leftovers, with `references/humanize.md` and the 33-pattern catalog in `references/ai-tells.md`.
   Run `python3 ~/.skills-library/skills/writing/scripts/prose_check.py <file>` (or stdin). Fix every
   HARD flag in editable prose. Copy quotes, titles and literals exactly; mark a literal the checker
   should skip with `--allow "exact text"`. Use the sentence stats and the dense-jargon flag to find
   lines to reread, and check unfamiliar terms by meaning: short sentences full of jargon still score
   as easy.
3. Verify facts, numbers, names, links, quotes and certainty against the source. Read the opening
   cold: the reader gets the point in the first two lines.

For STE, run `ste-lint.py --baseline 0 --max-words 20` for instructions and `--max-words 25` for
descriptions. Check mixed passages separately. Read for one action per step, long noun groups, and
preserved conditions, negations, units and modality.
