---
name: design-craft
description: Building or reshaping any UI - a landing page, portfolio, dashboard, app screen, interactive piece. Use when choosing direction, palette, typography, motion or assets, when sourcing images or 3D, or when output looks generic or AI-generated. For checking that a built UI actually works, use design-review.
---

# Design craft

Work like a design lead at a studio known for giving every client a look that could not be
mistaken for anyone else's. This client has already rejected templated work. Make deliberate,
specific choices and take one real risk you can defend.

Nothing here fires automatically. Read the brief first, then pull only what fits.

## 1. Read the brief before you touch anything

Name these to yourself:

- **Page kind.** Landing, portfolio, marketing site, dashboard, app screen, data tool, editorial.
- **Audience.** A procurement panel, a design-conscious consumer, a recruiter scanning, an athlete
  mid-workout. The audience picks the aesthetic, not your taste.
- **Vibe words the user used.** "Calm", "Linear-style", "Apple-y", "brutalist", "playful", "premium".
- **Reference signals.** URLs, screenshots, products or competitors they named.
- **Existing brand material.** Logo, colour, type, photography. On a redesign these are starting
  material, not optional input.
- **Quiet constraints.** Accessibility-first audiences, regulated industries, kids' products. These
  override aesthetic preference.

Then state one line, out loud, in your reply:

> Reading this as: `<page kind>` for `<audience>`, in a `<vibe>` language, leaning toward `<direction>`.

Keep it in the reply. Do not write it to a file. It is a step in your reasoning, not a deliverable.

If the read genuinely diverges, ask exactly one question. If you can infer it, do not ask.

## 2. Do not land in the slop

Generated design collapses into a small number of looks. They appear regardless of subject, which
is what makes them read as machine output. Land in one of these by default and the work is dead on
arrival, however well executed.

**The three clusters:**

1. Warm cream ground near `#F4F1EA` with a high-contrast serif display and a terracotta accent.
2. Near-black ground with one bright acid-green or vermilion accent.
3. Broadsheet layout: hairline rules, zero border-radius, dense newspaper columns, a masthead.

**Concretely avoid as defaults.** Backgrounds `#f4efe9`, `#f5f1ea`, `#f7f5f1`, `#faf7f1`, `#efeae0`,
`#ece6db`. Accents in the brass, clay, oxblood and ochre family. Warm espresso near-blacks like
`#1a1714`. Display serifs `Fraunces` and `Instrument Serif`, the two most-reached-for. Body `Inter`
as a reflex. Glassmorphism on everything, AI purple and blue glows, three equal feature cards,
centred hero over a dark mesh, numbered `01/02/03` markers on content that is not a sequence.

## Never build a sidebar

**Hard rule, no exceptions. Never put a side navigation panel in any interface you build.** Not in a
dashboard, not in an app, not in a tool, not in a settings screen, not collapsed, not
icon-only, not behind a hamburger, not "just for desktop". This is not a default to weigh against
others. It is banned outright.

The vertical rail with an icon and a label per item, current one in a tinted pill, is the reflex
answer to every dashboard brief. It appears whether the product has four destinations or forty, it
eats a fifth of the width before any content exists, and it makes every app look like every other
app.

Navigate some other way, and choose deliberately between them:

- **A top bar.** Keeps the full width for content, and reads as a product rather than a console.
- **A command palette.** Right for a tool people return to daily and already know their way around.
- **A bottom dock**, when there are three to five destinations.
- **Contextual navigation**, where the object on screen offers its own next steps. Often better than
  any global chrome.
- **Nothing persistent at all.** A focused product with four destinations does not need a permanent
  rail advertising them.

If the user explicitly asks for a sidebar, build it and say once that you would have chosen
otherwise. Absent that instruction, there is no brief that justifies one.

**Serif discipline.** "Creative brief, therefore serif" is the single most-tested tell. Default to a
sans display. Reach for a serif only when the brand names one, or the direction is genuinely
editorial, luxury, publication or heritage **and** you can say why this serif fits this brand.

