---
name: design-review
description: Judge and polish a UI that already exists - find what is unjustified, sluggish, inaccessible or off-personality in its motion and interaction, then fix it in the right order. Use when reviewing a diff or a page for craft, when something "feels off" but you cannot say why, when auditing an app's animations, or when asked to make an interface feel more responsive or more finished. For building new UI, use design-craft instead.
---

# Design review

Judging existing work. `design-craft` is for building it; this is for deciding whether it's good and
what to do about it.

Absorbed from **Emil Kowalski's `review-animations`, `improve-animations` and
`find-animation-opportunities` skills** (MIT — see `LICENSE-THIRD-PARTY.md`). Those three overlapped
heavily; this is the one merged review pass.

## Posture

**Default to flagging. Approval is earned.** A review that finds nothing is usually a review that
didn't look. But every finding must name the rule it violates and propose the specific fix — a
finding without a remedy is a complaint.

**Look at the thing.** Reading the code is not reviewing the interface. Screenshot it, scroll it,
click it. Half the real defects in our own testing were invisible in source and obvious on screen:
light shafts lit from the wrong side, a probe overlapping every section, labels reading `C-01`
against a list saying `R-01`.

## The ten standards

Every animation is measured against these. A violation is a finding.

1. **Justified motion.** It must answer "why does this animate?" — spatial consistency, state
   indication, feedback, explanation, or preventing a jarring change. "It looks cool" on something
   seen often is a block.
2. **Frequency-appropriate.** Keyboard-initiated and 100+/day actions get **no** animation. Tens/day
   gets reduced. Occasional gets standard. Rare gets delight.
3. **Responsive easing.** Enter/exit uses `ease-out` or a strong custom curve. **`ease-in` on UI is a
   block.** Built-in CSS easings are too weak — expect custom cubic-béziers.
4. **Sub-300ms UI.** Slower than that on a UI element needs a stated reason.
5. **Origin and physical correctness.** Trigger-anchored popovers scale from the trigger, not centre.
   Never from `scale(0)` — start at `scale(0.9-0.97)` plus opacity. Modals are exempt, they stay centred.
6. **Interruptibility.** Anything gesture-driven or rapidly retriggered must retarget from its current
   state — transitions or springs, not keyframes restarting from zero.
7. **GPU-only properties.** `transform` and `opacity` only. Animating `width`/`height`/`margin`/
   `padding`/`top`/`left` is a performance finding.
8. **Accessibility.** `prefers-reduced-motion` honoured — gentler, not zero: keep opacity and colour,
   drop movement. Hover motion gated behind `@media (hover: hover) and (pointer: fine)`.
9. **Asymmetric enter/exit.** Deliberate actions animate slower; system responses snap. Symmetric
   timing on a press-and-release is a finding.
10. **Cohesion.** Motion matches the component's personality and the rest of the product. When unsure
    whether motion feels right, **the strongest move is usually to delete it.**

## Flag these on sight

`transition: all` · `scale(0)` entrances · `ease-in` on any UI · animation on a keyboard shortcut or
command palette · UI duration >300ms unexplained · `transform-origin: center` on a trigger-anchored
popover · keyframes on toasts or toggles · animating layout properties · missing
`prefers-reduced-motion` · ungated `:hover` motion · symmetric timing on press-and-release ·
everything entering at once where a 30-80ms stagger belongs.

## Fix in this order

Prefer earlier moves. Most bad motion is fixed by removal, not by tuning.

1. **Delete it** — high frequency, no purpose, or keyboard-triggered.
2. **Reduce it** — shorter, smaller transform, fewer properties.
3. **Fix the easing** — `ease-in` → `ease-out`, weak built-in → strong cubic-bézier.
4. **Fix origin and physicality** — correct `transform-origin`; `scale(0)` → `scale(0.95)` + opacity.
5. **Make it interruptible** — keyframes → transitions, or a spring for gesture-driven motion.
6. **Move it to the GPU** — layout props → `transform`/`opacity`.
7. **Asymmetric timing** — slow the deliberate phase, snap the response.
8. **Polish** — blur to mask a crossfade, stagger a group, `@starting-style` for entry.

## Beyond motion — the rest of the pass

Motion is the most common failure but not the only one. Also check:

- **Readability.** Run `../design-craft/scripts/check_contrast.py`. Fix real WCAG AA violations
  because accessibility matters — but note that in our testing contrast did **not** predict whether a
  page read well: the page a reviewer called unreadable passed every check, while their favourite
  failed thirteen small labels. Use your eyes for "can I read this", the tool for compliance.
- **Colour.** Run `../design-craft/scripts/measure_palette.py`. One hue tinting everything is the
  single most reliable marker of generated-looking work.
- **Hierarchy.** Does the most important thing read first? Squint at the screenshot — whatever survives
  is your hierarchy, whether you intended it or not.
- **States.** Empty, loading, error, and too-much-content. Most generated UI only has the happy path.
- **Overflow.** No horizontal body scroll at 390px. Wide content scrolls in its own container.
- **Numbers.** Do the figures reconcile? Every build in our testing that gated its numbers caught a
  real error; every build that eyeballed them shipped one.
- **Copy.** Does a control say exactly what happens? Do errors say how to fix the problem?

## Output format

A findings table, then a verdict. Nothing else.

| # | Severity | Standard | Where | Finding | Fix |
|---|---|---|---|---|---|

Severity is **block** (ships broken or unusable), **finding** (real defect, should fix), or
**nit** (defensible either way — say so).

Then one paragraph: what is genuinely good here, what must change before this ships, and — stated
plainly — **anything you could not verify.** If you never clicked the interaction, never saw it at
390px, or never captured a screenshot, say that instead of implying you did.
