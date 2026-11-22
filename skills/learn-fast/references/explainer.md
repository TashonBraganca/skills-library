# Explainer pages and guided paths

Start from `template.html` in this folder. It is a working page: Back/Next buttons, arrow keys,
step dots, "Show all steps", figure beside the text on wide screens and above it on phones, reduced
motion, and the markup `scripts/explain_check.py` reads. It passes the check and a browser walk at
1280 and 390 px. Replace the story, the figure and the Go deeper text; keep the contract.

When publishing as a claude.ai artifact, follow the `artifact-design` skill (no doctype, html,
head or body tags; theme tokens; title of 2 to 4 words).

## The markup contract

| Markup | Holds | Checked as |
|---|---|---|
| `<div data-opener>` with `<p data-takeaway>` | the question as a title, the answer, why it matters | no listed terms, no symbols |
| `<section data-step="N" data-caption="...">` | one step, numbered 1 to N in order | the budgets in SKILL.md |
| `<g data-show="2 3">` on figure parts | the steps a part is visible in | at most 5 labels per step, plain words |
| `<p data-catch>` | the limit that changes the takeaway | required, visible, no symbols |
| `<details>` (closed) | Go deeper, Try it | never counted; open by default fails |
| `<dfn>` | first use of a word the reader may not know | counts as that step's new term |
| `data-ui` | counters, captions, controls | never counted |

## Go deeper (where precision lives)

- Each step may close with a "Go deeper: the real terms" disclosure that maps the story onto the
  source's words: "The card top is what the paper calls a key."
- The final Go deeper holds the worked example with real numbers, misconceptions (the wrong idea,
  why it tempts, why it is wrong), how far to trust the source, a glossary, and 2 or 3 sources with
  what each adds.

## Interaction rules

- Back/Next with visible labels, arrow keys and step dots. "Show all steps" lays the story out.
- Nothing is locked: every answer is one click away. Practice is optional.
- An interactive control earns its place only if it changes the outcome the reader is predicting.
  It starts in a meaningful state and shows its value.

## Guided path (big topics)

- A map page: chapters as boxes with arrows for prerequisites, a recommended route, and "skip this
  if you already know X" links.
- One running case through every chapter. Each chapter is one page built from the template and
  ends with a fresh case that needs only that chapter's idea.
- One glossary for the whole path.
