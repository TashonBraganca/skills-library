---
name: design-craft
description: Build web interfaces that look designed rather than generated - visual direction, measured colour, fluid gesture-driven motion, real fetched assets, and a self-review pass that catches what reading the code cannot. Use when building or reshaping any UI, landing page, dashboard, product site, or interactive piece; when output looks generic or "AI-generated"; when choosing a palette, typeface, or motion behaviour; or when reviewing a build for craft before shipping.
---

# Design craft

Every rule here was derived by building ten pages with five different design skills across two models,
then measuring what actually separated the work a person liked from the work they rejected. Where a
number appears, it came from that measurement, not from taste.

Motion sections marked **[EK]** are absorbed from Emil Kowalski's `apple-design` and `emil-design-eng`
skills (MIT). See `LICENSE-THIRD-PARTY.md`.

## The sequence — this ordering is the whole thing

Skipping straight to code is what produces generic work. Do these in order:

1. **Commit to a direction in writing** before any markup. Name the subject, the audience, the one job
   of the page, and the single aesthetic risk you are taking. Three sentences, not a document.
2. **Pick the palette from `references/palettes.md`** or measure your own — never invent hexes.
3. **Build.**
4. **Screenshot it and look at it.** Then fix what you see. This step is not optional and it is the one
   most likely to be skipped. See *Self-review*.

## Colour — the measured law

Two gates. `scripts/measure_palette.py <url|file>` checks both and exits non-zero on failure.

| Gate | Threshold | Evidence |
|---|---|---|
| Hue spread | **>= 17 deg** | Liked pages measured 17.6-41.5 deg; rejected pages 3.1-10.3 deg |
| Median chroma | **30-53 %** | Liked measured 33-51 %; rejected measured 56-87 % |

Together these reproduced all 9 scored human verdicts. **They were fitted on those same 9 pages**,
so a PASS means "inside the band this person liked", not "this design is good". Treat it as a floor
that catches the known failure, not a substitute for looking.

**Readability is a separate concern and is not a taste signal.** Run `scripts/check_contrast.py` for
WCAG AA (it walks the DOM, since pixel-area contrast measures the wrong thing entirely). But know
that in testing, the page a reviewer called unreadable *passed* every WCAG check, while their
favourite page *failed* thirteen small labels. Fix real AA violations because accessibility matters —
do not expect the ratio to tell you whether a design reads well.

**Two or three genuinely different hue families, each held quiet.** The failure mode is not brightness,
it is *one hue tinting everything* — teal-on-black, lime-on-black, purple gradients. That measured at
3-10 deg of spread every time it was rejected. A forest green against a terracotta against near-black
measures 79 deg and reads as considered.

Corollaries:

- **Neutrals are chosen, not inherited.** Bias greys slightly toward the accent's hue. `#0e0e0e` and
  `#f4efe9` are decisions; `#111` and `#f5f5f5` are defaults.
- **No grain or noise overlays.** Explicitly disliked on review ("the noise background is terrible"),
  and it is the single most common AI-design tell.
- **Never let a colour's only definition live inside a media query or `[data-theme]` block.** Define the
  full palette on bare `:root`, then redefine *only tokens* under the variants.

## Light and dark are two committed modes, not one hedged one

Pick one per project and execute it fully. Hedging produces the muddy middle.

**Dark** — near-black ground (`#0b0c0d`-`#1a1a1b`), body text >= 7:1 against it, chromatic accents at the
low end of the chroma band because saturation reads hotter on black. Restraint matters more here.

**Light** — warm off-white ground (`#f4efe9`, `#f0f0ef`), ink near-black, one earth accent. Rarer in
generated work, so it reads as less machine-made. If you go light it must be *clean*: real whitespace,
strict alignment, no decorative filler.

A page may use both as *sections* — a dark hero into light content — provided each section commits.
That pattern was singled out as the strongest of ten.

## Motion — behaviour, not animation **[EK]**

The difference between "fine" and "alive". Every rule below is about the interface responding to a
person rather than playing a clip at them.

- **Respond on pointer-down, never on release.** Feedback must be continuous *during* the gesture, not
  only at its end. Drag, slider, drawer: update 1:1 with the pointer the whole way.
- **Interruptibility is the most important principle.** Every animation must be grabbable and reversible
  mid-flight. Never lock out input during a transition.
- **Always animate from the presentation (current on-screen) value, never the target.** Reading the
  target on interrupt causes a visible jump. This one line prevents most janky motion.
- **Avoid CSS transitions and `@keyframes` for anything gesture-driven** — they cannot be smoothly
  grabbed and reversed. Use springs, which animate from the current value by default.
- **Springs, in Apple's two parameters** — damping ratio (overshoot) and response (seconds to target),
  not mass/stiffness:

  | Interaction | Damping | Response |
  |---|---|---|
  | Move / reposition | 1.0 | 0.4 |
  | Rotation | 0.8 | 0.4 |
  | Drawer / sheet | 0.8 | 0.3 |

  Default to **damping 1.0** (no bounce). Add bounce *only* when the gesture itself carried momentum —
  a flick or a throw. Overshoot on a menu that merely faded in feels wrong.
- **Hand off velocity at release** so there is no seam between dragging and animating.
- **Project momentum** — animate to where the gesture is *going*, not to the nearest snap point from the
  release position. Apple's actual function, not the physics-textbook one:

  ```js
  const project = (v, rate = 0.998) => (v / 1000) * rate / (1 - rate);
  const target = nearestSnapPoint(current + project(releaseVelocity));
  ```
- **Spatial symmetry.** What slides in from the right dismisses to the right. Anchor `transform-origin`
  to the element that triggered it, never to the centre.
