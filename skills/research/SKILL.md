---
name: research
description: Investigate a current or uncertain question against primary sources, reconcile conflicts, and produce a cited answer. Use for fact finding, comparisons, technical behavior, or evidence needed for a decision.
---

# Research

Start from the research contract produced by `brainstorming` when one exists. Otherwise write the same
contract briefly: the decision, open questions, established facts, scope, freshness needs, source needs,
and what counts as enough evidence. Resolve ambiguity here before searching.

## Search by claim

Break the question into claims that can be checked. Search each claim through the sources suited to it.
Use more than one independent source when a consequential claim can reasonably be corroborated. A search
result, snippet, title, or repeated syndicated statement is not an independent source.

Work outward from the source that owns the fact:

1. Official documentation, specifications, source code, changelogs, filings, datasets, or direct API output.
2. Repository code, issues, and pull requests for observed behavior, defects, maintenance, and intent.
3. Papers and their released data for scientific or algorithmic claims.
4. Technical Q&A for reproducible errors and version-specific fixes.
5. Practitioner forums for failure reports and leads that can be checked elsewhere.

Use web search for discovery and open every source used in the answer. When a source needs extraction and
Scrapling is available, use `StealthyFetcher` for protected pages and `DynamicFetcher` for rendered pages.
Confirm that a successful response contains the expected material. Change the query or source family when
the current route repeats the same claim, returns stale material, or leaves an open question untouched.
Before another search, name the unresolved claim and the new source owner or query angle. If a repeated route
produces no new evidence, record that route as a null result and move to the next unresolved claim.

## Keep evidence compact

Save facts, not page dumps. Build the evidence register from observed fetch results before drafting the
answer. For each claim, retain the source URL, owner, publication or update date, access date, the short
passage or data that bears on the claim, and whether it supports, weakens, or conflicts with the claim. A
source whose relevant content was not returned is an unverified lead and cannot support the answer. Keep
downloaded pages and large artifacts outside the model context and point to their paths.

Date current claims. Check repository activity and versions when software behavior or maintenance matters.
Trace secondary claims back to their primary evidence. When sources disagree, state both positions and say
which has stronger evidence. When evidence is absent, report where you looked and leave the answer open.

## Answer

Write the answer first with a confidence of settled, likely, contested, or unknown. Follow it with the
evidence for each claim, inline links and dates, conflicts, and what could not be established. Match the
requested delivery form. If none was given, save one Markdown file under the repository's existing research
directory, or `docs/research/<topic>.md` when none exists.

Saved research must use durable Markdown links containing the source URL. Conversation citation tokens and
search-result identifiers do not survive into the file and cannot serve as its evidence.

## Done when

Every answer claim maps to the evidence register and to content you opened. The source set fits the claim rather than a fixed checklist.
Current claims carry dates. Consequential claims have independent corroboration or an explicit reason they
cannot. Conflicts and null results remain visible. No failed route repeats an unchanged query. The answer
resolves the research contract without adding questions that do not affect its decision.
