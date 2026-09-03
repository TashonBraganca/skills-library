---
name: design-craft
description: Building or reshaping a UI - a page, landing page, dashboard, product site, interactive piece. Use when choosing a palette, typeface or motion behaviour, when sourcing images or 3D assets, or when output looks generic or AI-generated. For judging a UI that already exists, use design-review.
---

# Design craft

## Steps

1. **Write the direction before any markup.** Subject, audience, the one job of the page, and the
   single aesthetic risk you are taking. Three sentences.
   *Done when:* the risk is specific enough to argue with.
2. **Derive the palette**, from `references/palettes.md` or by measuring real work with
   `scripts/scrape_inspo.py palettes <dir>`. Never invent hexes.
   *Done when:* `scripts/measure_palette.py` passes.
3. **Build.** Motion principles: `references/motion.md`. Recipes and the should-this-animate gate:
   `references/techniques.md`. Libraries: `references/ui-libraries.md`.
4. **Run `design-review` against your own work** and fix what it finds. Do not self-assess from the
   code; it passes while the page is still wrong.
   *Done when:* no findings remain at block severity, and anything unfixed is named in your report.

## Colour

Two gates. `scripts/measure_palette.py <url|file>` checks both and exits non-zero on failure.

| Gate | Threshold |
|---|---|
| Hue spread | **>= 17 deg** (liked pages measured 17.6-41.5; rejected 3.1-10.3) |
| Median chroma | **30-53 %** (liked 33-51; rejected 56-87) |

**Two or three genuinely different hue families, each held quiet.** The failure is one hue tinting
everything: teal-on-black, lime-on-black, purple gradients. Forest green against terracotta against
near-black measures 79 deg and reads as considered.

These thresholds were fitted on nine pages scored by one person. A pass means "inside the band that
person liked", not "this is good".

- Bias neutrals toward the accent's hue. `#0e0e0e` and `#f4efe9` are decisions; `#111` is a default.
- No grain or noise overlays.
- Define the full palette on bare `:root`; redefine **only tokens** inside media queries and
  `[data-theme]`. A colour defined solely behind a query never applies in the unstamped state.

Readability is a separate axis and not a taste signal: run `scripts/check_contrast.py` for WCAG AA
(4.5:1 normal text, 3:1 large text, where large is 18pt or 14pt bold, roughly 24px or 18.66px bold).
Fix real violations. Do not expect the ratio to tell you whether a design reads well.

## Light and dark are two committed modes

Pick one and execute it fully.

**Dark:** near-black ground (`#0b0c0d`-`#1a1a1b`), body text 7:1 or better, accents at the low end of
the chroma band because saturation reads hotter on black.

**Light:** warm off-white ground (`#f4efe9`, `#f0f0ef`), near-black ink, one earth accent. Must be
genuinely clean: real whitespace, strict alignment, nothing decorative.

A dark hero into light content is fine if each section commits.

## Assets

Text search cannot judge an image. Two failure modes to avoid by name: falling back to gradients
because no image was ever fetched, and reciting a remembered stock photo ID, confirming the URL
resolves, and calling that research.

1. `scripts/scrape_inspo.py dribbble <tag>` for direction, `motion` for video, `landing` for layout.
   Dribbble needs the stealth fetcher; plain HTTP returns a 202 challenge.
2. **Open the downloaded files and look at them.** Judge crop, light, subject, mood on pixels.
3. Confirm every shipped URL returns `200` with `content-type: image/*`.

*Done when:* every asset in the page was opened and its URL verified this session.

Procedural is legitimate. If you choose it, commit: a grey placeholder box is worse than either.
Dribbble is direction, not stock. Embed CC0/CC-BY and keep attribution.

## Break the attractor

Given an open brief, models collapse onto the same few subjects. In testing, three of five agents
independently invented a deep-sea product and two named it identically.

**Write down the first three ideas you thought of, then discard them.** Reach for the fourth.

Naming the convergence is the intervention that works: agents told about it abandoned finished
deep-sea builds and produced genuinely different work. Known attractors: deep-sea and submersibles,
orbital telemetry, "the city at night", acid lime or electric purple on near-black, Inter, Roboto,
Space Grotesk, glassmorphism, three equal feature cards.

## Layout

- Use `gap` for repeated sibling spacing. Do not use margins as an implicit layout system.
- Running text near 65 characters. Set a type scale and stay on it.
- Wide content scrolls in its own `overflow-x: auto`. Verify no body scroll at 390 px.
- `font-variant-numeric: tabular-nums` wherever digits align in a column.
- House policy, not WCAG AA: 44 px minimum interactive target.
- An eyebrow, divider or number is information or it is noise. Numbered `01/02/03` markers require
  the content to genuinely be a sequence.

## Numbers must reconcile

- Compute derived figures at runtime and overwrite authored values, so copy cannot drift.
- **`throw` on a violated invariant.** A logged warning is not a gate. Series lengths equal;
  components sum to their total within tolerance; no negative residuals.
- State units and `n`. Say whether a number is a measurement or a proxy.

## Bugs a screenshot catches and code review does not

- **`gsap.from()` immediate-renders its start state.** Never let essential content depend on a reveal
  completing. On cancellation or teardown, revert or clear the tweened properties; prefer `fromTo()`
  for anything retriggerable.
- **A dead CDN URL silently kills a whole WebGL scene.** three.js deprecated the UMD build in r150 and
  removed it in r161, so `three@0.160.0/build/three.min.js` is the last UMD release. Prefer ESM. Test
  the URL you actually ship rather than trusting a version number.
- **A canvas that never paints** because its draw sits behind an IntersectionObserver that never
  fires. Guard it so it renders unconditionally as a fallback.
- **A heading that collapses in a flex row.** Inspect the item's `flex`, `flex-basis`, `flex-shrink`
  and `min-inline-size` and set the intended basis, for example `flex: 0 0 min(16ch, 100%)`. Setting
  `inline-size` alone does not stop flex shrinking.
- **Light shafts rising from a scene lit from above.**

## Report what you could not verify

If a screenshot was never captured, if a shared browser reassigned your tab, if an interaction needed
a click you never performed, say so in those words.
