# Video engine choice

| Need | Use | Why |
|---|---|---|
| The site is React or Next.js and the video reuses its components or data | Remotion | Videos are React components; props make variants. |
| Many data-driven variants (per customer, per metric) | Remotion | Parametrised compositions and batch rendering. |
| HTML, CSS and GSAP motion graphics written by the agent, fast iteration | HyperFrames | Plain HTML compositions with a preview and a frame-checked render loop. |
| Ready-made blocks (titles, captions, transitions, charts, 3D) | HyperFrames registry | Installs editable source blocks instead of hand-building. |
| A storyboard-led art explainer, or a specific rendered insert | huashu-art-motion | Has its own storyboard, renderer, QA and delivery gate; it owns the deliverable when chosen. README is mostly Chinese. |
| Recreate a reference video | reverse-any-video (HyperFrames) | Frame-by-frame comparison against the original. |

Both engines render locally and need FFmpeg; HyperFrames needs Node 22 or later. Remotion has its
own licence terms for companies: read the `remotion-license` skill before commercial use.
HyperFrames is Apache-2.0.

## Engine routes

- Remotion: `remotion-best-practices`, preview in `remotion-studio` before composition edits,
  `remotion-markup` while building (time-dependent behaviour uses `useCurrentFrame()`; CSS
  transitions do not render), `remotion-render` after visual review, `remotion-captions` only for
  captioned work. Reuse the site's tokens and static components, not its live animations.
- HyperFrames: its launcher with a verified CLI version, preview or inspect frames, render after the
  check. Registry and media skills only when needed. Its paused-timeline rules override ordinary
  GSAP recipes inside a composition.

## From video to website asset

1. Use the page's tokens (colours, type, radius, easing) in the composition.
2. A decorative loop gets a poster, a pause control if it keeps playing, and a deferred source; the
   reduced-motion path never attaches the source. A user-started explainer keeps its narration and
   has captions.
3. Encode MP4 (H.264) and WebM. Lazy-load below the fold.
4. Measure transfer and LCP with the poster and the real loading policy. Report both numbers.
