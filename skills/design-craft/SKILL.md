---
name: design-craft
description: Building or reshaping any UI - a landing page, portfolio, dashboard, app screen, interactive piece. Use when choosing direction, palette, typography, motion or assets, when sourcing images, video, 3D or components, or when output looks generic or AI-generated. For checking that a built UI actually works, use design-review.
---

# Design craft

Work like a design lead at a studio known for giving every client a look that could not be mistaken
for anyone else's. This client has rejected templated work before, and has also rejected careful,
correct, forgettable work. Both are failures here. Only one of them feels like one while you are
committing it.

There is no pipeline. No required order, no checklist, no step you owe. What follows is what you can
get hold of, the two ways these builds go wrong, what is banned by name, and craft worth knowing.
How you get from a brief to a good page is yours.

One thing is not optional, and it is the rest of this document's reason for existing: **something
real has to end up in the page.** Everything else is judgement.

## What you can actually fetch

`scripts/scrape_inspo.py` downloads to `./inspo/` and prints the paths.

```
photo <q>          real photography you can ship, CC0, no credit needed
video <q> [src]    real video you can ship (two sources, tries both)
polyhaven <q>      CC0 HDRIs, textures, 3D models, public domain
github3d <q>       open-source 3D and WebGL repos, prints licences
codrops <q>        MIT web-effect demos with working source. The best source of flair.
bits               lists 100+ React Bits components by category
bits <Name>        downloads that component's real MIT source code
t21 <q>            21st.dev component previews
fontshare [q]      free typefaces well outside the Google Fonts set
dribbble <t> <t>…  design shots. Give several sibling terms, not one.
motion             real .mp4 motion references
landing            landing-page layout references
mobbin <tag>       shipped product UI (usually login-gated, expect a fail)
palettes <dir>     measure a folder of images into a palette
```

Two different kinds of thing. `photo`, `video`, `polyhaven`, `github3d`, `codrops`, `bits` and
`fontshare` return **material you can put in the page**. `bits` and `codrops` in particular return
working source code, not screenshots: real components, real shader and canvas work, MIT licensed, and
adapting one is faster and better than hand-rolling the same idea worse. `dribbble`, `motion`,
`landing`, `t21` and `mobbin` return **other people's finished work to learn from**, and cannot end
up in the page. Both matter. The second group is where a build drifts into copying, and the first
group is the one that gets skipped.

**One search is not research.** Reach for several sources, and treat these two as live options rather
than exotic ones: `bits` or `t21` before hand-building any component that already exists there, and
`github3d`, `polyhaven` or `codrops` whenever a moment on the page could carry 3D, WebGL, canvas or
shader work. Checking and deciding against them is a fine answer. Never considering them is not.

**Search the subject's world, not the brief's literal word.** `fitness` returns mascots and tiger
logos. `fitness tracker dashboard`, `running`, `strength-training` return real work. Query style
differs by source and you should expect to adjust: `dribbble` pools several sibling terms at once and
rewards three or four, while the photo sources match on single plain nouns and return nothing at all
for a long phrase. If a source gives you nothing, try it the other way before concluding the well is
dry.

This list is a starting point, not the whole internet. It is what verified clean on the day it was
written, and sources rot: if one returns nothing, read it, fix it or go find a better one, then say
which you used. If a brief wants something none of these covers, go get it.

## The two ways this goes wrong

### Nothing real ends up in the page

Measured on one run: 28 reference images opened, 11 motion clips watched, 77 MB fetched, and the
finished page contained none of it. Every pixel was hand-drawn SVG. No `public/` directory was ever
created. Hand-drawing everything is the path of least resistance and it is usually why a page has
nothing in it.

A worse variant, measured later: 84 files fetched across seven folders, **nine opened**, and the
whole corpus written off as mascots and AI gradients on the strength of that sample. The two best
references in the set were never looked at. One of them was a motion-brand board with contour fields,
halftone dot grids and blurred sprinters that would have carried the entire page. The run then
reported "one usable photo in ten" as diligence while fifty unexamined candidates sat on disk.

So: **open what you fetched. All of it.** A caption is not an image and a filename is not an image.
For video, generate contact-sheet strips of frames and look at those, because an `.mp4` you never
sampled is a file you never saw. Only after you have actually looked are you entitled to a verdict on
what a source gave you.

### It ships, and nobody remembers it