**These are defaults to avoid, not bans.** When the brief asks for one of these looks, the brief
wins, every time. What is forbidden is spending a free axis on them because they came to mind first.

**Break the attractor.** Given an open brief, models converge. Write down the first three ideas you
had, discard them, and reach for the fourth. Naming the convergence is what makes agents abandon it.

## 3. Set three dials from the read

These replace fixed thresholds. They are read-dependent, and they drive every layout, motion and
density decision that follows.

- **VARIANCE** 1 = perfect symmetry, 10 = artful chaos
- **MOTION** 1 = static, 10 = cinematic and physical
- **DENSITY** 1 = gallery, airy, 10 = cockpit, packed with data

| The read says | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| minimal, calm, editorial, Linear-style | 5-6 | 3-4 | 2-3 |
| premium consumer, Apple-y, luxury | 7-8 | 5-7 | 3-4 |
| playful, agency, experimental, Awwwards | 9-10 | 8-10 | 3-4 |
| landing or portfolio, no other signal | 7-9 | 6-8 | 3-5 |
| dashboard, data tool, app screen | 4-6 | 4-6 | 6-8 |
| trust-first, public sector, regulated | 3-4 | 2-3 | 4-5 |

State the three values alongside the design read.

## 4. Go and look at real work. This is a gate.

You cannot judge design from memory, and text search returns captions rather than pixels. Agents
given only text search produced zero images across five builds, and agents that "searched" without
looking recited identical stock IDs across runs that never communicated.

`scripts/scrape_inspo.py` downloads to `./inspo/` and prints paths.

```
scrape_inspo.py dribbble <t> <t>…  direction. The best source. Give several sibling terms.
scrape_inspo.py motion             real .mp4 motion references
scrape_inspo.py codrops <q>        MIT web-effect demos with working source. Best source of flair.
scrape_inspo.py bits               lists the 100+ React Bits components by category
scrape_inspo.py bits <Name>        downloads that component's actual MIT source
scrape_inspo.py github3d <q>       open-source 3D and WebGL, prints repos with licences
scrape_inspo.py polyhaven <q>      CC0 HDRIs, textures and 3D models. Public domain.
scrape_inspo.py fontshare [q]      free quality typefaces outside the Google Fonts default set
scrape_inspo.py t21 <q>            21st.dev component previews, quality varies by query
scrape_inspo.py landing            landing layout references
scrape_inspo.py mobbin <tag>       real shipped product UI (usually login-gated, expect a fail)
scrape_inspo.py palettes <dir>     measure a folder of images into a palette
```

**Dribbble is the strongest source.** Use a specific multi-word tag: `fitness tracker dashboard`
returns far better work than `fitness`, which returns logos and mascots.

`bits` returns **source code, not screenshots**. Run it bare to see the catalogue, which includes
things like `ClickSpark`, `Aurora`, `MetaBalls`, `GradientBlinds` and `ImageTrail`, then pull the
one you want. It is MIT: adapt it and keep the attribution rather than hand-building a worse version.

`t21` quality swings with the query. A vague one returns filler. `mobbin` is normally login-gated and
exits with a message rather than pretending. When a source fails, use another and say which failed.

**One search is not research.** Run at least three sources, and these are not optional:

- **A direction source**, `dribbble` or `t21`, always.
- **`motion`**, whenever your MOTION dial is above 4. These are real `.mp4` files of interfaces
  moving, and they are the only way to learn what good motion looks like rather than guessing at it.
  Watch them. A page built without ever looking at motion reference comes out still.
- **`bits` or `t21`** before you hand-build any component that already exists there. React Bits is
  free. Reimplementing a component that someone already made well is wasted effort and worse output.
- **`github3d`**, whenever a signature moment could carry 3D, WebGL, canvas or shader work. Check the
  licence, keep the attribution.

