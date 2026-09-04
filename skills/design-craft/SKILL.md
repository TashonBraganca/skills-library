---
name: design-craft
description: Building or reshaping any UI - a landing page, portfolio, dashboard, app screen, interactive piece. Use when choosing direction, palette, typography, motion or assets, when sourcing images or 3D, or when output looks generic or AI-generated. For checking that a built UI actually works, use design-review.
---

# Design craft

Work like a design lead at a studio known for giving every client a look that could not be mistaken
for anyone else's. This client has rejected templated work before.

There is no pipeline here. No required order, no checklist to satisfy, no step you owe. What follows
is what is available to you, what is known to go wrong, and what has been banned by name. How you
get from a brief to a good page is your judgement.

## What you can actually fetch

`scripts/scrape_inspo.py` downloads to `./inspo/` and prints the paths. Query any of these with
whatever the subject is.

```
photo <q>          real photography you can ship
video <q> [src]    real video you can ship (two sources, tries both)
polyhaven <q>      CC0 HDRIs, textures, 3D models
github3d <q>       open-source 3D and WebGL repos
codrops <q>        MIT web-effect demos with working source
bits               lists 100+ React Bits components
bits <Name>        downloads that component's real source
t21 <q>            21st.dev component previews
fontshare [q]      free typefaces well outside the Google Fonts set
dribbble <t> <t>…  design shots. Give several sibling terms, not one.
motion             real .mp4 motion references
landing            landing-page layout references
mobbin <tag>       shipped product UI (usually login-gated, expect a fail)
palettes <dir>     measure a folder of images into a palette
```

Some of these return finished material you can put straight in the page (`photo`, `video`,
`polyhaven`, `github3d`, `codrops`, `bits`, `fontshare`). Others return other people's work to learn
from (`dribbble`, `motion`, `landing`, `t21`, `mobbin`). Both are useful, and which you reach for
depends on what you are making. Worth knowing: the second group is where a build naturally drifts,
and it is the group that cannot end up in the page.

This list is a starting point, not the whole internet. It is what happened to verify clean on the
day it was written. If a brief wants something none of these covers, go and find a better source,
use it, and say which one you used. `video` takes an optional source name if you want to pin it to
one.

**Search the subject's world, not the brief's literal word.** One tag is a bad search. `fitness`
returns mascots and tiger logos; `fitness tracker dashboard`, `running`, `strength-training` return
real work. Give `dribbble` several terms at once.

**Open what you download and look at it.** This is the part that matters and the part that gets
skipped. Text search returns captions, and choosing an image from its caption is not choosing an
image. Two measured failures: agents given only text search produced zero images across five
builds, and agents that "searched" without looking recited identical stock IDs across runs that
never communicated.

## What actually happens on these builds, so you can watch for it in yourself

**Nothing ends up in the page.** Measured on one run: 28 reference images opened, 11 motion clips
watched, 77 MB fetched, and the finished page contained none of it. Every pixel was hand-drawn SVG.
No `public/` directory was ever created. Hand-drawing everything is the path of least resistance and
it is usually why a page has nothing real in it. A dense data tool can be genuinely better with no
photography, and that is a fine answer, it is just worth reaching on purpose rather than by never
looking.

**Everything converges.** Five builds of the same brief, across two different models, all produced:
a greeting headline, a readiness score, a weekly bar chart, a route map, a session list, monospaced
numerals, off-white ground, one accent. Given an open brief, models land in the same place. Write
down the first three ideas you had, discard them, reach for the fourth. Naming the convergence is
what makes it stop.

**A weak asset is worse than none.** Smiling person on white, mascots, logo sheets, anything that
could sit on any product in any industry: bin it and ship nothing instead. "It satisfied a rule" is
the worst reason for an image to exist.

## Banned by name

**Never build a sidebar.** No side navigation panel in any interface. Not collapsed, not icon-only,
not behind a hamburger, not "just for desktop". Banned outright, not weighed against alternatives.
The vertical rail with an icon and a label per item is the reflex answer to every dashboard brief,
it eats a fifth of the width before any content exists, and it makes every app look like every
other app. Use a top bar, a command palette, a bottom dock, contextual navigation on the object
itself, or nothing persistent at all. If the user explicitly asks for one, build it and say once
that you would have chosen otherwise.

**Never ship Unsplash, Pexels or Lorem Picsum.** On ten thousand other sites, reads as filler on
sight. `photo` exists so a clean source is available.

**The three looks generated design collapses into.** These appear regardless of subject, which is
what makes them read as machine output:

1. Warm cream ground near `#F4F1EA`, high-contrast serif display, terracotta accent.
2. Near-black ground, one bright acid-green or vermilion accent.
3. Broadsheet: hairline rules, zero border-radius, dense newspaper columns, a masthead.