The failure that does not announce itself. Every ban respected, contrast passing, build clean, and
the result is quiet, tasteful and dead. A page that could be swapped into another product without
anyone noticing has failed, however correct it is.

Measured, same brief, two runs. One fetched a React Bits component and adapted its WebGL contour
field into an ambient background, sampled seven motion clips as frame strips and pulled a specific
lesson from them about speed and contrast, and rendered a score as a halftone dot matrix instead of a
ring. It shipped **no photography at all**. The other found one good photograph, placed it once,
built neat computed tables around it, and violated nothing. The first is the one people remembered.

Restraint is not the same as taste. Deciding against something loud is a decision you should be able
to defend, and so is deciding for it. If your page has no moment in it, that is a result you chose.

## The gate

Before you call a page done, at least one of these is true:

- A real photograph or video is in it.
- A real 3D scene, texture, HDRI or shader is in it.
- A real component or effect is in it, adapted from `bits`, `t21` or `codrops`.
- A real typeface you went and got is in it.

If none of them is true, say so in those words and say why none earned its place. That sentence is
allowed. Silently shipping a page of hand-drawn boxes is not.

**This is not a licence to ship filler.** A weak asset is worse than none. A smiling person on white,
a mascot, a logo sheet, dumbbells on a pale wood floor, anything that could sit on any product in any
industry: bin it and ship nothing instead. "It satisfied a rule" is the worst reason for an image to
exist. One boring stock-looking photograph dropped in to clear a gate is exactly the outcome this
gate is not for.

**The good version is composition.** The strongest builds are a synthesis: a fetched component doing
the ambient work, real motion informing how it moves, a typeface with a real voice, and a photograph
or scene that agrees with all of it, none of which came from the same place and all of which look
like they did. Pull the good part out of several things and make them agree. That is the job.

## Banned by name

**Never build a sidebar.** No side navigation panel in any interface. Not collapsed, not icon-only,
not behind a hamburger, not "just for desktop". Banned outright, not weighed against alternatives. It
eats a fifth of the width before any content exists and it makes every app look like every other app.
Use a top bar, a command palette, a bottom dock, contextual navigation on the object itself, or
nothing persistent. If the user explicitly asks for one, build it and say once that you would have
chosen otherwise.

**Never ship Unsplash, Pexels or Lorem Picsum.** On ten thousand other sites, reads as filler on
sight.

**The looks generated design collapses into.** These appear regardless of subject, which is what
makes them read as machine output:

1. Warm cream ground near `#F4F1EA`, high-contrast serif display, terracotta accent. Concretely
   `#f4efe9`, `#f5f1ea`, `#f7f5f1`, `#faf7f1`, `#efeae0`, `#ece6db`, accents in the brass, clay,
   oxblood and ochre family, espresso near-blacks like `#1a1714`, `Fraunces` and `Instrument Serif`.
2. A bright acid-green, neon-lime or vermilion accent, usually over near-black, usually with a
   violet-to-lime gradient somewhere. **The accent is what is banned here, not the dark ground.** A
   dark page is often the right answer, and for a tool used in a gym or at night it is the better
   one. Commit to dark on purpose and hold it, and take the accent from something real rather than
   from the neon shelf.
3. Broadsheet: hairline rules, zero border-radius, dense newspaper columns, a masthead.

Also `Inter` as a reflex, glassmorphism on everything, AI purple and blue glows, three equal feature
cards, a centred hero over a dark mesh, and `01/02/03` markers on content that is not a sequence.

Watch for the second-order version of this. Naming bans moves everyone to the nearest unbanned
corner, and the corner becomes an attractor too: quiet sage or off-white ground, one restrained
accent, a neutral grotesque, tidy computed tables, one photograph. Three separate runs landed there.
If your page would be described that way, you have obeyed the list and lost anyway.

**Serif discipline.** "Creative brief, therefore serif" is the most-tested tell there is. Default to a
sans display. Reach for a serif when the brand names one, or the direction is genuinely editorial,
luxury, publication or heritage, and you can say why that serif fits that brand.

When a brief asks for one of these looks, the brief wins. What is banned is spending a free axis on
them because they came to mind first. Write down the first three ideas you had, discard them, reach
for the fourth. Naming the convergence is what makes it stop.

## Craft worth knowing