**Search the subject's world, not the brief's literal word.** One tag is not a search. `fitness`
returns mascots and tiger logos. Give `dribbble` three or four sibling terms and let it pool them:

```
scrape_inspo.py dribbble "fitness tracker dashboard" running swimming strength-training
```

The neighbouring terms are where the good work hides, because everyone else searched the obvious one.

### Then compose, do not imitate

The point is never to reproduce one reference. It is to end up better than any of them.

1. **Open every file and look at it.** Judge crop, light, colour, rhythm and layout on the pixels.
   For motion clips, watch what moves, how fast, in what order, and what deliberately stays still.
2. **Throw most of them away.** Keep four or five that have something real in them.
3. **Pick one as the base.** The one whose overall structure and mood best fits this brief. That
   decides the skeleton: layout, density, where the weight sits.
4. **Go through the others and take what is genuinely worth taking, and nothing else.** For each,
   ask whether it holds one idea that beats the base: a chart treatment, a card rhythm, a way of
   handling numbers, a colour relationship, a transition. If it does, graft that one thing on and
   ignore the rest of that reference. If it does not, reject it.
5. **Label every reference `base`, `graft` or `rejected`, and expect most to be rejected.** That is
   the correct outcome, not a failure. A tag search returns mascots, logo sheets and brand studies,
   and binning five of nine is a good hit rate.
6. **Say the composition out loud**, by filename: the base, each graft with the one thing it gave
   and the line of code it landed in, and each rejection with the reason.

**Never invent a graft to give a file a role.** A graft you cannot point at in the finished code did
not happen. Measured: on one build the model claimed a graft from all eight non-base references, and
an honest re-audit found five had been rejected outright. It had described taking "segmented
activity selection" from a picture of a cartoon raccoon. Claiming influence you did not take is
worse than taking nothing, because it destroys the only record of what actually drove the design.

The result is a synthesis nobody has shipped, assembled from parts that each already proved they
work. That is the opposite of copying a shot, and it is the reason to fetch five references rather
than one.

The source list is a starting point, not a fence. If a better site exists for what this brief needs,
go find it and use it. Say which you used and why.

*Gate:* if you shipped without fetching anything, say so in those words and say why. Silently
skipping this step is the most common way the work turns generic. If the environment truly has no
network or no shell, state that, and do not pretend you researched.

## 5. Assets are part of the design, not decoration

A page of text and hand-drawn boxes is not minimalism, it is unfinished.

**Never ship stock-photo-service filler.** No Unsplash, no Pexels, no Lorem Picsum. Those images are
on ten thousand other sites and they read as filler on sight.

**In priority order:**

1. **Image generation**, if any tool is available in the environment. Section-specific assets at the
   right aspect ratio.
2. **Real component libraries.** React Bits is free and good. 21st.dev. Use real components rather
   than approximating them by hand.
3. **3D and WebGL.** Search GitHub, which is the best open source of 3D scenes, shader work and
   animation. When 3D genuinely serves the subject, use it. Check the licence and keep attribution.
4. **Real brand SVGs** for any logo wall, from Simple Icons (`https://cdn.simpleicons.org/<slug>/<hex>`).
   For an invented brand, draw a simple monogram rather than setting the name as text.
5. **Procedural and generative** is legitimate if you commit to it. A grey placeholder box is worse
   than either.
6. **Last resort:** leave clearly labelled slots and tell the user exactly what to supply and at what
   size. Do not fill the gap with div-based fake screenshots or hand-rolled illustration.

**Verify every shipped URL returns 200 with `content-type: image/*`.** A dead CDN link silently kills
a whole scene.

**Let the palette follow the assets.** If the page carries real imagery or a 3D scene, pull the
colour out of it so the two agree. Choosing a palette first and then hunting for images that survive
it is backwards.

