---
name: design-craft
description: Use when building or reshaping any interface, including landing pages, portfolios, dashboards, tools, and interactive pieces. Use when choosing visual direction, studying references, sourcing assets, designing motion, or correcting generic AI frontend work. For a deep review of a built interface, use design-review.
---

# Design craft

Create an interface with a clear point of view. It must help someone do its job and hold one coherent idea
across content, visuals, motion, and interaction. Reject generic AI slop. A competent page that could
belong to any product is unfinished.

## Learn the work

Begin with the subject, audience, task, content, data, code, and real setting. Identify the primary
action, what the audience already knows, its strongest objection, and the available proof. Make a
reasonable assumption for missing context and continue. Find what belongs to this work and nowhere else.
Use that knowledge to judge references and material instead of starting from a familiar component system
or visual treatment.

Treat a format noun in the brief as a description of the information or task, not a command to reuse its
familiar shell. Research the underlying work, direct peers, and useful ideas from outside the immediate
category. The reference set should expand the construction, not average examples of the same layout.
Use direct peers to learn product truth. A repeated category treatment cannot establish the page's visual language by itself; test it against the subject and adjacent work.

## Research construction and material together

Study finished work to learn how strong interfaces control hierarchy, pacing, crop, depth, type, motion,
and interaction. Search for usable material at the same time: film, photography, illustration, sound, 3D
objects, scenes, shaders, textures, motion or interface components, typography, and live data.

Inspect at least one finished moving or interactive reference when motion or interaction belongs to the
brief. A collection of static screens cannot teach timing, continuity, response, or how the experience
holds attention.

When research, references, or asset sourcing are part of the task, read and follow
`references/research-pipeline.md` before searching. It lists the scrapers, asset records, construction
handoff, and completion check for downloads, code, repositories, and media. These routes are paths into
the internet, not a checklist or a limit on useful sources. Do not begin implementation until the
construction has enough inspected evidence and the pipeline's completion check passes.

Before choosing a base, make a short design read from the inspected evidence. Identify the focal element,
visual gravity, text-to-material relationship, depth, pacing, interaction behavior, and the small details
that make the work specific. Keep this internal unless the user asks for it. A mood label is not a design
read because it does not describe a construction.

## Choose a base, then build the ensemble

A finished reference or a piece of material can become the base. Choose the candidate with the strongest
idea for this brief. A reference may lead through its composition and pacing. A material may lead through
its image, movement, space, sound, interaction, or behavior.

State what leads, why it leads, and what a person should notice or understand first. Carry the base's
useful principles into an original construction. The base begins the design. It does not finish the
research.

Set the visual direction before inventing a brand name. Let the name express the direction rather than choose its palette, type, or atmosphere by association.

Find material for the jobs the base cannot perform. A video may establish time and atmosphere. A 3D
object may create space and direct manipulation. A shader may connect input to state. A photograph may
provide subject, light, and crop. A component may give an interaction the behavior it deserves. Type,
texture, sound, and data may contribute in the same way. These are examples of roles, not required items.

Treat a strong find as material to integrate. Test possible roles before rejecting it. A useful candidate
stays when it improves the construction without confusing the task or breaking the experience. Record a
specific reason when a promising candidate does not fit, then search differently if its job remains open.
Do not accept a weak candidate to save searches or context. Keep the full research record available and
pass a construction receipt into implementation as its index, not as a replacement for the evidence.

Test whether a proposed lead is replaceable. Name the observed property that changes the page's geometry,
timing, or behavior, then state what breaks when that material is removed. If another item from the same
category could preserve both answers after a small colour or crop change, the material is illustrating
the category rather than leading the construction. Keep searching or give it a supporting role.

Build an ensemble from as much material as the work supports. After the base works, revisit motion,
interaction, spatial, media, and type candidates for its open jobs. Compare compatible combinations, not
only each candidate against the base. Keep each item that adds a distinct job and make the items affect one another through
shared state, geometry, timing, depth, or material response. Separate panels that merely update together
are an assembly, not an ensemble. Stop when no candidate improves an open job or relationship.

When active or spatial jobs belong to an interactive brief, carry inspected active material and an
inspected interaction implementation into the core construction. The medium remains your choice. If the
first candidates fail, find better candidates or change the construction, then account for the rejected
files.

For interactive work, inspect relevant component and interaction sources before implementing a
substitute. Inspect React Bits as a first-class candidate for React work. Use it when its behavior improves
a core interaction. If another inspected source wins the same job, record why the chosen source performs
that job better. Use Codrops, open-source repositories, and other libraries when they improve another open
job or relationship. An original CSS, SVG, canvas, or WebGL effect does not close an unsearched evidence
family.

The active material must shape the main composition or the main product state. The interaction source
must control that material or another core state. A background flourish and a button hover do not satisfy
these jobs.

## Build the working model

Before coding, form a concrete internal model from the brief, references, selected material, tools,
data, code, and technical limits.

Compare rendered ensemble candidates before approving the direction. Use the same content, viewport, and
loaded material so composition is the variable. For the winner and strongest alternative, record what
the eye meets first, how the materials affect one another, what becomes ordinary when the lead is
removed, and how the spatial and temporal ideas develop. Choose from the rendered evidence, not the
written rationale. When another vision-capable reviewer is available, show it unlabeled renders and the
fixed reference without the candidate rationales, then use its comparison as evidence rather than an
automatic verdict.

