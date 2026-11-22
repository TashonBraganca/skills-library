# studio: test prompts

Generation and grading on GPT-6.1-Terra high, blind, fresh folders, same brief, assets, tools and
time budget in both arms. Ask the owner before running. Track time and cost separately.

## Paired tests (from the Sol research review, 2026-11-21)

1. Marketing page and chosen direction: "Build a landing page for Clearbook, a tool that matches bank
   lines to invoices. Use the supplied sample rows. Bookkeepers should be able to try a match and
   undo it. Show me three rough directions, including one bold option, and pick one yourself. Give
   the page a signature motion moment. No stock photos." Pass: three first-screen sketches with the
   same headline and different compositions; the pick names an opened reference and the choice it
   informed; a visitor can match two rows and undo it; the chosen hero holds at 1440 and 390 with no
   clipped text; the signature motion is captured and reduced motion keeps the task.
2. Scoped interaction: "In this existing audit queue, fix the details drawer. Enter should open it
   from the selected row. Escape should close it and return focus. Keep the table and tokens. Check
   a 390 px screen with a long title and test reduced motion." Pass: Enter opens, Escape restores
   focus to the row; Escape works mid-transition and it reopens at once; at 390 px the long title
   wraps and close stays reachable; reduced motion keeps content without the slide; no table or
   token changes.
3. Standalone video: "Deliver a silent 12-second vertical MP4 for our release notes. Use the supplied
   product screenshots. Open on 'Batch export', show selecting three reports and exporting them,
   then hold '3 reports exported' for the last two seconds. 1080 x 1920." Pass: 1080x1920 and within
   one frame of 12 s; no audio; beats in order; the final text legible for the last two seconds;
   handoff includes measured properties and start, middle and end frames.

## Should stay quiet

- "Change the API timeout to 30s." (backend)
- "Fix the typo in the hero headline." (copy-only)

## Failure to watch for

- A gallery page or a challenge page kept as a reference; screenshots never opened.
- The shipped page drifting from the approved sketch without a recorded reason.
- Two builders editing one surface; a reviewer agent spawned without asking.
