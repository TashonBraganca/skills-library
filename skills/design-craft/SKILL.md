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

Research must reveal both how strong finished work is constructed and what active or spatial material
could make this interface possible. Study Behance, Dribbble, Awwwards, live products, and other useful
finished work for composition, hierarchy, pacing, crop, and interaction. Search for video, motion,
interactive code, shaders, 3D work, textures, type, and imagery that suit the subject. These are paths
to consider, not ingredients that every interface must contain.

Do not choose a lead while the evidence consists only of static references, a typeface, and the
category's usual photograph. Put that option beside moving, interactive, or spatial material that
could change the construction. Then choose the reference, asset, or combination with the strongest
specific idea. This comparison is the bridge between gathering material and committing to a design.

Use the available sources below, or reach the same kind of source with the tools you do have.

```
video <query> [source] shippable video
polyhaven <query>      CC0 models, HDRIs, textures
github3d <query>       open-source WebGL and 3D projects, with licences
codrops <query>        MIT interaction and WebGL demos
magicui <query>        named motion component candidates
repo <github-url>      download the selected repository for inspection
fetch <direct-url>     download the selected remote asset
bits [Name]            React Bits components and source
t21 <query>            component previews
fontshare [query]      typefaces
dribbble <terms>       reference work
motion <query>         motion references
landinglove <query>    full-page motion recordings
landing <query>        landing-page references
palettes <directory>   measure imagery when imagery leads
```

`github3d`, `codrops`, and `polyhaven` find candidates. Use `repo` or `fetch` to bring the selected
source or asset into the work. The other download commands return local material directly. `dribbble`,
`motion`, `landing`, `t21`, and galleries provide work to study. If a command is unavailable, use web,
code, or file tools to inspect the same kind of source. Missing tooling is not permission to skip it.

Inspect what you fetch. Open images at useful size. Inspect a video's opening, development, ending,
camera movement, loop, resolution, and usable crop across time. Run and inspect code before adapting
it. When selected code depends on bundled models, textures, images, or media, inspect those dependencies
before deciding what the construction will carry forward. A filename, one video frame, thumbnail,
search result, or description is not inspection.

Do not use Unsplash or let generic stock photography lead the work. Before building around a photograph,
inspect what its subject, moment, crop, light, or texture gives this exact composition. If the answer
could describe any image in the category, choose a different photograph or lead. Photography remains
available when it is commissioned, documentary, archival, product-specific, or strongly art-directed.

The final construction must carry the strongest inspected material or adapted interaction source.
A typeface alone does not complete material research. Give the selected material a concrete job. It
may carry the first viewport, set the crop and light, reveal a state change, make data legible, create
depth, or change how a person moves through the interface. Do not reduce it to a token background,
proof-of-research thumbnail, or decoration that could disappear without changing the page.

Rejecting every candidate returns you to research. Change the query, source, or kind of material and
inspect the new result before coding. Once a useful candidate or combination gives the interface an
idea worth building, select it, integrate it, and stop collecting. Do not finish with only hand-authored
DOM, CSS, and SVG after researching active or spatial material.

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
produce a clearer payoff. Give the construction a current decision trail: name the inspected
source or material that determines its palette, type, space, and motion. Category references may explain
the product, but choose visual language from evidence that changes those decisions. If the decision trail
matches recent work, research a different source before coding. Improve the same idea instead of
decorating it with unrelated effects.

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

Treat a familiar treatment as an unmade decision. Name what in the present brief, inspected reference,
or selected material requires each major choice. When nothing does, return to the lead and derive the
choice from its geometry, light, content, or behavior. Any style remains available when that evidence
calls for it.

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
