---
name: research
description: Investigate a question against primary sources and write cited findings to a Markdown file. Use for researching a topic, gathering API or library facts, comparing tools, checking whether something is still true, or delegating reading legwork.
---

# Research

Dispatch a **background subagent** so you keep working while it reads. On Sonnet, per the standing
cost rule.

## Source hierarchy

Work down this list. A claim's weight is the weight of its worst source.

1. **The source that owns the fact.** Official docs, the actual source code, the spec, the changelog,
   the API response. A library's behaviour is settled by reading the library, not a blog about it.
2. **GitHub.** Issues and PRs for "is this a known bug", "why was it built this way", "is this
   maintained". Check the commit date and open-issue count before trusting a repo at all. Read the
   code when docs and behaviour disagree; the code wins.
3. **Papers.** arXiv, Semantic Scholar, Papers with Code for anything ML or algorithmic. Prefer the
   paper over the summary of the paper. Note the year: a 2021 benchmark is archaeology.
4. **Stack Overflow.** Good for "why does this error happen". Check the answer date and whether a
   newer answer contradicts the accepted one, which is common and the accepted answer is often stale.
5. **Reddit and forums.** r/LocalLLaMA, r/MachineLearning, r/webdev, HN and similar are the fastest
   signal on what practitioners actually hit in production, and the only place some failure modes are
   written down. Weight by whether the commenter shows their work. Treat consensus as a lead to
   verify, never as the fact itself.

**Fetching:** Scrapling first, per the standing rule. `StealthyFetcher` for anything bot-protected,
`DynamicFetcher` for JS-rendered pages. A 200 with an empty or challenge body is a silent failure,
not a source: confirm real content before quoting it.

## Rules that decide whether the output is worth anything

- **Follow every claim to the source that owns it.** A secondary write-up is a pointer, not evidence.
  If you cannot reach the primary source, say so next to the claim.
- **Date everything.** Note when the source was published and when you read it. "Current as of" is
  part of the finding, because most of these facts have a shelf life.
- **Report the disagreement.** When sources conflict, that conflict *is* the finding. Give both
  positions and say which is better supported and why. Do not average them into a bland middle.
- **A null result is a result.** "I could not find evidence for this, here is where I looked" is
  worth writing. Manufacturing a confident answer from thin sources is the failure mode.
- **Quote the load-bearing line.** For anything a decision rests on, quote the source's own words
  rather than paraphrasing, so the reader can judge it themselves.

## Output

One Markdown file. Every claim carries an inline source link. Structure:

- **Answer** first, in a few sentences, with a confidence: settled / likely / contested / unknown.
- **Evidence**, claim by claim, each with its link and date.
- **What conflicts**, if anything did.
- **What I could not establish**, explicitly. This section is not optional and an empty one is
  usually a sign you did not look hard enough.

Save it where the repo already keeps notes; match the existing convention. If there is none, use
`docs/research/<topic>.md` and say where you put it.

## Done when

Every claim in the answer traces to a link you actually opened, the date is on it, and the
"could not establish" section is honest rather than empty.
