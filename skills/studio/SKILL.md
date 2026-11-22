---
name: studio
description: Conductor for websites, landing pages, app UI, components, design systems, animation, interactive 3D, and video or motion-graphics assets. Hunts design references widely (Dribbble, 21st.dev, Godly, Awwwards, Codrops, three.js examples) and real assets, shows the owner a reference board and 3 sketched directions (one bold) to pick from, then runs the specialist skills (taste-skill v2.5, impeccable, Emil Kowalski's apple-design, emil-design-eng and animate, antialgorithm, GSAP, three.js, Remotion, HyperFrames) each for what it does best. Use for "build/redesign/polish a site or UI", "make it look good", "find design references", "inspiration for", "what should this look like", "animate this", "scroll effects", "3D scene", "promo or explainer video", "hero video", and any frontend change where quality matters. Not for copy-only, config or backend changes.
---

# Studio

You keep one plan and route each part to the specialist that owns it. The owner wants pages that
are really nice, fun and full of motion, made from real references, never the default AI look.

## 1. Pick the route first

| Route | When | Steps | Check |
|---|---|---|---|
| Direction | "find references", "what should this look like" | §2 | `--route direction` |
| New or redesigned web | a page, site or surface without a settled look | §2, then §3 | `--route web` |
| Scoped edit | a button, a section, one animation, a fix | §4 | `--route scoped` |
| 3D | a scene or 3D hero | §5 (plus §3 if it sits in a page) | `--route 3d` |
| Video | a promo, explainer or hero video file | §6 | `--route video --video <file>` |

Mixed jobs apply each route to the thing it delivers. If `DESIGN.md` already settles the look and
the owner did not ask for a new one, skip §2. Run
`python3 ~/.skills-library/skills/studio/scripts/studio_check.py . --route <route>` before handoff
and fix every FAIL. Ask the owner before any subagent, including a specialist's reviewer agent.

**Load the specialists you route to.** Look in this order: the Skill tool list,
`./.claude/skills/<name>/SKILL.md`, `./.agents/skills/<name>/SKILL.md`,
`~/.skills-library/packs/.cache/*/**/<name>/SKILL.md`. Read the file itself, never a memory of it.
If all four miss, name the pack and offer `python3 ~/.skills-library/packs/install_pack.py add
<pack> --project .` (ask first). Record each one in `DESIGN.md` under `## Skills used`: the skill,
the file you read, and the decision or finding it supplied.

## Who owns what

| Work | Owner |
|---|---|
| Persuade surfaces (company site, landing, product, shop, portfolio) | You build from the chosen direction. Taste v2.5.1 is a toolbox: its copy checks, single components and finish gate. Run its full flow only when the owner picks it as builder. |
| Operate, Read, Experience surfaces (app UI, dashboards, tools, docs, game UI) | `impeccable`: `shape`, then new work, craft floor on every edit |
| Every component (states, focus, popovers, forms, toasts) | `emil-design-eng` |
| Drag, sheets, drawers, gestures, the "does it feel right" pass | `apple-design` with `gestures` |
| Whether something moves, and how | `animate` first (it asks how often a control is used), then `choreograph`, GSAP or Motion |
| Open creative choices: directions, concepts, names, layouts | `antialgorithm` (it steers away from the first, most average idea, including yesterday's clever one) |
| One palette, type or stack question | one scoped `ui-ux-pro-max` search |

One builder per surface; others review. Conflicts: `references/conflicts.md`.

**The owner's taste beats house rules.** Where a specialist would flatten the chosen direction (a
"90% neutral, one accent" ratio, no playful copy, no tilt, dealt layouts), keep the direction and
note the override in `DESIGN.md`. In the 2026-11-19 test those rules sanded a bold, playful page into
generic pastel SaaS, and a plain run with no skills made the more fun page.

**Owner bans:** no Unsplash, ever, including taste-skill's photo library and `picsum.photos`. Real
photos only from Wikimedia Commons with the licence recorded; otherwise product UI, illustration,
SVG or CSS art. Ship only the files the page uses.

## 2. References and direction

1. **Read the room.** Page kind, audience, the owner's vibe words, links or screenshots they gave,
   brand assets. One line: "Reading this as: <kind> for <audience>, with a <vibe> language."
2. **Hunt wide.** At least 30 distinct candidates from at least 5 source types (award galleries,
   SaaS and landing galleries, Dribbble shots, component libraries such as 21st.dev, motion and 3D
   showcases, type foundries; `references/sources.md`). Search the feeling and the interaction, not
   only the category: "playful fintech onboarding", "3D hero product". Log each in
   `design/candidates.txt`: `<url> <source type> <keep|drop> <four-word reason>`. A gallery listing
   is where you find references; keep the site or the single shot inside it.
3. **Capture 10 to 15 kept references**: `python3 ~/.skills-library/skills/studio/scripts/ref_board.py
   --out design/refs --mobile <urls>`. Open every screenshot. Replace BLOCKED, FAILED and LISTING
   captures. A "needs review" capture counts once you open it and set its status to "approved". If
   the browser cannot launch, use screenshots the owner gave or images you can open directly, and
   say which sources you could inspect.
4. **Annotate** each kept reference in `design/refs/refs.json`: `why`, `borrow` (one concrete thing:
   a type scale, a hero structure, a motion beat), `avoid`. Rebuild: `ref_board.py --out design/refs
   --file design/refs/refs.json --render-only`. Never copy a reference's code, copy, images or
   signature effect.
5. **Name your default look** in one line before proposing (cream background, big serif or quirky
   grotesque, sticker shapes are common ones). A direction uses a default trait only when a kept
   reference supplies it.
6. **Sketch 3 directions that really differ,** with `antialgorithm`. All three use the same real
   hero content (the product's actual headline and one real detail from the brief), so the owner
   compares composition and motion, not copy. One is bold: motion-led, 3D, illustration or a
   striking type idea. Don't build the whole look from a literal picture of the subject (ledger
   paper for accounting); a real product detail is welcome. Screenshot each first screen into
   `design/sketches/` and link them from the board.
7. **Show and ask.** In chat: the board path, the 3 names with one line each, your pick and its
   trade-off. At most 120 words. Ask with AskUserQuestion (in Codex, ask and stop) when the
   direction is the owner's to choose; when the brief says to choose yourself, choose.
8. **Record it** in `DESIGN.md`: `## Approved` (the picked direction's hero structure, visual motif
   and motion idea) and `## Borrowed` (rows for type, palette, hero, layout rhythm, motion; at least
   4 cite a kept reference file and name the decision taken; a row with none says "default").

## 3. Build a new page, site or surface

1. **Plan:** the user task, real copy and proof points, asset sources and rights, breakpoints, and
   budgets (initial transfer, frame time). Prototype the riskiest media or interaction first.
2. **Build** with the owning builder from the approved direction. Then `emil-design-eng` on every
   interactive component, and `apple-design` with `gestures` for anything dragged or sheet-like.
3. **Motion.** Rich motion is the default for creative and marketing work. Read `animate` first and
   write `## Motion plan` in `DESIGN.md` before motion code: each moving element, its trigger, its
   owner (CSS, WAAPI, Motion or GSAP), its duration, and one **signature moment** with a job in the
   story. Frequent controls stay quick. For GSAP, read `gsap-core` and the ScrollTrigger, timeline
   or React skill that applies before writing GSAP code; one motion owner per element. Reduced
   motion keeps the same content and task. Content is visible at rest; never wait on a scroll
   observer to show text.
4. **Finish:** the builder's own gate, then a cross-review (impeccable `critique` and `audit`, or
   taste-skill's `consistency.mjs` and `copy-lint.mjs`), `review-animations` for motion, and an
   `apple-design` feel pass on interactions.
5. **Exercise the shipped page** in a browser at 1440 and 390 wide. Save full-page captures to
   `design/final-1440.png` and `design/final-390.png` and open every section of both. Compare them
   with the approved sketch: hero structure, motif and motion idea; record any change and why. Drive
   the main task by keyboard and touch; check focus, reduced motion, console errors, and that no text
   sits under another element. Public pages: title, description and crawlable content.
6. **Corrections:** when the owner corrects the design, `learn-taste` proposes rules; write only the
   ones the owner approves into `DESIGN.md`.

## 4. Scoped edit

Read the code and any `DESIGN.md`. Use the matching `impeccable` refine command (`layout`,
`typeset`, `clarify`, `adapt`, `harden`, `bolder`, `quieter`, `animate`) on that target only, and
`emil-design-eng` or `apple-design` for its interaction details. Keep the existing identity, tokens
and layout. Check the change in a real browser: keyboard path, focus, 390 px, reduced motion, and a
before/after capture. Record what you checked.

## 5. 3D

Check the installed three, React and React Three Fiber versions; keep the stack unless migration is
in scope. `threejs-fundamentals` or `threejs-react-three-fiber`, then only the topic skills the
scene needs. Plan loading, fallback and disposal first. Finish with `threejs-performance`: frame
time, draw calls and transfer measured, and a static fallback that keeps the task usable.

## 6. Video and motion graphics

One engine owns each file (`references/pipelines.md`): Remotion for React compositions, HyperFrames
for HTML compositions, `huashu-art-motion` for a storyboard-led art explainer. Render the final file,
run `studio_check.py . --route video --video <file> --seconds <n> --size <WxH>`, look at frames from
the start, middle and end, and play it once. Report the measured properties. Registry feedback and
paid media need the owner's say-so.