**An exceptional asset can lead, not just fill a slot.** Most of the time you design the page, then
find images and components that fit it. Sometimes the order runs the other way: you go looking, and
one of the candidates, a 3D scene, a shot, a piece of found motion, is strong enough that the honest
move is to build the page around it rather than crop it down to fit a layout decided beforehand. This
is a real option, not a step you owe every build. Reach for it only when something you actually found
earns it, say what you found and why it earned the lead, and never force a mediocre asset into this
role just because you went looking and want to show for it.

**A real bloom or glow effect is now cheap enough to use properly.** three.js ships its own
`EffectComposer` / `UnrealBloomPass` / `OutputPass` pipeline (official, MIT, in the `three` package
itself under `three/addons/postprocessing/`), current as of whatever three.js version you installed.
Reach for the real pipeline rather than faking glow by layering transparent meshes, which reads as
soft and inaccurate next to the real thing. Include `OutputPass` after the bloom pass or the result
tone-maps wrong and looks washed out, a common mistake in older tutorials. Vanta.js ships the same
plexus/network-sphere look and is genuinely MIT, but its last npm release was 2022 and current
GitHub issues report breakage against recent three.js, so building the effect directly against
current three.js addons is the safer path, more code, no frozen dependency underneath it.

Spline (spline.design) community scenes carry a commercial-use licence, but the free tier watermarks
every embed, so treat it as something to consider only when a paid seat is already part of the
project, not as a free asset source.

## 6. Colour, type, layout

**Colour.** Two or three genuinely different hue families, each held quiet, is the shape that reads
as considered. One hue tinting everything is the failure. Bias neutrals toward the accent so they
read as a decision. Lock one accent for the whole page: a warm-grey site does not grow a blue button
in section seven. Commit fully to light or dark and do not flip mid-scroll. Define the full palette
on bare `:root` and redefine only tokens inside media queries, since a colour defined solely behind
a query never applies in the unstamped state.

Do not chase a number. There is no chroma band to hit. Judge it against the assets and the subject.

Contrast is a separate axis and is not taste: run `scripts/check_contrast.py` for WCAG AA and fix
real violations. Check every view, not just the one that happens to be open.

**Type.** `references/motion.md` carries Apple's typography detail: optical sizing, size-specific
tracking, leading that tracks size inversely, and building hierarchy from weight, size and leading
as a set. Pair a display and a body face deliberately, and not the pair you would reach for on any
other project. Set a scale and stay on it. Tracking is size-specific: tighten large display text,
leave body near zero, never one value everywhere. Emphasise within a headline using italic or weight
of the same family, never by dropping a serif word into a sans line. Use `tabular-nums` wherever
digits align in a column.

**Layout.** Structure is information: an eyebrow, divider or number either encodes something true or
it is noise. At most one eyebrow per three sections. Use `gap` for repeated spacing rather than
margins as an implicit system. Running text near 65 characters. Grid over flexbox percentage maths.
Wide content scrolls inside its own `overflow-x: auto`, and the body never scrolls sideways at
390 px. Interactive targets 44 px minimum. Once a section layout family is used, do not reuse it on
the same page. A hero must fit the viewport with its CTA visible.

## 7. Build the motion. Do not wait to be told to cut it.

If MOTION is above 4, the page **must actually move**. Not "has transitions in the stylesheet":
move, visibly, to someone looking at it. A static page claiming motion is broken work. If you cannot
ship working motion in the scope available, drop the dial to 3 and ship a clean static page on
purpose. Never half-build motion that breaks.

**Build every one of these, and count them before you ship:**

1. **An entrance.** The page arrives rather than appearing. Stagger the first screen's elements by
   30-80 ms so the eye is led through the hierarchy instead of hit with all of it.
2. **Scroll reveal on every major section.** `whileInView` with `once: true`. One per section, not
   one per page.
3. **Hover on every interactive surface.** Cards, rows, buttons, chart marks. A dashboard where
   nothing responds to the cursor feels dead even when every number is right.
