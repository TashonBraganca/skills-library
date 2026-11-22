# Probes: throwaway code that answers one question

Merged from mattpocock's `prototype` (MIT). Use when the cheapest check for an open decision is to
build something small and look at it, instead of arguing about it.

1. **Name the question and the stop criterion** ("Does the retry state machine survive a double
   cancel?", "Which of three layouts reads fastest on a phone?"). Write what result favours each
   option before you build.
2. **Pick the branch.**
   - Logic or state model: one self-contained HTML or script that pushes the model through the hard
     cases, with buttons or a scripted walkthrough, printing the full state after every step.
   - UI: several genuinely different variants on one route, switchable by a URL parameter, using the
     project's routing convention and real content.
3. **Make it trivial to run**: one command, or one file to double-click. State in memory; a scratch
   database or file only when persistence is the question, named so it is obviously disposable.
4. **Skip polish**: no tests, no abstractions, only enough error handling to run.
5. **Mark it throwaway**: name it as a prototype, keep it beside the code it informs, out of main.
6. **Record the verdict**: the question, the result, the decision it settled, and where the probe
   lives (a throwaway branch or folder). Fold only the validated decision into real code.