Concretely: backgrounds `#f4efe9`, `#f5f1ea`, `#f7f5f1`, `#faf7f1`, `#efeae0`, `#ece6db`; accents in
the brass, clay, oxblood, ochre family; espresso near-blacks like `#1a1714`; display serifs
`Fraunces` and `Instrument Serif`; `Inter` as a reflex. Also glassmorphism on everything, AI purple
and blue glows, three equal feature cards, centred hero over a dark mesh, and `01/02/03` markers on
content that is not a sequence.

**Serif discipline.** "Creative brief, therefore serif" is the most-tested tell there is. Default to
a sans display. Reach for a serif when the brand names one, or the direction is genuinely editorial,
luxury, publication or heritage, and you can say why that serif fits that brand.

When a brief asks for one of these looks, the brief wins. What is banned is spending a free axis on
them because they came to mind first.

## Craft worth knowing

**Colour.** Two or three genuinely different hue families, each held quiet, is what reads as
considered. One hue tinting everything is the failure. Bias neutrals toward the accent. Lock one
accent for the whole page. Commit fully to light or dark, do not flip mid-scroll. Define the palette
on bare `:root` and redefine only tokens inside media queries, since a colour defined solely behind
a query never applies in the unstamped state. If the page carries real imagery, pull the colour out
of it so the two agree. There is no number to hit.

Contrast is not taste: run `scripts/check_contrast.py` for WCAG AA and fix real violations, across
every view rather than the one that happens to be open.

**Type.** `references/motion.md` carries Apple's typography detail: optical sizing, size-specific
tracking, leading that tracks size inversely. Tighten large display text, leave body near zero,
never one tracking value everywhere. Emphasise within a headline using italic or weight of the same
family, not by dropping in a serif word. `tabular-nums` wherever digits align in a column.

**Motion.** `references/motion.md` is Emil Kowalski's `apple-design` absorbed whole: real spring
numbers, velocity handoff, momentum projection, interruptibility, materials. Read it before building
motion rather than guessing. The short version: respond on pointer-down not release, animate from
the current on-screen value never the target, springs for anything a user touches (damping 1.0,
response 0.3-0.4 as default, bounce only when the gesture carried momentum), enter and exit along
the same path, `transform` and `opacity` only. Reduced motion means a gentler equivalent, not
nothing. `references/techniques.md` has recipes and the should-this-animate gate.

If a page claims to move, it should visibly move to someone looking at it. Transitions sitting in a
stylesheet that nobody notices are not motion. Equally, a page with nothing moving is a choice you
should be able to defend.

**Layout.** Structure is information: an eyebrow, divider or number either encodes something true or
it is noise. `gap` for repeated spacing rather than margins as an implicit system. Running text near
65 characters. Grid over flexbox percentage maths. Wide content scrolls inside its own container and
the body never scrolls sideways at 390 px. Interactive targets 44 px minimum. A hero fits the
viewport with its primary action visible.

**Copy.** Words make a page feel templated as fast as the visuals do. Name things by what people
recognise, not how the system is built. Active voice. A control says what happens: "Save changes",
not "Submit". Keep a name stable through a flow, so "Publish" produces "Published". Errors explain
what happened and how to fix it. Before shipping, re-read every visible string and rewrite anything
broken, cute-but-wrong, or forced. Invented precise-looking numbers are banned unless real or
labelled as sample.

**Numbers.** Compute derived figures at runtime so copy cannot drift, and `throw` on a violated
invariant rather than logging a warning. State whether a number is a measurement or a proxy.

## Default stack

Next.js App Router with React, Tailwind v4 (`@import "tailwindcss"`, the `@tailwindcss/postcss`
plugin, CSS-first `@theme` tokens, no `tailwind.config.js`), Motion from `motion/react`, one icon
family for the whole project, `next/font` or self-hosted faces. Never drive continuous values like
pointer position or scroll progress through `useState`: use `useMotionValue`, `useTransform`,
`useScroll`. Check `package.json` before importing anything.

For a single self-contained HTML file, drop the framework and use vanilla CSS and JS. The absence of
a bundler is not permission to ship a static page. `references/ui-libraries.md` covers what to reach
for and when.

## Before you hand it over

`next build` exits 0. Open it once. Fix what is wrong at a glance. Then stop.

**This overrides the global verification rule in `CLAUDE.md` for UI work.** That rule is right for
pipelines and numbers, where a plausible output hides a broken input. Here the user is about to look
at the thing with their own eyes. Measured cost of ignoring this: one run spent 17 minutes and 216k
tokens auditing, another was killed at 24 minutes while rewriting working code to fix an artifact of
its own screenshot.

Do not invoke `design-review`. It is user-invoked so a deep audit happens on request, not on
momentum.

**Full-page screenshots lie about anything animated.** Chrome's beyond-viewport capture never fires
`IntersectionObserver`, so every scroll-reveal photographs frozen at its initial state. Verified:
seven chart bars that looked entirely missing rendered at real heights when scrolled into a normal
viewport. Use a normal viewport, scroll, wait, then capture. Never rewrite working code because a
full-page image looked empty.

Naming something you did not chase is a complete answer. "The week panel looks wrong to me, I did
not chase it" is fine.