Give that model a visual proof. Use an inspected finished reference when one supplies the construction.
If no found reference resolves the composition and a rendering or image-generation tool is available,
make a quick construction study from the selected material and inspect it. The proof is a spatial target,
not a new style source and not a shippable asset by default. Do not let a prose plan approve a composition
that has never been seen.

The proof must resolve the proposed lead in a comparable role. A reference that contributes one useful
rule but leaves the intended crop, scale, layering, or text-to-material relationship unanswered is input,
not proof. Make and inspect a construction study for the unanswered composition.
A construction study can prove that a composition works, not the origin of choices it introduced. Trace its colour, type, atmosphere, and material treatment to outside evidence.
Read the proof without its labels. Its silhouette, bounded regions, focal geometry, and media relationships must still express the idea; prose cannot rename a familiar container pattern into an original construction.

Treat each selected active source as a behavior contract. Record its defining input, response, timing,
depth, visual role, implementation medium, and adaptation boundary. The combined construction study must
demonstrate every selected active behavior in its intended relationship. Separate source demos do not prove
the ensemble, so compare the source and proof in the same role. A static proxy cannot prove active material. If an adaptation crosses its recorded boundary,
reopen selection and compare the changed construction before approving it.

Describe the spatial construction. Place the layers, masks, crops, frames, overlaps, depth planes, type,
data, and controls. Decide how selected material changes scale, light, balance, and reading order. Know
what is present before heavy material loads and how the idea recomposes across viewport sizes and input
methods.

Describe the temporal construction. Define the opening state, development, response, continuity, and
payoff. Decide what persists while other parts change. Time may come from scroll, pointer movement,
gesture, live data, product state, video, sound, or another cause that belongs to the work.

Give every selected item a starting role and behavior. Decide what it reveals, changes, frames, carries,
or lets the person control. Integrate it into the structure. A research thumbnail or removable background
does not count as use.

Judge material at the size, duration, crop, and loading role it will have in the page. Compare the chosen
item with the strongest inspected alternative for that job. Do not let the easiest downloadable file win
when its visible detail or behavior is weaker than the construction needs.

Challenge the model before implementation. Find every region inherited from a familiar product pattern.
Test whether the subject or inspected material can make that job specific to this work, then keep the
simple form or carry the stronger source for a stated reason.
Compare free choices against recurring generated defaults, including familiar palette pairings, repeated
card geometry, ornamental labels, standard navigation frames, and generic hero formulas. Keep a familiar
choice only when the subject or inspected evidence explains it. Change the construction when several defaults
arrive together without that evidence.
Compare the proposed page with the finished reference you inspected. Name the spatial or temporal rule
you carried across and show where it changes this construction. Trace the other major decisions to the
subject or inspected material. If the same reasoning could produce an unrelated project, if removing the
lead leaves the layout intact, or if the page still reduces to familiar format containers, change the
evidence or construction.

## Compose the interface

Let the composition express the subject. Use hierarchy, rhythm, contrast, alignment, negative space,
density, image, and movement as active decisions. Let typography participate through scale, width,
tracking, line breaks, position, and timing. Trace colour, type, and material treatment to an observed
property of the subject or inspected evidence. A category association is not evidence.

Derive navigation from the task and lead composition. Keep a persistent navigation frame only when it
enables frequent movement or commands, and make its shape participate in the composition. Do not import
navigation from a category template.

Make the work itself visible. Translate its objects, actions, measures, and state changes into the
composition instead of placing them inside a generic container and explaining them with labels. Choose a
construction that explains the work and rewards attention.

Place product proof beside the claim it supports. Write specific draft content rather than filler,
invented praise, vague benefits, or suspiciously round data. Break headings where the idea breaks and
inspect their rendered line endings.

Allow the composition to change pace. A persistent object, camera, line, material, sound, or live value
can connect distinct moments. Supporting regions may be quiet or forceful according to their jobs. The
whole interface should feel authored as one experience rather than assembled as interchangeable parts.

## Design behavior and motion

When the interface moves or responds, read `references/motion.md` before planning that behavior. It is a
required part of this skill for motion work. Design interaction and visuals together.

Use causal, interruptible motion that preserves spatial relationships. Give important sequences an opening,
development, and payoff. Review them frame by frame, at normal speed, and with reduced-motion input.

## Build and improve

Use selected sources instead of replacing their defining properties with easier imitations. Adapt them to the project's framework and content without crossing their recorded boundary. Keep the main experience working while optional material loads, and provide a
deliberate fallback when a browser cannot render it.

Build the interactive version early enough to learn from it. Use it with pointer, touch, keyboard, and
scroll where they apply. Compare genuinely different constructions when the direction remains uncertain.
Improve the chosen construction instead of adding unrelated decoration.

Before finishing, ask whether the interface can do more with its strongest material. Confirm that every selected asset performs its job, useful inspected material has a recorded decision, and no major choice came from habit.

## Reconcile the result

After the first working render, perform one visual reconciliation against the approved proof. Compare
silhouette, focal scale, reading order, material relationships, crop, depth, and important motion beats.
Confirm that every selected item remains visible or active in its intended role and that implementation
has not simplified the idea into familiar containers. Repair the largest visual loss, render again, and
inspect the result. Repeat the comparison until the defining composition and selected behaviors survive.
Then stop adding
material that has no open job.

Use `design-review` when the task includes a full mechanical audit. It owns exhaustive browser, state,
accessibility, and responsive verification.

When handing over the work, name the base decision, the references and material that changed the build,
each selected item's job, and any useful candidate that was left out with its specific reason.
