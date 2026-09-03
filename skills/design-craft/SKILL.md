---
name: design-craft
description: Building or reshaping a UI - a page, landing page, dashboard, product site, interactive piece. Use when choosing a palette, typeface or motion behaviour, when sourcing images or 3D assets, or when output looks generic or AI-generated. For judging a UI that already exists, use design-review.
---

# Design craft

Every threshold here came from building ten pages with five design skills across two models, then
measuring what separated the work one person liked from the work they rejected. Where a number
appears it was measured, not chosen.

## Steps

Run these in order. Skipping to step 3 is what produces generic work.

1. **Commit to a direction in writing.** Name the subject, the audience, the one job of the page, and
   the single aesthetic risk you are taking. Three sentences.
   *Done when:* those four things are written down and the risk is specific enough to argue with.
2. **Choose the palette from `references/palettes.md`**, or measure one from real work with
   `scripts/scrape_inspo.py palettes <dir>`. Derive hexes, never invent them.
   *Done when:* `scripts/measure_palette.py` passes on your chosen swatches.
3. **Build.** Motion technique is `references/motion.md`; concrete recipes and the
   should-this-animate gate are `references/techniques.md`; libraries are `references/ui-libraries.md`.
4. **Run the `design-review` skill against your own work**, then fix what it finds. Do not
   self-assess from the code; it will pass and the page will still be wrong.
   *Done when:* review returns no findings at **block** severity, and every remaining finding is
   either fixed or named in your report as a known limitation.

## The colour law

Two gates. `scripts/measure_palette.py <url|file>` checks both and exits non-zero on failure.

| Gate | Threshold | Measured evidence |
|---|---|---|
| Hue spread | **>= 17 deg** | liked 17.6-41.5 deg; rejected 3.1-10.3 deg |
| Median chroma | **30-53 %** | liked 33-51 %; rejected 56-87 % |

**Two or three genuinely different hue families, each held quiet.** The failure is not brightness, it
is one hue tinting everything: teal-on-black, lime-on-black, purple gradients all measured 3-10 deg
and were all rejected. Forest green against terracotta against near-black measures 79 deg and reads
as considered.

These reproduced all 9 scored verdicts, but were **fitted on those same 9 pages**. A pass means
"inside the band this person liked", not "this is good". It is a floor, not a judgement.

Choose neutrals rather than inheriting them: bias greys toward the accent's hue. `#0e0e0e` and
`#f4efe9` are decisions; `#111` and `#f5f5f5` are defaults.

Define the full palette on bare `:root`, then redefine **only tokens** inside media queries and
`[data-theme]` blocks. A colour whose only definition sits behind a query never applies in the
unstamped state, which renders one theme's text on the other theme's ground.

Skip grain and noise overlays. They were called out unprompted on review, and they are the most
common generated-design tell.

## Light and dark are two committed modes

Pick one per project and execute it fully. Hedging produces the muddy middle.

**Dark:** near-black ground (`#0b0c0d`-`#1a1a1b`), body text at 7:1 or better, chromatic accents at
the low end of the chroma band, because saturation reads hotter on black.

**Light:** warm off-white ground (`#f4efe9`, `#f0f0ef`), near-black ink, one earth accent. Rarer in
generated work, so it reads as less machine-made, but it must be genuinely clean: real whitespace,
strict alignment, nothing decorative.

A page may run dark hero into light content as long as each section commits. That pattern was the
strongest of the ten tested.

## Assets: you cannot judge what you cannot see

Two measured failures. Agents with only text search produced **zero** images across five builds and
fell back to gradients. Agents that "searched" without looking reproduced **identical stock photo
IDs** across runs that never communicated: they recited IDs from training data, confirmed the URL
resolved, and reported it as research.

The pipeline that fixes it:

1. `scripts/scrape_inspo.py dribbble <tag>` for direction, `motion` for video, `landing` for layout.
   Dribbble needs the stealth fetcher; plain HTTP returns a 202 challenge.
