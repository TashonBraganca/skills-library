---
name: learn-fast
description: Explain a hard or new topic to the owner so it is easy and fun to follow from the first line - one real case followed from question to result, each step saying why the next one happens, one simple picture that changes with the story, the catch in plain words, and the exact terms, maths and paper details one click away under "Go deeper". Uses the writing skill's drafting guide and humanizer. Chat for a short answer, a page when seeing the change helps, a short guided path for a big topic. Use for "explain", "explain how X works", "teach me", "help me understand", "I don't get", "ELI5", "walk me through", "I need to learn X", "make me an explainer", a paper or concept to learn, or before working in an unfamiliar field. Not for docs or reports (writing).
---

# Learn fast

Goal: the owner gets the idea fast, enjoys it, and can use it on a new case. The default path is a
**plain story**: one real case followed from question to result, a few short steps, a picture that
changes with the story. The exact terms, numbers and maths sit one click away under "Go deeper". A
page that is accurate but hard to follow has failed. So has one that is easy but wrong. Above all,
make it fun to read.

The `writing` skill runs with this one, always (owner's rule). Copy the steps into your task list.
Story and picture rules, with a worked example: `references/flow.md`. Page contract and engine:
`references/explainer.md`. Evidence: `references/learning-science.md`.

## 1. Reader and format

- **Reader:** an adult who is new to this topic. Assume ordinary English and everyday life. Assume
  a technical idea (attention, gradients, an API) only when the owner has shown they know it or says
  "skip the basics". General skill in a field is not knowledge of this topic.
- **Format:** give the answer in the format asked for. Otherwise:

| Need | Format |
|---|---|
| A definition, a quick fact, or a question that fits one screen | Chat: the first sentence is the answer with the number that carries it ("No: only about 8%, one in twelve"), then one worked case and the catch. No page. Stop. |
| A mechanism, a paper, anything where seeing the change helps | One page: opener, 3 to 7 steps, the catch, Go deeper |
| A big topic or a new field | A guided path: a map page, then 3 to 7 short pages, one running case |

For a paper or big topic, first teach the smallest mechanism that answers the owner's question.

## 2. Get it right, quietly

Read the original source (paper, docs, code). Run `research` only when the topic depends on current
or disputed facts. Every number on the page is computed, or traced to the source's figure or table.
For a page, list in `terms.txt` the unfamiliar terms likely to appear: the source's method names,
abbreviations and everyday words with a special sense ("key", "head"). The check reads it.

## 3. Outline the story before any page code

A short outline (`story.md`, format in `flow.md`):

1. **The answer** in one plain sentence a curious 14-year-old could follow: what the thing does,
   then the answer to the owner's own question if they asked one. If they said what they already
   know ("I get that a fridge keeps food cold"), start there and name the one thing they are missing.
2. **Why it matters:** the everyday problem it solves, as a scene with something at stake.
3. **One complete case,** followed from input to outcome: a person asks where a shop is; a fridge
   pushes heat out of its back. Prefer a real case from the source over an invented one.
4. **The steps:** 3 to 7 lines. Each changes one thing in the case and **says why that change
   causes the next**. Show what happens before you name it.
5. **A comparison** only if it carries the mechanism. Pair its parts with the real parts, and name
   one thing the comparison would predict wrongly.
6. **The catch:** the limit that changes the takeaway, in plain words, next to the claim it limits.
7. **The rule, then a fresh case:** state the idea in one plain sentence, then give one new case
   where it predicts something different (the optional "what would happen if...?").

Read the step lines aloud. They must sound like a story told to a friend, each line answering the
question the one before left open.

## 4. Keep the default path light

`scripts/explain_check.py` enforces the hard limits and flags the soft ones for a reread:

- **Show what matters.** Keep on the main path everything the answer stands on: the key formula,
  the headline numbers, the term the field uses. Explain each in plain words right where it
  appears ("stopping distance grows with the square of speed, so twice as fast needs four times the road"). A
  reader who knows the field should never have to open Go deeper to find the core result.
- **Hard limits** (the checker fails these): no term from `terms.txt` in the opener or step 1; at
  most one new term per step; at most 5 visible diagram labels a step; at most 80 words a step; a
  visible catch.
- **Soft flags** (reread, fix if it reads hard): formulas, symbols or 3+ numbers in a step, numbers
  early on, rare words, more than 60 words a step. Give each number a scale the reader can picture
  ("one card in a billion: a stack of paper 100 km high").
- Go deeper (closed by default, one click) holds the detail that does not change the takeaway:
  derivations, full result tables, misconceptions and the honest critique of the source.

## 5. Make it a joy to read and watch

- **Fun, from the first line:** a case with something at stake, a character with a goal, a small
  surprise, playful plain labels ("the clerk", "slow storage"), a satisfying reveal at the end of
  the steps. Light wit where it fits. Never trade accuracy for a joke; label an invented case.
- **Words:** use the `writing` skill's drafting guide and humanizer: answer first, short active
  sentences, one word for one thing. STE structure for steps (`writing/references/ste100.md`).
- **Picture:** one figure per question, the same parts in the same places while the reader follows
  a change. On wide screens the figure and the step text sit side by side, so the reader never
  scrolls between them. Every step changes the picture in a way you can point at.
- **Micro-animation:** animate the one change each step makes (a card slides to the desk, a drawer
  greys out), 200 to 400 ms. Motion that only decorates is cut. Reduced motion shows the same
  before and after with no movement.
- Build the page from `references/explainer.md` (contract and a tested step engine). Follow the
  `artifact-design` skill when publishing as a claude.ai artifact, and `artifact-diagramming` for
  the SVG.

## 6. Check before handing it over

1. `python3 ~/.skills-library/skills/learn-fast/scripts/explain_check.py page.html --terms terms.txt`:
   no FAIL. Read every WARN on the rendered page and fix the ones that read hard.
2. `python3 ~/.skills-library/skills/writing/scripts/prose_check.py page.html`: no HARD flags.
   Grade level is a style signal only: short jargon sentences score "easy".
3. Read the default path aloud with every Go deeper closed. Fix any step that does not say why the
   next one happens. Check that the answer, the catch and what was actually measured are all there.
4. Recompute derived numbers with a script. Trace reported numbers to the source figure or table.
5. Open it in a browser: walk Back/Next and the arrow keys forward and back at 1280 and 390 px,
   then with reduced motion. No horizontal scroll, text beside the figure on wide screens, labels
   readable. Look at screenshots of 3 steps.

## 7. Close the loop

Offer the fresh case from step 3.7 as one optional question, with the answer and the reason behind
a native disclosure. If the owner gets it wrong, fix the step where the story broke.
