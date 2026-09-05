---
name: design-craft
description: Use when building or reshaping any interface, including landing pages, portfolios, dashboards, tools, and interactive pieces. Use when choosing visual direction, studying references, sourcing assets, designing motion, or correcting generic AI frontend work. For a deep review of a built interface, use design-review.
---

# Design craft

Create an interface with a clear point of view. It must help someone do its job and hold one coherent
idea across content, visuals, motion, and interaction. Reject generic AI slop. A competent page that
could belong to any product is unfinished.

## Learn the work

Begin with the subject, audience, task, content, data, code, and real setting. Find what belongs to
this work and nowhere else. Use that knowledge to judge references and material instead of starting
from a familiar component system or visual treatment.

If the brief leaves an important product decision open, make a reasoned proposal. If the missing fact
exists in the project or online, find it. Keep invented sample content visibly identified as sample
content.

## Research construction and material together

Study finished work to learn how strong interfaces control hierarchy, pacing, crop, depth, type,
motion, and interaction. Search for usable material at the same time. Material may include film,
photography, illustration, sound, 3D objects, scenes, shaders, textures, motion components, interface
components, typography, and live data.

Begin search terms with concrete language from the subject, task, content, or needed material. Do not
smuggle an unearned visual direction into the query. A later search may use a style, light, type, mood,
or construction term when inspected evidence gave you that term and you want to pursue it deliberately.

When research, references, or asset sourcing are part of the task, read and follow
`references/research-pipeline.md` before the first search. This is a required part of this skill, not
optional reading. It lists the available scrapers and the completion checks for downloads, code,
repositories, and media. The list is a set of paths into the internet, not a limit on where useful work
may come from. Do not begin implementation until its asset records and research completion check exist.

Look at what you fetch. Open images at useful size. Watch video across its full duration. Run or render
interactive work. Read selected code. Inspect the models, textures, media, fonts, and other dependencies
bundled with a chosen source. A title, description, thumbnail, filename, or first frame is not inspection.
Inspect the current result before starting another batch so the next search can respond to evidence.

## Choose a base, then build the ensemble

A finished reference or a piece of material can become the base. Choose the candidate with the strongest
idea for this brief. A reference may lead through its composition and pacing. A material may lead through
its image, movement, space, sound, interaction, or behavior.

State what leads, why it leads, and what a person should notice or understand first. Carry the base's
useful principles into an original construction. The base begins the design. It does not finish the
research.

Find material for the jobs the base cannot perform. A video may establish time and atmosphere. A 3D
object may create space and direct manipulation. A shader may connect input to state. A photograph may
provide subject, light, and crop. A component may give an interaction the behavior it deserves. Type,
texture, sound, and data may contribute in the same way. These are examples of roles, not required items.

Treat a strong find as material to integrate. Test possible roles before rejecting it. A useful candidate
stays when it improves the construction without confusing the task or breaking the experience. Record a
specific reason when a promising candidate does not fit, then search differently if its job remains open.

Test whether a proposed lead is replaceable. If another item from the same category could preserve the
idea after a small colour or crop change, the material is illustrating the category rather than leading
the construction. Keep searching or give it a supporting role.

Use as much material as the work supports. Each selected item needs a visible job, and the items must
strengthen the same idea. Research is complete when the working model covers its visual, spatial,
temporal, and interactive jobs. Stop when another candidate cannot improve a named open job.

Compare the proposed base with material that could change the construction in a different way before
committing. A static image does not cover temporal or interactive jobs by assertion. Inspect moving,
spatial, or interactive material when those jobs exist, even if you later reject it for a specific reason.

Do not finish an interactive product with only a still image, native shapes, and a hand-authored chart
after researching active material. The accepted construction must carry an inspected active or spatial
material and an inspected interaction implementation when those jobs belong to the brief. The medium
remains your choice. If the first candidates fail, find better candidates or change the construction,
then account for the rejected files.

## Build the working model

Before coding, form a concrete internal model from the brief, references, selected material, tools,
data, code, and technical limits. Keep it private unless the user asks to review it.

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

Challenge the model before implementation. Ask what remains ordinary, what the base could do better,
where useful depth or interaction is still absent, and whether the selected parts truly work together.
Trace the major decisions in this run to the subject, a reference, or inspected material. If the same
reasoning could produce an unrelated project or repeats recent work, change the evidence or construction.

## Compose the interface

Let the composition express the subject. Use hierarchy, rhythm, contrast, alignment, negative space,
density, image, and movement as active decisions. Let typography participate through scale, width,
tracking, line breaks, position, and timing. Let colour come from the subject and selected material.

Make the work itself visible. A process can become a changing object. A reserve can become a physical
field. A route can carry progress. A subject can share depth with typography. A product state can reshape
the scene around it. Choose the construction that explains the work and rewards attention.

Allow the composition to change pace. A persistent object, camera, line, material, sound, or live value
can connect distinct moments. Supporting regions may be quiet or forceful according to their jobs. The
whole interface should feel authored as one experience rather than assembled as interchangeable parts.

## Design behavior and motion

When the interface moves or responds, read `references/motion.md` before planning that behavior. When
choosing how to implement it, also read `references/techniques.md`. These are required parts of this
skill for motion work. Design interaction and visuals together.

Respond on the causal input. Direct manipulation follows the person continuously. Gesture-driven motion
starts from the current visible state, carries velocity when the action supplies it, predicts its outcome,
and remains interruptible. Changes preserve spatial relationships so a person can follow what happened.

Give authored motion an opening state, development, and payoff. Use motion to reveal, explain, orient,
confirm, or let someone act. Review important movement frame by frame and at normal speed. Provide an
equivalent readable experience for reduced-motion input.

## Build and improve

Use selected sources instead of replacing them with weaker imitations. Adapt them to the project's
framework and content. Keep the main experience working while optional material loads, and provide a
deliberate fallback when a browser cannot render it.

Build the interactive version early enough to learn from it. Use it with pointer, touch, keyboard, and
scroll where they apply. Compare genuinely different constructions when the direction remains uncertain.
Improve the chosen construction instead of adding unrelated decoration.

Before finishing, ask whether the interface can do more with its strongest material. Check whether every
selected asset is present and performs its planned job. Check whether useful inspected material was left
unused without a recorded reason. Check whether any major choice came from habit rather than this work.

## Verify the result

Run the project, use every important control, and inspect it at real viewport sizes. Check the console,
network requests, loading behavior, fallbacks, focus, contrast, content truth, responsive composition,
and reduced motion. For involved movement, inspect both the normal-speed experience and representative
frames. Use `design-review` for the full mechanical pass.

When handing over the work, name the base decision, the references and material that changed the build,
each selected item's job, and any useful candidate that was left out with its specific reason.