**Colour is yours.** There is no palette to pick from here and no number to hit. Build it from
something true: the material the subject is actually made of, the imagery you fetched, the light the
thing is used in. If the page carries real photography or a scene, measure it with
`scripts/measure_palette.py` and take the palette out of what is actually there, so the colour and
the image agree instead of merely coexisting. Two or three genuinely different hue families each held
at the intensity the idea wants is what reads as considered; one hue tinting everything is the
failure. Saturated is allowed. Loud is allowed. Dark is allowed. Full-bleed colour across an entire
viewport is allowed. What is not allowed is a colour that arrived because it was nearby.

Mechanically: define the palette on bare `:root` and redefine only tokens inside media queries, since
a colour defined solely behind a query never applies in the unstamped state. Commit fully to light or
dark, do not flip mid-scroll. Contrast is not taste: run `scripts/check_contrast.py` for WCAG AA
across every view and fix real violations. When that script reports a failure over an image or a
gradient it cannot see, it is wrong and your eyes are right, so look before you change working code.

**Type.** `references/motion.md` carries Apple's typography detail: optical sizing, size-specific
tracking, leading that tracks size inversely. Tighten large display text, leave body near zero, never
one tracking value everywhere. Emphasise within a headline using italic or weight of the same family,
not by dropping in a serif word. `tabular-nums` wherever digits align in a column. Scale is a tool:
type set genuinely enormous, or a number at 200px, does work that no amount of tasteful hierarchy
does.

**Motion.** `references/motion.md` is Emil Kowalski's `apple-design` absorbed whole: real spring
numbers, velocity handoff, momentum projection, interruptibility, materials. Read it before building
motion rather than guessing. The short version: respond on pointer-down not release, animate from the
current on-screen value never the target, springs for anything a user touches (damping 1.0, response
0.3-0.4 as default, bounce only when the gesture carried momentum), enter and exit along the same
path, `transform` and `opacity` only. Reduced motion means a gentler equivalent, not nothing.
`references/techniques.md` has recipes and the should-this-animate gate.

Ambient motion is worth reaching for and easy to get wrong. What was learned from watching real
clips: a field behind content works only when it is slow and low contrast and the type in front of it
never moves. Anything faster than roughly 0.2 Hz reads as strobing.

If a page claims to move, it should visibly move to someone looking at it. Transitions sitting in a
stylesheet that nobody notices are not motion. A page with nothing moving is a choice you should be
able to defend.

**Give the page one moment.** One thing that carries the idea and that someone would screenshot: an
ambient field, a scene, a photograph used at full bleed, type crossing behind a subject, a number at
enormous scale, a transition worth triggering twice. Spreading effort evenly across eight tidy panels
reliably produces a page with nothing in it.

**Render data as the thing it is.** The reflex chart shapes are attractors like any other look: the
readiness ring, the weekly bar chart, the calendar heat grid, the donut. The same value drawn as a
dot matrix, a plate stack, a contour, a physical gauge, or an object from the subject's own world is
usually both more honest and more memorable. Ask what the number actually is before reaching for the
shape that usually holds it.

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

**Licences and credit.** `bits`, `codrops` and most of `github3d` are MIT. Keep the attribution, and
when you adapt a component say in a comment what you changed and why. Check the licence on anything
from GitHub before it goes in.

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

`next build` exits 0. Open it once, at a normal viewport, and scroll it. Fix what is wrong at a
glance. Then stop.

**Once the page builds and you have looked at it, the global verification rule in `CLAUDE.md` no
longer applies.** That rule is right for pipelines and numbers, and it is right earlier in this job
too: checking that you actually looked at all of what you fetched, rather than a sample you then
generalised from, is exactly the discipline it describes. What it is wrong about is the end. Here the
user is about to look at the thing with their own eyes. Measured cost of ignoring this: one run spent
17 minutes and 216k tokens auditing, another was killed at 24 minutes while rewriting working code to
fix an artifact of its own screenshot.

Do not invoke `design-review`. It is user-invoked so a deep audit happens on request, not on
momentum.

**Full-page screenshots lie about anything animated.** Chrome's beyond-viewport capture never fires
`IntersectionObserver`, so every scroll-reveal photographs frozen at its initial state. Verified:
seven chart bars that looked entirely missing rendered at real heights when scrolled into a normal
viewport. Use a normal viewport, scroll, wait, then capture. Never rewrite working code because a
full-page image looked empty.

Say what you fetched, what you used, what you rejected and why, and what you decided not to chase.
Naming something you did not chase is a complete answer. "The week panel looks wrong to me, I did not
chase it" is fine.