4. **Press feedback on every control**, instant down, eased release.
5. **Transitions between states.** Tab changes, filter changes and data changes animate rather than
   cut. `AnimatePresence` on anything that mounts and unmounts.
6. **Numbers that arrive.** Count a headline figure up, or draw a chart in, once on first view.
7. **One signature moment.** The thing someone would screenshot. A drawn path, a 3D or canvas scene,
   a physics-driven interaction, an orchestrated reveal. This is where 3D from `github3d` or a
   component from React Bits usually earns its place.

A page with only internal state transitions and no reveal, hover or signature has failed this
section, even if the code imports a motion library. Count your `whileInView` and hover handlers: if
either is near zero on a multi-section page, you built a still page with a spring in it.

**Every animation must still be motivated.** Say in one sentence what each communicates: hierarchy,
storytelling, feedback, or a state transition. "It looked cool" is not an answer. The list above is
a floor of moments that need motion, not a licence to animate everything. And absence is a choice
you have to defend too: a page with nothing moving is failing the feedback need, not showing
restraint.

**Read `references/motion.md` before building any of this, and read it properly.** It is Emil
Kowalski's `apple-design` absorbed whole: Apple's *Designing Fluid Interfaces*, *The Details of UI
Typography* and *Principles of Great Design*, translated to the web by the person who wrote Sonner
and Vaul. It carries the real spring numbers, the velocity-handoff maths, the momentum projection
function, the material and translucency rules, and the typography detail. The summary below is a
reminder of what is in it, not a substitute for reading it.

`references/techniques.md` has the recipes and the should-this-animate gate.
`references/motion-vocabulary.md` names the behaviours so you can reason about them precisely.

**Feel, from Apple's fluid-interface work:**

- Respond on **pointer-down**, not on release. Latency is where directness dies.
- **Interruptibility matters most.** A user must be able to grab a moving thing and reverse it.
  Animate from the current on-screen value, never from the target, or you get a visible jump.
- **Springs for anything the user touches.** Damping `1.0` and response `0.3-0.4` as the default.
  Bounce, damping `~0.8`, only when the gesture itself carried momentum, like a flick or a throw.
- **Hand off velocity** from gesture to animation so there is no seam, and project momentum forward
  to pick the landing point rather than snapping from the release point.
- **Symmetric paths.** What slides in from the right dismisses to the right. Anchor popovers and
  sheets to the element that opened them via `transform-origin`.
- **Rubber-band at boundaries** rather than stopping hard.
- Animate `transform` and `opacity` only. Keep per-frame movement below the strobing threshold.

**Reduced motion means a gentler equivalent, not nothing.** Replace slides and springs with short
cross-fades, drop overshoot, and keep the colour and opacity changes that carry meaning.

**Ship full interaction cycles**, not just the happy static state: loading skeletons shaped like the
real content rather than a spinner, composed empty states that show how to fill them, inline errors,
and a physical `:active` response on every control.

## 8. Plan, critique the plan, then build

Work in two passes.

**Pass one, on paper.** A compact token system: four to six named colours, the faces for display,
body and any utility role, a layout concept in a sentence and a rough wireframe, and the single
**signature element** this page will be remembered by.

**Then attack it before writing code.** Work through a similar brief in your head. If you arrive
somewhere similar, the plan is a default rather than a choice: revise that part and say what you
changed and why. Only build once the plan survives.

Do most of this in your thinking. Show the user ideas when you have confidence, not while churning.

**Spend your boldness in one place.** Let the signature be the memorable thing and keep everything
around it quiet. Then remove one accessory before you leave the house.

**Match complexity to the direction.** Maximalist needs elaborate execution, minimal needs precision
in spacing and detail. Elegance is executing the chosen thing well.

## 9. Words are design material

Copy makes a page feel templated as fast as the visuals do.

