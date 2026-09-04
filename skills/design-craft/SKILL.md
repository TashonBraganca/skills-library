---
name: design-craft
description: Use when building or reshaping any interface, including landing pages, portfolios, dashboards, tools, and interactive pieces. Use it when choosing visual direction, studying references, sourcing assets, designing motion, or when a result looks generic or AI-generated. For a deep review of a built interface, use design-review.
---

# Design craft

Make an interface with a clear point of view. It must help someone do its job, but it must also have
an idea that holds together from the first viewport through the last interaction. A clean build that
could belong to any product has failed.

Do not begin from a component library, a card grid, a palette, or the first image search result.
Begin by learning what is distinctive about the subject, its user, and its task. Then study good work
and real material until you can make a design decision with a reason.

## Choose what leads

Either a finished reference or a material can lead the design. Inspect both before deciding.

A reference can lead when its composition is the strongest idea. Study its hierarchy, pacing, crop
logic, depth, material treatment, and how information enters or recedes. Build an original interface
that carries those principles. Do not copy its screen layout, branding, images, copy, or source code.

A material can lead when it has more force than a reference. A film, photograph, 3D model, shader,
texture, animated component, live data object, or typeface may determine the page's scale, light,
movement, and layout. Let the interface grow around it when that produces the stronger result.

Make the decision explicit before implementation: what leads, why it leads, and what the page should
make a person notice or understand first. This is a design call, not a fixed formula. Change it if a
better inspected candidate changes the answer.

## Research material with intent

Study real finished work from places such as Behance, Dribbble, Awwwards, site galleries, and live
product sites. Use them to learn a method, not as a mood board. A useful reference gives you a
specific lesson that changes a decision in the page.

Find material that can ship when the direction needs it. Use the available sources below, or find a
better legitimate source when they do not cover the need.

```
photo <query>          CC0 photography
video <query> [source] shippable video
polyhaven <query>      CC0 models, HDRIs, textures
github3d <query>       open-source WebGL and 3D projects, with licences
codrops <query>        MIT interaction and WebGL demos
bits [Name]            React Bits components and source
t21 <query>            component previews
fontshare [query]      typefaces
dribbble <terms>       reference work
motion                 motion references
landing                landing-page references
palettes <directory>   measure imagery when imagery leads
```

`photo`, `video`, `polyhaven`, `github3d`, `codrops`, `bits`, and `fontshare` can provide material
for the build. `dribbble`, `motion`, `landing`, `t21`, and most galleries provide work to study. Keep
the distinction clear. Inspect what you fetch. Open images at useful size. Sample video frames or
watch the clip. Run and inspect code before adapting it. A filename, a thumbnail, and search text are
not inspection.

Treat a strong find as an opportunity. Select only material you intend to integrate, then give each
selected item a concrete job in the composition. It may carry the first viewport, set the crop and
light, reveal a state change, make a data object legible, create physical depth, or change how a
person moves through the interface. It must not exist as a token background, a tiny proof-of-research
thumbnail, or a decorative layer that could disappear without changing the page.

Choose material that gives the interface an idea worth building. A weak result does not become good
because it was the best item in a batch, and it does not justify falling back to hand-drawn cards.

## Build an internal working model

Before coding, turn the research into an internal working model. Keep it private unless the user asks
to review the direction. It must be concrete enough that another designer could build the same idea
without guessing what the references meant.

Account for what the project actually contains: the brief, content, data, existing code, selected
references, shippable assets, available tools, and technical constraints. Then decide how those parts
become one experience.

Describe the spatial construction. Map any layers, masks, crops, frames, overlaps, depth, type, and
controls that make the idea work. Know how the chosen material changes the page's scale, light, and
balance. A flat image can still create depth through crop, occlusion, type placement, and movement.
Layered assets can act like a stage.

Describe the temporal construction. Know the opening state, how the experience develops, what changes
or responds, what persists while other parts move, and what the payoff is. Time may come from scroll,
pointer movement, a gesture, live data, product state, video, or another cause that fits the work.
This is not a demand for a scrolling story. It is a way to understand how the interface behaves.

Give each selected asset a starting role and a behavior. Decide whether it stays fixed, transforms,
reveals another layer, frames content, carries information, or responds to the person using it. Include
loading behavior in the model. Decide what the first meaningful frame shows before heavy material is
ready, what must arrive early, and what can wait until it is needed.

Preserve the idea across viewport sizes and input methods. Recompose it when shrinking would destroy
the crop, depth, readability, or interaction. Responsive work keeps the experience, not every desktop
coordinate.

