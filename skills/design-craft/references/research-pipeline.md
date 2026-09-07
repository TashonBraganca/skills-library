# Research and asset pipeline

Run `scripts/scrape_inspo.py routes` before planning research. Its machine-readable registry is the
source of truth for discovery catalogs, follow-up retrieval, and analysis routes. Use the routes that
fit the work, and search the wider web when a built-in source does not return the required material.

Start with words supplied by the subject, task, content, or needed material. Do not prescribe an aesthetic
before you have inspected evidence for it. Use a focused query, then broaden its terms or change source
when the result is empty. A failed catalog search should lead to hosted web search for a specific project
or asset, followed by `repo` or `fetch`.

Do not repeat the brief's format noun in every query. Search the underlying action, environment, movement,
material, and information problem. Study direct peers for product truth, then use adjacent finished work
to escape their shared layout habits.
Keep those roles separate. A direct peer may establish content or behavior, but a repeated category treatment needs support from the subject or adjacent work before it governs the page.

For an interaction-heavy brief, inspect finished moving work, time-based material, spatial or 3D material,
and interaction source code before choosing a direction. These are required comparisons, not required
output ingredients. Run a relevant route for each applicable family. If a route returns weak or empty
results, retry it with the source's vocabulary or use another source before closing that family. Do not
set the visual direction until the product truths, construction references, and candidate material can
be compared together. If a built-in route fails or returns weak work, use the wider web or make original
material. A weak result does not close its evidence lane.
If found material remains weak and an image, video, or 3D generation tool is available, generate brief-specific candidate material. Record its prompt, model, output path, and measured facts, then inspect and compare it under the same standard as found material.
When a reference supplies the strongest answer but cannot ship, keep its material job open. Find or make
a usable candidate and compare both in the same displayed role. Change the construction only when visual
proof shows that its replacement preserves or improves the reference's specific strength.

Before naming the direction, optimizing candidates, or choosing to move selected files into the build, run
`python3 scripts/research_gate.py --example` and write the generated schema to `research/research-receipt.json`.
Keep its family names and fields. Set both brief classifications from the requested implementation, then fill the
family evidence. Mark a source attempt viable only after opening a relevant candidate and record what you observed.
An empty or unrelated result guides the next query but does not count as an inspected candidate. Run
`python3 scripts/research_gate.py research/research-receipt.json --root . --phase evidence`. Continue only
after it prints `EVIDENCE GATE PASSED`. This keeps an early category idea from ending the comparison.

A download completes discovery, not inspection. Open visual files, watch video timelines, render models
and scenes, and read the source that creates the selected behavior. For a repository, read its inventory
and inspect the dependencies used by the relevant entry point.

Inspect lightweight previews from one result before issuing another batch or downloading large files.
Carry observed words and open construction jobs into the next query. When a catalogue uses different
vocabulary, inspect adjacent work by mechanism or composition instead of treating a literal miss as an
empty source. This prevents a category stereotype from choosing the direction before the evidence does.

Each downloaded file needs an asset record. Record its local path, source URL, type, byte size, measured
media facts, inspection output, and a short observed description. Record dimensions for images, duration
and codec for video, and scene contents for 3D files. Add the file's intended job after selecting it.
Record which selected items it can affect and the inspected evidence behind the decision.

Do not fill these fields from a filename, search caption, or memory. `scripts/scrape_inspo.py` records
download facts. Run `scripts/inspect_media.py` on downloaded visual material and look at its inspection
output. The observed description records what was actually seen. A 3D inventory is useful evidence, but
it does not replace rendering the model or scene.

Keep the research folder. Its manifests connect local files to their source URLs and reveal duplicates.
Account for every standalone downloaded candidate as selected, supporting, or rejected with a specific
reason. One content hash is one candidate even when several URLs return it. Treat a cloned repository as
one candidate with an inventory. Inspect and account for its entry
point, the dependencies that create the relevant behavior, and the bundled assets considered for use,
not every file it happens to contain.

Describe the colour fingerprint of the exact selected images and representative video frames. Compare it
with the evidence and recent related work. Do not accept or reject a direction from a fitted colour metric.
Rank viable combinations before choosing the direction. Prefer the combination whose members solve
distinct open jobs and change one another through composition or behavior. Research completes when one
inspected combination gives the strongest construction for the brief, not when every named source has
been visited or one acceptable file has been found. A collection of individually acceptable files does
not pass this test.

Render the viable ensemble candidates with the same content, viewport, loaded material, and product
state. Compare the winner with its strongest alternative. Record what appears first, the visible
relationships between materials, what becomes ordinary without the lead, the spatial and temporal case,
and why the winner is stronger. Different descriptions of one render do not constitute a comparison.
For React work, the selected ensemble includes inspected React Bits behavior that controls the lead
material or another core product state. Its contribution must remain visible in the rendered comparison.

## Hand research to implementation

Keep raw pages, search output, source trees, previews, and rejected files available throughout implementation.
Write a construction receipt as an index, not a replacement, with the base
decision, direct-peer product truths and adjacent-work construction rules, the observed spatial and temporal
rules, selected local paths, each item's job and relationships, compatible combinations considered, the strongest rejected alternative with its
reason, the rendered selection review, technical facts needed to load the files, and any open risk. Use the receipt to navigate the full
record. Reopen the underlying evidence whenever an implementation decision needs it.

The early evidence receipt becomes the construction receipt. Update it before implementation without renaming
its fields. Record each applicable evidence family, its source attempts, queries,
the construction job behind each query, inspection files, and selected or rejected decision. Closing a family as rejected requires two distinct
inspected sources and a construction reason. Record the inspected visual proof, selected material with
measured facts and jobs, and at least one tested relationship between compatible candidates. Active
material also records its input, response, timing, defining property, and runnable or frame proof. Trace
colour, type, and geometry to the exact inspected evidence that introduced each decision. For every
selected item, name the observed property that makes the exact item hard to replace and what breaks when
it is removed. Give every selected item a stable ID. Combination candidates must use those IDs, not
category names or source families. The pre-code proof must contain the selected files and behaviors together
in their intended roles, and its receipt must name every included ID. Keep an item as a candidate rather
than calling it selected when the combined proof has not shown its contribution. Give each tested
combination a stable ID and record its proof. The selection review names the selected combination as its
winner and another tested combination as its strongest alternative.

Run `python3 scripts/research_gate.py research/research-receipt.json --root .` from the skill directory,
or pass the installed script's full path. Implementation begins only after this command prints
`RESEARCH GATE PASSED`. A failed gate names missing evidence. Answer it by inspecting or comparing material,
not by weakening the receipt. Source count and token count do not decide completion. Evidence does.
