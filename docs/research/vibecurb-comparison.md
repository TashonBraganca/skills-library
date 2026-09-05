# VibeCurb comparison

## Answer

Current as of September 5, 2026, VibeCurb is strong at steering a model toward polished screenshots,
but its best general lesson is the staged visual specification, not its preset design recipes. Confidence
is likely because the repository documents its process but does not publish the prompts or run records
behind each example.

## Evidence

The repository describes a sequence of design reading, a pre-code quality gate, a precise build, a visual
comparison, and drift rejection. Its image-generation skill creates visual references that feed its other
skills. This gives the coding model a concrete target instead of asking it to invent and implement the
direction in one pass. [VibeCurb README](https://github.com/Yu-369/VibeCurb), read September 5, 2026.

The hero skill also limits the model to six architectures, named font choices, a small fixed palette, and
exact hero checks. The motion skill requires motion coverage across every visible element. These rules can
raise consistency, but they can also make unrelated projects converge on the same construction. The useful
parts for design-craft are the design read, visual proof, and rendered comparison. The preset architectures,
font lists, palette count, and blanket motion rule should stay out. [VibeCurb source](https://github.com/Yu-369/VibeCurb/tree/main/skills), read September 5, 2026.

## What conflicts

VibeCurb says the model should avoid generic stock imagery, but its hero verification suggests Picsum as a
placeholder source. Its motion skill says every visible element must move, while it also says every motion
needs a functional reason. Those rules conflict. Design-craft keeps the functional test and rejects blanket
coverage.

## What I could not establish

The repository does not provide reproducible prompts, model versions, generated source, or run logs for the
example images. I could not establish how much of their quality came from the skills, the input references,
the image model, or manual curation.