2. Candidates land on disk.
3. **Read the image files.** Judge crop, light, subject and mood on pixels. A caption is not a
   photograph.
4. Confirm every shipped URL returns `200` with `content-type: image/*`.

*Done when:* every asset in the page was opened and looked at, and its URL verified this session.

Procedural is a legitimate answer, and hand-authored SVG, canvas and WebGL produced the strongest
work in the set. Commit to it if you choose it: a grey placeholder box where a real asset belongs is
the one outcome worse than either.

Dribbble is direction, not stock. Embed CC0/CC-BY material and keep the attribution.

## Break the attractor

Given an open brief, models collapse onto the same few subjects. Measured: three of five Opus builds
independently invented a deep-sea product and **two independently named it "HADAL"**; the GPT builds
independently converged on acid lime. An 87 KB ban-list prevented neither.

**Write down the first three ideas you thought of, then discard them.** Those are the attractor.
Reach for the fourth.

Known attractors, listed deliberately: deep-sea and submersibles, orbital telemetry, "the city at
night", acid lime or electric purple on near-black, Inter, Roboto, Space Grotesk as the safe
interesting face, glassmorphism, three equal feature cards.

*A deliberate exception to a rule:* `writing-for-agents` warns that steering by prohibition makes the
forbidden thing more available, and it is usually right. Here the measurement says otherwise. Naming
the convergence out loud was the **only** intervention that broke it: two agents told about it
abandoned finished deep-sea builds and produced a bell foundry and a vinyl cutting room instead. The
list stays.

## Layout and copy

- Lay out with flex or grid and `gap`. Per-element margins collapse and double.
- Running text near 65 characters. Set a type scale and stay on it.
- Wide content scrolls inside its own `overflow-x: auto`. Verify at 390 px.
- `font-variant-numeric: tabular-nums` wherever digits align in a column.
- Visible focus state and a 44 px minimum target on everything interactive.
- Structure encodes something true. An eyebrow, a divider, or a number is information or it is noise.
  Numbered `01 / 02 / 03` markers require the content to genuinely be a sequence.

## Numbers must reconcile

Every build that gated its numbers caught a real error. Every build that eyeballed them shipped one.
Measured: a bell weight stated as 669 kg whose own `12-2-19` notation computed to 1419 lb; a page
claiming 51.7 % carbon-free against data computing 72.7 %.

- Compute derived figures at runtime and overwrite the authored values, so copy cannot drift.
- **`throw` on a violated invariant.** A logged warning is not a gate. Series lengths equal;
  components sum to their total within tolerance; no negative residuals.
- State the units and state `n`. A proxy is not a measurement, and saying which it is costs one word.

## Bugs that only a screenshot catches

Each of these shipped in a page that read as structurally perfect. Check them by name:

- **`gsap.from()` strands an element at `opacity: 0`** if the tween never completes. Make the visible
  state the CSS default and animate away from it, so failure leaves content visible.
- **A dead CDN URL silently kills an entire WebGL scene.** `three@0.161.0/build/three.min.js` and
  `cdnjs/three.js/r160/three.min.js` both 404: the UMD min build was dropped after r147.
  `three@0.160.0/build/three.min.js` is verified. Test the URL rather than assuming the version.
- **A canvas that never paints** because its draw sits behind an IntersectionObserver that never
  fires. Guard it so it renders unconditionally as a fallback.
- **A heading collapsed to nothing** from `max-width: 16ch` in a flex context. Use
  `inline-size: min(16ch, 100%)`.
- **Light shafts rising from the bottom** of a scene lit from above.

## Report what you could not verify

If a screenshot was never captured, if a shared browser reassigned your tab, if an interaction needed
a click you never performed, **say so in those words.** Describing pixels you have not seen is the
one failure that destroys trust in everything else in the report.
