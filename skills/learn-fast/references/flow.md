# The plain story, the picture, and motion

## Story outline (story.md, before any page code)

```
Answer:        <one plain sentence; no listed terms>
Why it matters: <the everyday problem, as a scene with something at stake>
Case:          <one complete case, input to outcome; real from the source when possible>
Steps:
 1 <what happens in the case>                  so: <why that makes step 2 necessary>   picture: <what is shown>
 2 <the next change, caused by step 1's gap>  so: <...>                               picture: <the one change>
 ...
Comparison:    <familiar thing>  parts: <its part = real part, ...>  predicts wrongly: <one thing>
Catch:         <the limit that changes the takeaway, beside the claim it limits>
Rule + fresh case: <the idea in one sentence>  new case: <a case where it predicts something different>
Go deeper:     <exact names, maths, full results, misconceptions, critique of the source>
```

## Checks on the outline

- Read the step lines aloud. They must sound like a story told to a friend.
- Every "so" line is answered by the next step. If two steps could swap places, the order is not
  doing work: merge them or find the cause that links them.
- Show the thing before naming it. "The clerk opens only the drawers whose labels look close. The
  paper calls this pruning" works. "Pruning means..." first does not.
- 3 to 7 steps. More means the topic needs a guided path.
- The catch is true to the source: what was measured, at what size, and what was not.

## Worked example: a paper (AtlasKV, arXiv 2510.17934v2; checked against the PDF 2026-11-21)

| Step | What happens in the case | So | Picture |
|---|---|---|---|
| 1 | Someone asks the AI about Morocco's opinion (a real test question from the paper). The answer is one fact in a pile far too big to read. | It needs a way to use the pile without reading it. | Person, question bubble, AI, huge pile |
| 2 | Each fact becomes a card. The top says what it is about ("the opinion of Morocco"); the inside holds the answer. | The AI must learn which card top fits a question. | One card: top and inside |
| 3 | Practice questions teach small new parts of the AI to match questions to card tops. The AI itself stays unchanged. | Matching against every card, for every word, still takes too much memory. | Questions pointing at the right card |
| 4 | Similar cards share a drawer, drawers share a cabinet. The AI reads the cabinet signs, opens the best few, then the best drawers. The rest wait in slow storage. | Now it has a handful of likely cards. | Cabinets, most greyed out, a desk |
| 5 | The best few cards land on the desk. The AI weighs each by how well it matches and blends their facts into its answer. | (the reveal: the answer appears) | Cards on the desk, answer bubble |

Comparison: a library card catalogue. Parts: card top = what the paper calls a key, card inside =
value, cabinet sign = root key. Predicts wrongly: a librarian picks one card; the AI blends several,
and it repeats the search for every word it writes.

Catch: a card in a skipped cabinet is missed for that lookup. The billion-card result measured
memory only. Finding the right card was tested on up to 100,000 cards (Appendix B.4.1), where it
came first less than a third of the time.

Fresh case: what happens if two cabinets have nearly the same sign? (The AI may open the wrong one
and blend in a wrong fact; widening how many cabinets it opens helps, at a cost in speed.)

## Picture rules

- One figure per question. Keep the same parts in the same places while the reader follows a change.
  Switch to a new view only when the question changes, and say so in the caption.
- Show only what this step needs: each part lists the steps it appears in (`<g data-show="2 3 4">`).
  At most 5 labels visible per step, in plain words ("drawer label", not "K3").
- One caption per step: what to notice, in one short sentence.
- Wide screens: figure and step text side by side, figure sticky. Phone: figure above the text,
  text at least 12 px, no horizontal scroll.

## Motion rules

- Each step animates the one change it makes: a card slides to the desk, a drawer greys out, a line
  draws in. 200 to 400 ms, ease-out; a travelling object may take up to 1.2 s. One motion at a time.
- Going back reverses the change.
- `prefers-reduced-motion`: the same before and after states, switched instantly.
- CSS transitions on `opacity` and `transform`. No library needed.