- **Rubber-band at boundaries** — resist progressively instead of stopping hard.
- **Honour `prefers-reduced-motion`** with a branch that renders every final state statically. Test it.

What reviewers actually praised in the bake-off, unprompted: cursor-tracked 3D that could be dragged,
an object that fell to the bottom of the frame on scroll, hovering a list row lighting the exact
corresponding band of a 3D model. All three are *direct manipulation*, not entrance animation.

## Assets — you cannot judge what you cannot see

Text-returning search tools make asset selection impossible. Two failures were measured directly:

- Agents given only text search produced **zero** images across five builds and fell back to gradients.
- Agents that "searched" without verifying reproduced **identical Unsplash photo IDs** across runs that
  never communicated — they were reciting IDs from training data, then confirming the URL resolved, and
  reporting it as research.

The fix is mechanical:

1. `scripts/scrape_inspo.py` — pull real candidates via Scrapling (Dribbble for direction, motionsites
   for video, landinghero for layout reference, reactbits for components). Dribbble needs
   `StealthyFetcher`; plain HTTP gets a 202 challenge.
2. **Download candidates to disk.**
3. **Look at them.** Read the actual image files, judge crop, light, subject and mood on the pixels.
   A caption is not a photograph.
4. Verify every URL you ship returns `200` with `content-type: image/*`. Never reference a remembered ID.
5. Prefer CC0/CC-BY sources for anything embedded. Dribbble is *direction*, not stock — do not
   redistribute other designers' work as your asset.

Procedural is a legitimate answer. Hand-authored SVG, canvas and WebGL produced the strongest work in
the set. If you go procedural, commit — do not scatter grey placeholder boxes where a real asset belongs.

## Break the attractor

Given an open brief, models collapse onto the same few subjects and palettes. Measured: three of five
Opus builds independently invented a deep-sea product and **two independently named it "HADAL"**; the
GPT builds independently converged on acid lime. An 87 KB ban-list did not prevent either.

Naming the attractor out loud is the only intervention that worked. So:

- Before committing to a subject, write down the **first three ideas you thought of and discard them.**
  Those are the attractor.
- Known attractors to avoid unless the brief demands them: deep-sea / abyssal / submersibles, space and
  orbital telemetry, "the city at night", acid lime or electric purple on near-black, Inter and Roboto,
  Space Grotesk as the "safe interesting" face, glassmorphism, three equal feature cards in a row.
- Decorative `01 / 02 / 03` markers are allowed **only** when the content is genuinely a sequence.

## UX and layout

- **Lay out with flex/grid and `gap`**, never per-element margins that collapse or double.
- **Running text near 65 characters.** Set a type scale and stay on it.
- **Wide content scrolls inside its own `overflow-x: auto`** container. The page body must never scroll
  sideways — verify at 390 px.
- **`font-variant-numeric: tabular-nums`** anywhere digits align in a column.
- **Every interactive element needs a visible focus state** and a >= 44 px touch target.
- **Copy is design material.** Name things as a person recognises them. A control says exactly what
  happens. Errors state what went wrong and how to fix it.
- **Structure must encode something true.** An eyebrow, a divider, a number is information or it is noise.

## Numbers must reconcile — gates that halt

Every build that gated its numbers caught a real error; every build that eyeballed them shipped one.
Measured examples: a bell weight stated as 669 kg while its own `12-2-19` notation computed to 1419 lb;
a page claiming 51.7 % carbon-free while its data computed 72.7 %.

- **Compute derived figures at runtime and overwrite the authored values.** Copy cannot then drift.
- **`throw` on violated invariants — do not log.** Series lengths equal; components sum to their total
  within tolerance; no negative residuals.
- State the units. State `n`. Never present a proxy as a measurement.

## Self-review — the step that gets skipped

After you believe it is finished, and before you report anything:

1. **Screenshot it** at 1440 px and at 390 px. Scroll to at least three positions and screenshot each —
   entrance animations mean the top of the page is not the page.
2. **Look at the screenshots.** Then ask specifically: is the hierarchy right, is anything unreadable,
   is anything overlapping, does the eye flow, is there anything I would be embarrassed by.
3. **Run the gates**: `measure_palette.py`, contrast, `node --check` per script block, every external
   URL returns 200, no horizontal overflow at 390 px.
4. **Then improve the UX** — not just fix bugs. Ask where the interface could be more informative or
   more direct, and do that. Nothing in the bake-off did this unprompted, and it showed.

### Real bugs this pass caught, that reading the code did not

Check for these by name — each shipped in a page that looked structurally perfect:

- **`gsap.from()` leaves an element at `opacity: 0` forever** if the tween never completes. Make the
  final visible state the CSS default and animate *away* from it, so failure leaves content visible.
- **A dead CDN URL silently kills an entire WebGL scene.** `three@0.161.0/build/three.min.js` and
  `cdnjs/three.js/r160/three.min.js` both 404 — the UMD min build was dropped after r147.
  `three@0.160.0/build/three.min.js` is verified working. Test the URL, do not assume the version.
- **A canvas that never paints** because its draw sits behind an IntersectionObserver that never fires.
  Guard it so it renders unconditionally as a fallback.
- **A heading collapsed to nothing** from `max-width: 16ch` inside a flex context. Use
  `inline-size: min(16ch, 100%)`.
- **Light shafts emanating from the bottom** of a scene lit from above. Only a screenshot catches this.

## When verifying is impossible, say so

If a screenshot could not be captured, if a browser was shared and reassigned your tab, if an
interaction needs a real click you never performed — **report that plainly as unverified.** Do not
describe pixels you have not seen. A stated limitation is worth more than a confident guess.