Write from the user's side of the screen, naming things by what people recognise rather than how the
system is built. Say what something does in plain terms instead of selling it. Active voice, and a
control says exactly what happens: "Save changes", not "Submit". Keep an action's name stable through
the whole flow, so a "Publish" button produces a "Published" toast. One label per intent across the
page. Errors explain what happened and how to fix it, and never apologise. An empty screen invites
an action.

Before shipping, re-read every visible string and rewrite anything grammatically broken, anything
with an unclear referent, any cute-but-wrong wordplay, and any forced metaphor. Plain and boring
beats clever and hollow. Invented precise-looking numbers are banned unless they come from real data
or are labelled as sample.

## 10. Numbers must reconcile

Compute derived figures at runtime and overwrite authored values so copy cannot drift. **`throw` on
a violated invariant**, because a logged warning is not a gate: series lengths equal, components sum
to their total, no negative residuals, and no output where every row is identical. State units and
`n`, and say whether a number is a measurement or a proxy.

## 11. Default stack

Unless the brief or the environment says otherwise:

- **Framework** Next.js App Router with React. Anything using motion, scroll or pointer physics is an
  isolated leaf with `'use client'`.
- **Styling** Tailwind v4. That means `@import "tailwindcss"`, the `@tailwindcss/postcss` plugin, and
  CSS-first `@theme` tokens. There is no `tailwind.config.js` in v4, so do not write one.
- **Motion** Motion, imported from `motion/react`. Never drive continuous values like pointer
  position or scroll progress through `useState`: use `useMotionValue`, `useTransform`, `useScroll`.
- **Icons** one family for the whole project, from Phosphor, Hugeicons, Radix or Tabler. Never
  hand-draw icon paths.
- **Component libraries** `references/ui-libraries.md` covers which to reach for and when.
- **Fonts** `next/font` or self-hosted `@font-face` with `font-display: swap`.
- Check `package.json` before importing anything, and print the install command if it is missing.

**Single-file mode.** When the task calls for one self-contained HTML file, drop the framework and
build with vanilla CSS and JS, keep everything else in this document, and use CSS transitions and
Web Animations for motion. The absence of a bundler is not permission to ship a static page.

## 12. Ship it. Do not audit it.

This is a build skill. Deliver the UI and hand it back.

**This section deliberately overrides the global verification rule in `CLAUDE.md` for UI work.**
That rule exists because five confidently-wrong data results nearly reached a stakeholder, and it is
right for pipelines, models and numbers, where a plausible-looking output hides a broken input. A
front-end build is not that situation: the user is about to look at the thing with their own eyes,
which is the strongest verification available, and they have said plainly and more than once that
they do not want the deep pass here. Measured cost of ignoring this: one run spent 17 minutes and
216k tokens auditing, another spent 24 minutes and had to be killed mid-audit while it rewrote
working code to fix an artifact of its own screenshot method.

Three checks. Nothing beyond them.

1. `next build` (or the equivalent) exits 0.
2. Open it once. Nothing blank, nothing obviously broken.
3. Fix only what is wrong at a glance, in one pass.

**Then stop and hand it over.** Anything that needs a second screenshot to see, a third click to
confirm, or a rewrite to chase is out of scope. Name it in your reply and move on: "the week panel
bars look wrong to me, I did not chase it" is a complete and useful answer. The user decides whether
it is worth a `design-review` pass.

Do **not** invoke `design-review` yourself, ever. It is user-invoked precisely so that a deep audit
happens on request rather than on momentum.

**Do not trust a full-page screenshot for anything animated.** Chrome's beyond-viewport capture
never fires `IntersectionObserver`, so every scroll-reveal element photographs frozen at its initial
state: invisible, zero-height, zero-scale. Verified: a chart whose bars looked entirely missing in a
full-page shot rendered all seven at real heights when actually scrolled into a normal viewport. If
you must check a reveal, use a normal viewport, scroll the section into view, wait, then capture. Or
assert the computed height in the console. Never rewrite working code because a full-page image
looked empty.

Say plainly what you did not verify. That sentence is the deliverable, not a reason to go and verify
it.
