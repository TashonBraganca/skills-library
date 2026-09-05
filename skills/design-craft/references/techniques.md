# Concrete techniques

Absorbed from **Emil Kowalski's `emil-design-eng` and `animate` skills** (MIT, see
`LICENSE-THIRD-PARTY.md`). These are the specific recipes; `motion.md` holds the principles.

## Decide what motion contributes

Judge motion by its frequency, cause, and role. Repeated operational actions should respond without
making the person wait. Rare or exploratory moments can carry more expression. Keyboard input should
feel immediate, though the resulting state may still move when that movement explains location or
change. Motion may preserve space, expose state, explain an action, give feedback, connect material,
or provide an expressive moment that belongs to the work. Tune it in the running interface.

## Easing: the built-in curves are too weak

```css
--ease-out:    cubic-bezier(0.23, 1, 0.32, 1);      /* UI interactions, enter/exit */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);     /* on-screen movement, morphing */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);      /* iOS-like drawer */
```

Choosing:

- entering or exiting → **ease-out** (starts fast, feels responsive)
- moving or morphing on screen → **ease-in-out**
- hover / colour change → **ease**
- constant motion (marquee, progress) → **linear**

**Never use `ease-in` for UI.** It delays the initial movement, the exact moment the user is
watching hardest, so a 300ms `ease-in` dropdown *feels* slower than 300ms `ease-out`.

## Component principles

**Buttons must feel pressed.** Instant feedback is the cheapest quality win there is.

```css
.button { transition: transform 160ms ease-out; }
.button:active { transform: scale(0.97); }   /* keep it 0.95-0.98 */
```

**Never animate from `scale(0)`.** Nothing in the real world vanishes to nothing. Start at `0.95`
with opacity, even a barely-visible initial scale reads as natural.

```css
.entering { transform: scale(0.95); opacity: 0; }   /* not scale(0) */
```

**Popovers scale from their trigger, not their centre.** `transform-origin: center` is wrong for
almost every popover. Use the library's origin variable. **Exception: modals** keep centre origin,
because they aren't anchored to a trigger.

```css
.popover { transform-origin: var(--transform-origin); }
```

**Tooltips: delay the first, skip the rest.** A delay prevents accidental activation, but once one
tooltip is open, adjacent ones should appear instantly.

```css
.tooltip { transition: transform 125ms ease-out, opacity 125ms ease-out; }
.tooltip[data-instant] { transition-duration: 0ms; }
```

**Prefer CSS transitions over `@keyframes` for interruptible UI.** Keyframes always run to
completion; transitions can be redirected mid-flight.

**Use blur to mask an imperfect transition.** A few px of blur during a fast morph hides
interpolation artefacts the eye would otherwise catch.

**Animate enter states with `@starting-style`** rather than a JS double-rAF hack.

## Transform and clip-path

- **`translateY(-100%)`** is relative to the element's own height, the correct tool for
  "slide exactly its own height", no magic numbers.
- **`scale()` scales children too**: including border-radius and text. If you don't want that,
  animate width/height or use `clip-path`.
- **`clip-path: inset()`** reveals without moving anything, the right tool for tab indicators with
  perfect colour transitions, hold-to-delete fills, scroll image reveals, and comparison sliders.
- **3D transforms** (`perspective`, `rotateX/Y`) give real depth; a shadow alone does not.

## Gesture and drag

- Momentum-based dismissal: decide on **velocity**: not distance travelled.
- **Damping at boundaries** and friction rather than a hard stop.
- **`setPointerCapture`** so a drag survives the pointer leaving the element.
- Guard against **multi-touch** interfering with a single-pointer drag.

## Performance rules

- Prefer compositor-friendly properties for ordinary interface movement. Measure before using a
  painted property, canvas, shader, or layout animation in a repeated path.
- CSS variables are inheritable, animate one variable on a parent instead of many properties on
  children.
- **CSS animations beat JS under load**: they run on the compositor and survive a busy main thread.
- Use **WAAPI** (`element.animate()`) when you need programmatic control but compositor performance.
- Framer Motion caveat: it does not always hardware-accelerate, check the generated transform.

## Prototype before committing

When the direction remains uncertain, build genuinely different versions and compare them in motion.
Do not spend time on token variations of the same construction. The version that reads best on screen
is frequently not the one that read best as a description.

An interactive prototype is worth "a million static designs", and it sets a concrete quality bar
that stops the final implementation drifting to mediocre.
