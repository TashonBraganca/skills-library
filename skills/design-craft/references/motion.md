# Motion and interaction

Adapted from Emil Kowalski's `apple-design`, `animate`, and `emil-design-eng` skills under the MIT
license recorded in `LICENSE-THIRD-PARTY.md`.

Read this when the interface moves in response to touch, pointer, keyboard, scroll, time, media, or live
state. The aim is not a house animation style. The aim is motion whose cause, path, and result belong to
the work.

## Start with the cause

Respond on the causal input. A press responds on pointer down. A dragged object follows the pointer. A
control that changes a scene updates the scene while the person acts. Keep accepting input while motion
is running.

Motion should reveal state, preserve location, explain an action, connect selected material, or create an
expressive beat supported by the direction. If removing it changes none of those things, it is decoration.

For each important sequence, define the opening state, development, response, continuity, and payoff.
Choose the cause from the actual work. It may be direct input, scroll, time, media, product state, or live
data. Do not add a cause only because a reference used it.

## Preserve agency and continuity

Start a new motion from the current visible state, not the previous target. Carry velocity when the input
supplies it. Let the person interrupt or reverse the motion. Intermediate frames should show where the
object came from and what changed.

During direct manipulation, preserve the grab offset and track input continuously. Use pointer capture so
a drag survives leaving the element. Resolve competing gestures from the same movement, then cancel the
ones that do not match the person's intent. At a boundary, resistance and return usually communicate the
limit better than a hard stop.

For momentum, project the release velocity toward a valid destination. Use separate motion for independent
axes. Tune the result in the running interface rather than copying a timing value from another product.

## Choose mechanics from the behavior

Use a spring when interruption, momentum, or settling matters. Use an easing curve when the movement has a
clear authored beginning and end. Use linear time only when constant rate carries meaning. CSS transitions
work well for simple interruptible state changes. The Web Animations API or a motion library helps when the
sequence needs programmatic control. Canvas, shaders, video, and 3D are valid when their behavior earns the
rendering cost.

Use transforms and opacity for frequent movement when they preserve the intended effect. Measure any
paint, layout, canvas, shader, or 3D work on the target device. A technical shortcut that changes the visual
idea is not an optimization.

Build from observed behavior instead of effect names. The same technique can feel precise, playful,
forceful, or quiet depending on distance, timing, scale, sound, and what triggers it. Tune those properties
as one system with the selected material.

## Connect the whole sequence

Let persistent objects, camera position, masks, light, type, sound, or live values carry continuity across
states. A selected component should affect the main material or product state when that relationship makes
the construction clearer. Several unrelated effects running at once do not create a sequence.

Autonomous motion needs a readable cycle and a reason to continue. Scroll-linked motion must still leave the
person in control of reading. Video should have a useful opening frame, a stable loading state, and a role
after playback begins. Direct manipulation should remain understandable without hover.

## Make reduced motion equivalent

Honor `prefers-reduced-motion`. Remove large travel, momentum, parallax, and repeated ambient movement when
requested. Preserve state change and reading order through cuts, short fades, or another calm treatment.
Raise opacity when reduced transparency is requested. Increase separation when higher contrast is requested.
The alternate experience must preserve the task and information, not merely stop the animation.

## Verify motion in the product

Use the interactive build with pointer, touch, keyboard, and scroll where they apply. Interrupt gestures
mid-flight. Reverse them. Resize during a sequence. Test slow loading and failed media. Watch important
movement at normal speed and frame by frame. Check the browser console, frame timing, focus order, reduced
motion, and the final state after every path.

Judge the sequence against its visual proof. The important crop, depth, reading order, and text-to-material
relationship must survive between key frames. If the motion only moves generic containers, revisit the
construction rather than adding more effects.
