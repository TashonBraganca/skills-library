---
name: design-review
description: Checking that a built UI actually works - a page, a diff, an app's interactions. Mechanics only, deliberately harsh. Invoke it deliberately when you want a build audited; it does not fire on its own. For building new UI, use design-craft.
disable-model-invocation: true
---

# Design review

This pass answers one question: **does it work?**

It does not have taste. It does not decide whether a direction is good, whether a palette is
fashionable, or whether a page has too much personality. Those are the author's calls, made in
`design-craft`. Judging them here produces bland work, because a reviewer with an opinion and a
delete key will flatten anything it did not think of.

So: be mechanical, be exhaustive, and be harsh. Every check below is pass or fail. A finding names
the fix. A finding without a remedy is a complaint.

**You must actually run the thing.** Open it, click every view, resize it, tab through it. A review
performed by reading source is not a review, and it passes while the page is visibly broken.

## Never delete to fix

Removing something is not a fix, it is an amputation. If motion is wrong, correct its easing,
origin, duration or interruptibility. If a component is broken, repair it. Delete only when the
element is genuinely duplicated, or when the author asked for it to go.

The old instinct of "when unsure, cut it" produced pages with no animation, no charts and nothing
memorable. Do not reach for it.

## 1. It runs

- It builds, compiles, or opens with no errors.
- The console is clean. No uncaught exceptions, no failed requests, no missing modules.
- Every asset URL returns `200`. A dead CDN link silently kills a whole scene.
- Every declared dependency is installed and every import resolves.
- Nothing renders as a raw placeholder, a broken image glyph, or `undefined`.

## 2. Every view actually works

- Click every tab, route, filter, toggle and disclosure. Each one renders.
- State changes land everywhere they should. Two panels must never disagree about the same fact.
- Forms accept input, validate inline, and show their error and success states.
- Loading, empty and error states exist and are reachable, not just the happy path.
- Nothing is dead: no button without a handler, no link to nowhere.

## 3. Layout holds

- No horizontal body scroll at 390 px. Wide content scrolls inside its own container.
- Check 390, 768, 1024 and 1440 at minimum. Every multi-column block declares its mobile fallback.
- No text overflows, clips or collapses. Italic descenders are not cut off.
- Button labels fit on one line at desktop. A wrapped primary CTA is a fail.
- Navigation fits one line at desktop.
- The hero fits the viewport with its primary action visible without scrolling.
- No overlapping elements, no content hidden behind fixed chrome.
- Alignment is real. Things that should share an edge share it to the pixel.
- Spacing is consistent. The same relationship gets the same gap everywhere.

## 4. Text is readable

- WCAG AA: 4.5:1 for body, 3:1 for large text at 18pt or 14pt bold. Run `check_contrast.py` from
  `design-craft/scripts/` against **every view**, since a single-view tool misses the rest.
- Button text is readable against its own background. White on white, or a ghost button on a photo
  with no scrim, is a fail.
- Placeholders, helper text, focus rings and error text all pass against their real background.
- No text sitting directly on a busy image without a scrim.

## 5. Motion behaves

Checked only when motion exists. The absence of motion is a `design-craft` question, not this pass.

- **What was claimed is what runs.** If the build says it animates, watch it animate.
- Nothing is `transition: all`.
- No `ease-in` on UI. Things leave on `ease-in`, they arrive on `ease-out`.
- UI transitions stay under 300 ms unless there is a stated reason.
- Press is instant, release is eased. Symmetric timing on a press is a fail.
- Animation is interruptible: grab a moving element and it follows, without a jump.
- `transform-origin` matches the trigger for anything anchored, like a popover or a menu.
- Enter and exit follow the same path.
- Only `transform` and `opacity` animate. No animating layout properties.
- `prefers-reduced-motion` is handled, and handled as a gentler equivalent rather than as nothing.
- `:hover` motion is gated behind `hover: hover`.
- Nothing loops forever without a reason.

## 6. Keyboard and screen reader

- Tab reaches every interactive element in a sensible order.
- Focus is always visible. Never `outline: none` without a replacement.
- Escape closes what it opened. Focus returns where it came from.
- Images carry real `alt` text, or empty `alt` when decorative.
- Headings descend in order. Landmarks exist.

## 7. The numbers are true

- Derived figures are computed, not authored, so they cannot drift.
- Totals reconcile with their components. Series lengths match.
- No `NaN`, no `undefined`, no `Infinity`, no negative residual.
- Nothing is degenerate: if every row is identical, or a value never changes when it should, that is
  broken rather than stable.
- Invented precise-looking numbers are labelled as sample data.

## 8. Copy holds up

- Every visible string is grammatical and has a clear referent.
- One label per intent across the whole page.
- An action keeps its name through the flow.
- No placeholder copy left in, no lorem ipsum, no `TODO` visible to a user.

## Reporting

1. **Say what you ran and on what.** Which views, which widths, which browser. If you could not run
   it, say that first and stop claiming a review.
2. **Every section above is accounted for**, including the ones that produced nothing. Name any you
   could not assess, and why.
3. **Every finding names its fix**, concretely.
4. **Separate blocking from cosmetic.** Blocking means a user hits it and the product is wrong.

The exhaustive bar is the point. "Every check accounted for" forces work that "list what you found"
does not.
