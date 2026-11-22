# Query bank, intent ladder and scoring

Replace <job>, <role>, <workaround>, <incumbent>, <category>, <symptom> with words from real posts.
Run each in the buyer's language and the local variants you find.

## Templates

| Signal | Queries |
|---|---|
| Problem in their words | `"<job>" "takes hours"`, `"how do you handle" "<problem>"`, `"<symptom>" workaround`, `"<workflow>" spreadsheet`, `"is there a way to" "<job>"` |
| Trigger and consequence | `"<job>" "missed deadline"`, `"had to hire" "<job>"`, `"<incumbent>" "price increase"`, `"client requires" "<workflow>"` |
| Active search | `"looking for" "<job> tool"`, `"any recommendations" "<job>"`, `"alternative to <incumbent>"`, `"switching from <incumbent>"`, `"<incumbent>" export alternative` |
| Money and switching | `"<job>" budget`, `"paid for" "<alternative>"`, `"<category>" demo`, `"<job>" RFP`, `"cancelled <incumbent>"`, `"moved to"`, `"hire someone to" "<job>"` (Upwork, Fiverr, job boards) |
| Counter-evidence | `"we built our own" "<category>"`, `"not worth paying" "<problem>"`, `"stopped using" "<alternative>"`, `"<workaround>" "good enough"` |
| Venue discovery | `"<role>" "<workflow>" forum`, `"<pain phrase>" subreddit`, `"<job>" newsletter`, `"<job>" meetup OR conference`, `"<incumbent>" community`, `"<role>" slack OR discord` |

## Intent ladder

| Rung | Meaning | Example evidence |
|---|---|---|
| 0 | Mention, advice, or a seller talking | "You could try X" from a vendor |
| 1 | First-hand pain | "Reconciling these invoices eats my Fridays" |
| 2 | Costly workaround or repeated failure | "We pay an intern to copy this into Sheets every week" |
| 3 | Active search or switching | "Looking for an alternative to X, it broke our exports again" |
| 4 | Budget, trial, demo or procurement | "We have budget for this quarter, who should we demo?" |
| 5 | Documented purchase or migration | "We moved our team of 40 from X to Y last month" |

Rung 5 proves someone bought a solution, in the past. A current rung 3 or 4 may be the better
opportunity. Quote the evidence for every rung you assign.

## Score per venue (0 to 10)

| Component | 0 | max |
|---|---|---|
| Audience fit (0 to 3) | Wrong role or job | The exact buyer role discussing the exact job |
| Recent intent (0 to 3) | No rung 2+ posts | Several independent buyers at rung 3+ in the window (3 needs at least three distinct buyers) |
| Recency (0 to 2) | Nothing in 12 months | Rung 2+ posts in the last 90 days |
| Reach under the rules (0 to 2) | Promotion banned and no allowed format | A permitted format (weekly self-promo thread, show-and-tell, answering questions with disclosure) |

Show the components, the counts behind them and the coverage. Venues sampled to different depths
compare only by bands (strong, some, thin), never as measured conversion.