Before coding, challenge the first working model. Ask what still looks ordinary, whether the lead could
do more, whether the subject and interface can share depth, and whether an action or transition could
produce a clearer payoff. Improve the same idea instead of decorating it with unrelated effects.

Think in constructions rather than styles. A phone can be the stage for changing product content. A
photograph can hold type between its depth planes. A live value can become the moving object in an
operational tool. These are ways of thinking, not layouts to repeat.

## Make every interface memorable

Every interface needs a focal experience. Its form follows the work. It gives a person a meaningful
change they can see or cause, even when the lead material itself is still.

For a story, brand, or consumer product, the focal experience may be a full-frame scene, film, image
sequence, kinetic type, or an object moving through depth. Type can share the same space as the
subject. It can pass behind it, be clipped by it, respond to it, or create scale against it.

For an operational product, make the work itself the focal experience. A live object, changing state,
time-based process, command interaction, spatial model, or data representation can carry the page.
Do not reduce it to a row of generic metrics when its actual behavior can be shown.

The rest of the interface supports the focal experience. It may be quiet or loud. It may be light or
dark. It may use film, WebGL, photography, code-driven motion, ordinary HTML, or another medium. The
choice must follow the idea, not a habit.

## Build a coherent composition

Give typography an active role. Its scale, width, tracking, line breaks, and position should belong
to the composition. Use a typeface because its character suits the subject or the lead material, not
because it is a familiar default. Use tabular figures where people compare changing numbers.

Take colour from the subject, the lead material, or the real conditions in which the product is used.
Use `scripts/measure_palette.py` when imagery is leading and measurement helps. Do not choose a mode
or accent merely because it is common in generated work. Dark, bright, restrained, saturated, and
full-bleed treatments are all available when they serve the idea.

Motion is choreography, not a collection of entrances. Give it an opening state, development, and a
payoff. Let one thing persist when continuity helps the experience feel like one passage instead of a
stack of sections. The persistent element may be an object, camera direction, device frame, line,
material, or piece of live data.

Choose motion from the idea. A film may set the pace. A mask may uncover space. Type may cross behind
a subject. A working object may change as data arrives. A direct gesture should respond from its
current on-screen state, inherit the person's movement when appropriate, and remain interruptible.
Motion can be quiet or forceful, but it must be visible in the result when it is part of the direction.

Read `references/motion.md` before building involved motion. It carries the interaction mechanics,
springs, momentum, materials, and typography taken from Emil Kowalski's Apple design guidance. Use
`references/techniques.md` when choosing an implementation. Review important movement frame by frame,
then use it at normal speed. Give reduced-motion users an equivalent readable experience.

Render information as the thing it represents when that makes the job clearer. A physical reserve, a
contour, a route, a staged process, or a changing object can say more than the usual ring, chart, or
heat grid. Use conventional controls when convention helps someone act without thought.

Do not spend every section on the same treatment. Do not turn one effect into wallpaper. Let the
composition change pace so the page feels authored rather than assembled from repeated panels.

## Avoid reflexes, not styles

Generated work often reaches for identical rounded cards, a centered heading over a dark mesh, one
bright accent, glass blur, a warm-cream serif layout, generic dashboard chrome, or a decorative
numbering system. These are not forbidden styles. They are warnings that you may be making a choice
before you have a reason.

When a brief asks for one of those treatments, follow the brief. Otherwise, ask what decision in this
specific interface requires it. If there is no answer, choose the treatment that follows the lead.
Do not use a sidebar, a hero image, animation, a serif, a chart, or a gradient by reflex. Use any of
them when the content structure and composition call for it.

## Keep the work real

Use licensed material and preserve required attribution. Check licences for code and 3D material.
Keep a short comment when you adapt a component that identifies its source and what you changed.
Never ship another designer's branded asset, screen-for-screen layout, copy, or source code as your
own work.

Use readable copy, visible keyboard focus, responsive layouts, and controls that say what they do.
Do not invent precise-looking facts. Compute derived values where the interface shows them and state
when a value is sample data or a proxy.

Run `scripts/check_contrast.py` for layouts whose contrast it can measure, then inspect image and
gradient treatments with your eyes. Check the project before importing packages. For a Next.js app,
run the build. Open the page at a normal viewport, use its interactions, scroll it, and inspect the
motion in a real viewport. Full-page screenshots often miss scroll-triggered animation.

When handing work over, name the lead decision, the references or materials that changed the build,
and each selected material's job. State a limitation plainly when one remains.
