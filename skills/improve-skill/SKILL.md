---
name: improve-skill
description: Fix a skill that just misbehaved, while the evidence is still in the conversation. Use for "that was wrong", "improve the X skill", "it should have done Y instead", or after a skill produced work that needed correcting. Edits the SKILL.md and commits the reason.
disable-model-invocation: true
---

# Improve a skill

A skill only gets better if the moment it failed becomes an edit. That moment is now, while the
transcript still holds what actually happened. An hour later you have only a vague sense that
something was off.

## Steps

1. **Name the failure in one sentence, from evidence in this conversation.** Not "it could be
   better": what did the agent do, and what should it have done? Quote the turn if you can.
   *Done when:* the sentence names a behaviour, not a feeling.

2. **Find the cause in the file.** Read the target SKILL.md at
   `~/.skills-library/skills/<name>/SKILL.md`. The cause is one of four, in order of likelihood:
   - **The pointer.** It did not fire when it should have, or fired when it should not. The
     `description` is wrong, not the body.
   - **A missing rule.** The situation genuinely was not covered.
   - **A weak completion criterion.** It stopped early because "done" was fuzzy.
   - **A no-op or a contradiction.** The rule was there, but buried under lines that changed nothing,
     or another line told it the opposite.

   *Done when:* you can point at the specific lines, or state that nothing in the file covers this.

3. **Make the smallest edit that would have prevented it.** Follow `working-with-agents`: prompt the
   positive, one meaning in one place, delete no-ops rather than adding caveats.

   **Prefer deleting.** A skill that grew a paragraph every time something went wrong becomes the
   87 KB ban-list that measurably performed worst in our own testing. If the new rule duplicates an
   existing one, sharpen the existing one instead of adding.

   *Done when:* the diff is as small as it can be while still preventing the failure.

4. **Commit with the reason.**
   ```
   cd ~/.skills-library && git add -A && git commit -m "<skill>: <what changed>

   Failed when: <the one-sentence failure>
   Cause: <pointer | missing rule | weak criterion | no-op>"
   ```
   The history is the point. `git log -p skills/design-craft/SKILL.md` then tells you why every rule
   exists, and lets you revert one that turned out to be an overcorrection.

5. **Say what you changed and what you deleted**, in two lines. If you added net length, justify it.

## When the fix does not belong in a skill

- **It applies to everything you do, always** → it belongs in `~/.claude/CLAUDE.md`, not a skill. A
  skill only fires when its description matches; CLAUDE.md is loaded every turn. This is how `unslop`
  was promoted out of the skill system.
- **It is one project's convention** → that project's own CLAUDE.md.
- **It happened once and may not recur** → do nothing yet. Wait for the second occurrence. Editing on
  a single sample is how skills accumulate sediment.

## Reviewing the whole set

Occasionally, rather than reacting to one failure:

- `wc -l ~/.skills-library/skills/*/SKILL.md` — anything growing past ~200 lines needs reference
  files split out or content cut.
- Check every `description` still matches what the skill does. Drift there is invisible and it
  silently stops the skill firing.
- Look for the same rule in two skills. Pick the owner, delete the copy.
- Ask of any skill you have not fired in months: user-invoked and free, or delete it?
