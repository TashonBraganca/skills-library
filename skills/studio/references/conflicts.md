# When specialists disagree

Order: the owner's words, then the project's `DESIGN.md`, `PRODUCT.md` or tokens, then the
specialist that owns the area below. Only one builder owns a surface; the other gives review notes,
and a note that breaks the owner's house rules goes to the owner instead of into the code.

| Area | Owner | Notes |
|---|---|---|
| Reference hunt, board, direction choice | studio step 0 | The owner picks. `antialgorithm` widens the options; taste-skill's "Design Read" line names each one. |
| Build of a Persuade surface (company site, landing, product page, shop, portfolio) | studio, from the approved direction | taste-skill is a toolbox here (copy checks, single components, finish gate); its full flow and house rules apply only when the owner picks it as builder. impeccable's craft floor and critique review the page. |
| Build of an Operate, Read or Experience surface (app UI, dashboard, tool, docs, game UI) | impeccable | Its mode decides how bold to be. Its craft floor applies to every edit. taste-skill does not build these (its own scope excludes dashboards and multi-step product UI). |
| Marketing copy and imagery on an impeccable page | taste-skill references | `copy-voice.md`, `copy.md`, `photos.md` as guidance only. |
| Component interaction details | emil-design-eng | States, focus, popovers, forms, the small things. Applies under both builders. |
| Physical motion, gestures, depth, the feel review | apple-design, gestures | Springs and interruptible motion for direct manipulation. |
| Whether something animates, and how | animate, choreograph | "Should it move at all?" comes first. Rich motion is the default on creative work; animate may remove a piece only when it fails a task, accessibility or budget requirement, or slows a frequently used control, and says which. |
| Timelines and scroll-linked motion | GSAP skills | Do not drive the same property of the same element with GSAP and Motion. |
| React component state and layout animation | Motion | Pick one library per element. |
| Frame budget | animation-performance, gsap-performance, threejs-performance | Prefer compositor-friendly DOM motion and verify it under load. For 3D, measure frame time, draw calls and transfer separately. |
| Final checks | the builder's gate first, then the cross-review in studio §3.4, then the browser pass in §3.5 | taste-skill: `node <taste-skill>/scripts/gate.mjs` and its checklist; `consistency.mjs` (1440, 1024, 768, 390) and `copy-lint.mjs`. impeccable: finish review, `critique`, `audit`. Treat each FAIL as a defect to fix or to waive with a written reason. |

Resolve routine conflicts against the approved direction, the platform, accessibility and the
measured budget. Ask the owner only when the choice changes the agreed outcome.

## Owner rules beat specialist defaults

- taste-skill's photo library and `picsum.photos` placeholders come from Unsplash. The owner bans
  Unsplash, so they are never used. (Found 2026-11-19: 548 Unsplash entries in `assets/photos/photos.json`.)
- Ship only the assets the page references, never a specialist's whole library.
