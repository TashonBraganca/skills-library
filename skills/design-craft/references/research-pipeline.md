# Research and asset pipeline

## Find evidence

Set `DESIGN_CRAFT_INSPO_DIR` to the project's research folder. Run
`scripts/scrape_inspo.py routes` and use the routes that fit the open construction jobs. The registry is
a starting point, not a source quota. Use wider web search, `repo`, or `fetch` when a built-in catalogue
is weak.

Start with the subject, action, environment, movement, material, and information problem. Study direct
peers for product truth and adjacent finished work for construction ideas. Keep those roles separate.
Do not set the visual direction until product truths, finished references, and candidate material can be
compared together.

For interaction-heavy work, inspect finished moving work, time-based material, spatial or 3D material,
and interaction source code. These are required comparisons, not required output ingredients. Run a
relevant route for each family. If a route misses, retry it with the source's vocabulary or use another
source. An empty result does not close the family. If found work remains weak and a suitable generation
tool exists, generate brief-specific candidate material and judge it by the same standard.

When a reference cannot ship, keep its material job open. Find or make a usable candidate and compare it
with the reference in the same displayed role. Preserve or improve the reference's specific strength.

## Inspect what you find

A download is not inspection. Open images at useful size. Watch video across its duration. Render 3D
models and scenes. Run interactive work. Read the source and dependencies that create the relevant
behavior. A title, thumbnail, filename, first frame, or repository inventory cannot substitute for this.

Inspect a lightweight result before requesting another batch. Use observed terms and open jobs in the
next search. Keep the original evidence on disk. Use scraper manifests and media inspection output as the
record of URLs, hashes, file sizes, dimensions, codecs, durations, and scene contents. Add a short
description based on what was actually seen. Treat duplicate hashes as one candidate.

Account for each downloaded candidate as selected, supporting, or rejected. A repository counts as one
candidate. Inspect its relevant entry point, dependencies, and bundled assets rather than documenting
every file.

## Choose a construction

Rank viable combinations before choosing the direction. Prefer material that solves distinct jobs and
changes other selected material through shared state, geometry, timing, depth, or response. Stop when no
candidate improves an open job or relationship.

Render viable combinations with the same content, viewport, loaded material, and product state. Compare
the winner with its strongest alternative. Record what appears first, which materials affect each other,
what becomes ordinary without the lead, the spatial and temporal case, and why the winner is stronger.
After rendering a candidate, record its proof path and inspection evidence before any further proof work.
Update the receipt with the candidate, selected IDs, and comparison outcome. Do not investigate browser
tooling or proof mechanics beyond what decides the composition.

For React work, inspect React Bits as a first-class candidate. Select it when it performs a core
interaction better than the alternatives. If another source wins, record the compared behavior and the
visible reason it won. The chosen interaction must remain visible in the combined proof.

## Pass evidence into implementation

Run `python3 scripts/research_gate.py --example` to learn the schema. Before naming the direction or
choosing to move selected files into the build, write the generated schema to
`research/research-receipt.json`. Keep its family names and fields. Set both brief classifications from
the requested implementation. Write the complete receipt once after inspection instead of recreating it
after each search. Then run:

`python3 scripts/research_gate.py research/research-receipt.json --root . --phase evidence`

Continue only after it prints `EVIDENCE GATE PASSED`. If it fails, patch only the fields named by the
gate. Do not rewrite valid evidence or weaken the check.

The receipt is an index, not a replacement for the research folder. It records direct-peer product truths
and adjacent-work construction rules, family attempts, queries, source kinds, inspection paths, decisions,
selected local paths, measured facts, jobs, relationships, and risks. Reopen only the files needed for
the current decision. Do not replay old command output or images merely to restore context.

Closing a family as rejected requires two distinct inspected sources and a construction reason. Give
every selected item a stable ID. Combination candidates use those IDs, not category names or source
families. Record what makes each exact item hard to replace, what breaks without it, its implementation
medium, and the boundary an adaptation must preserve. Active material records its input, response,
timing, defining property, and runnable or frame proof. Trace colour, type, and geometry to inspected
evidence.

Update the receipt with the tested combinations and selection review. The pre-code proof must contain the
selected files and behaviors together in their intended roles. Separate demos do not prove a combined
interaction. React work requires a runnable combined proof.

Run `python3 scripts/research_gate.py research/research-receipt.json --root .`. Implementation begins only
after this command prints `RESEARCH GATE PASSED`. Keep the gate and schema fixed during a run. A failed
gate names missing evidence. Inspect or compare that evidence, then patch the named fields. Source count,
token count, and the first acceptable result do not decide completion.
