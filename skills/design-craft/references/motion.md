# Motion, materials and type

Absorbed from **Emil Kowalski's `apple-design` skill** (MIT — see `LICENSE-THIRD-PARTY.md`), which
distils Apple's *Designing Fluid Interfaces*, *The Details of UI Typography*, *Designing
Audio-Haptic Experiences* and *Principles of Great Design* into web technique. Emil wrote Sonner and
Vaul; this is not secondhand theory.

Read this when building anything a person can touch, drag, scroll or hover.

## The one-line version

An interface feels alive when motion **starts from the current on-screen value, inherits the user's
velocity, projects momentum forward, and can be grabbed and reversed at any instant.**

## Springs, in two parameters

Think in damping ratio and response, never mass/stiffness/damping.

- **Damping ratio** — overshoot. `1.0` = critically damped, no bounce. `<1.0` overshoots.
- **Response** — seconds to reach target. Not a duration; a spring has no fixed duration.

| Interaction | Damping | Response |
|---|---|---|
| Move / reposition | 1.0 | 0.4 |
| Rotation | 0.8 | 0.4 |
| Drawer / sheet | 0.8 | 0.3 |

Default **1.0** everywhere. Bounce only after a gesture carried momentum.

```js
import { animate } from 'motion';
animate(el, { y: 0 }, { type: 'spring', bounce: 0,   duration: 0.4 });  // default
animate(el, { y: t }, { type: 'spring', bounce: 0.2, duration: 0.4 });  // after a flick
```

## Gesture mechanics

- **Tap** — highlight on pointer-*down*, commit on *up*. ~10px hit padding. Allow cancel by dragging
  away, and re-commit by dragging back.
- **Drag** — ~10px hysteresis before committing to a direction, then track 1:1. Use Pointer Events
  with `setPointerCapture` so tracking survives leaving the element. Respect the **grab offset** —
  snapping to the element's centre breaks the illusion instantly.
- **Detect all plausible gestures in parallel** from the first move, then cancel the losers once
  intent is clear. Avoid recognisers that only report a final state (`swipeleft`-style) — they throw
  away the continuous tracking you need for feedback.
- **Decide reverse-vs-commit on velocity sign, not position.**
- **Rubber-band** at boundaries rather than hard-stopping:

```js
const rubberband = (overshoot, dimension, k = 0.55) =>
  (overshoot * dimension * k) / (dimension + k * Math.abs(overshoot));
```

- **Momentum projection** — animate to where the gesture is going. Apple's shipped function, not the
  textbook `v²/2a`:

```js
const project = (v, rate = 0.998) => (v / 1000) * rate / (1 - rate);
const target  = nearestSnapPoint(current + project(releaseVelocity));
```

- **Decompose 2D motion into independent X and Y springs.** One spring on a 2D distance desyncs.

## Frame-level smoothness

Smoothness is about what is *in* the frames, not just the frame rate.

- Animate **`transform` and `opacity` only** — they are compositor-friendly. Hint with `will-change`
  where motion is imminent.
- Keep per-frame positional change below the perception threshold or it strobes.
- For very fast motion, a subtle motion blur or stretch reads better than a hard sharp streak.
- `requestAnimationFrame` is the display-synced clock.

## Materials and depth

Translucency is a functional layer that conveys hierarchy without stealing focus.

- Build nav, toolbars and sheets as translucent layers (`backdrop-filter: blur()` plus a
  semi-transparent background) with content scrolling **underneath** — not opaque fixed strips.
- **Material weight encodes hierarchy.** Heavier materials separate structural regions; lighter ones
  draw attention to interactive elements. **Never stack a light translucent surface on another** —
  legibility collapses.
- **Bigger surfaces read as thicker**: stronger blur, deeper shadow than small chips.
- **Dim to focus, separate to keep flow.** A blocking modal pairs the surface with a scrim and pushes
  the background back. A parallel non-blocking panel uses translucency and offset with **no** scrim.
- **Vibrancy for legibility over changing backgrounds** — higher contrast, slightly heavier weight, a
  small letter-spacing bump. Never flat grey text on glass. Put colour on a solid layer.
- **Scroll edge effects, not hard dividers.** Fade a small blur/gradient mask where content meets
  floating chrome, only where they actually overlap.
- **Materialise, don't fade.** Animate blur radius and scale together on enter/exit so glass reads as
  a real material arriving.

```css
.toolbar {
  background: rgba(255,255,255,.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255,255,255,.4);   /* bright edge = light catching the material */
}
```

## Typography — tracking and leading are size-specific

- **Never one `letter-spacing` for all sizes.** Large display text wants *negative* tracking
  (`-0.02em`); small text wants slightly positive. A fixed value is wrong somewhere.
- **Leading tracks size inversely** — tight on large headings, looser on body.
- **Build hierarchy from weight + size + leading as a set**, not size alone. Weight adds presence
  without consuming space.
- **Spacing in `rem`/`em`, not px**, so a larger user text setting scales the layout with the text.

```css
.display {
  font-size: clamp(2rem, 5vw, 4rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
  font-optical-sizing: auto;
}
```

## Multimodal feedback

1. **Causality** — trigger on the actual causal event; match its character to the action.
2. **Harmony** — visual, sound and haptic must fire on the **same frame**. Latency kills the illusion.
3. **Utility** — reserve haptics and sound for meaningful moments. Over-feedback trains people to
   ignore all of it.

## Reduced motion is three signals, not one

- `prefers-reduced-motion: reduce` — short opacity cross-fades instead of slides/springs/parallax.
  Drop overshoot. Keep colour/opacity changes that aid comprehension.
- `prefers-reduced-transparency: reduce` — raise background opacity, drop the blur.
- `prefers-contrast: more` — near-solid backgrounds with a defined contrasting border.

Also avoid full-viewport moving backgrounds, slow loops near 0.2 Hz, and abrupt brightness jumps.

## Quick reference

| Need | Technique | Value |
|---|---|---|
| Default UI spring | critically damped | damping 1.0, response 0.3-0.4 |
| Flick / momentum | under-damped | damping ~0.8 |
| Gesture to spring | hand off release velocity | `v / (target - current)` if normalised |
| Flick landing | project momentum | `current + (v/1000)·d/(1-d)`, d ≈ 0.998 |
| Clean interrupt | start from presentation value | read the live transform |
| Reversible transition | mirror the easing | inverse cubic-bézier |
| Reverse vs commit | velocity **sign** at release | not position |
| 1:1 drag | Pointer Events + capture | respect grab offset |
| Feedback | on pointer-down, continuous | never only at the end |
| Boundary | rubber-band | progressive resistance |
| Translucent chrome | `backdrop-filter` layer | content scrolls under |
| Type tracking | size-specific | `-0.02em` display, ~0 body |
| Reduced motion | cross-fade | not slide/spring |

## The eight principles, as names to reason with

Purpose · Agency · Responsibility · Familiarity · Flexibility · Simplicity · Craft · Delight.

Two worth quoting directly:

**Simplicity is not minimalism.** Burying everything in one place looks minimal but isn't simple.
Show the common path first, advanced options one level deeper. Sometimes *adding* context simplifies.

**Craft is defensible detail.** Every spacing, timing and alignment value is a deliberate choice you
can defend. Jittery scroll, misaligned icons and layouts that break on rotation read as carelessness.

## Process

- **An interactive prototype is worth "a million static designs."** Build it and play with it.
- **Design interaction and visuals together** — you shouldn't be able to tell where one ends and the
  other begins. Motion is not a layer added after the pixels.
- **Review motion frame-by-frame.** Play it in slow motion to catch what's invisible at full speed.
