# Fun and easy to read

The owner's bar: a reader should want to keep going. Boring is a defect, the same as unclear.
Fun here means momentum and specifics, not jokes pasted on. Accuracy always wins: a vivid wrong
sentence is worse than a dull right one.

## Easy first (these make fun possible)

- **Answer first.** The reader gets the point in the first two lines, then the reasons.
- **Short sentences, mostly.** Aim for an average under 20 words. A long sentence is fine when it
  carries one reason from start to end. `prose_check.py` prints the average and the long ones.
- **One idea per paragraph,** led by its point.
- **Plain words.** "use", not "utilize". Define a term the first time, in the same sentence.
- **Same word for the same thing.** Rotating synonyms makes the reader wonder if it is new.

## Fun (pick the moves the genre allows)

| Move | Before | After |
|---|---|---|
| Open on the most interesting true thing | "This report covers our caching work." | "Our API answered the same 40 questions 2 million times last month. Caching them cut the bill by half." |
| A real example where a claim is abstract | "Retries improve resilience." | "When the payment API blinked for 3 seconds on Tuesday, retries saved 214 orders." |
| Give a number a scale people feel | "Latency is 445 ms." | "445 ms: slow enough that a user notices the click lagging." (only when the comparison is true) |
| Show the stakes | "Pin the version." | "Pin the version, or the next release can change your eval scores overnight." |
| Leave a real gap, then fill it | Paragraphs that each restart | End a paragraph on the question the reader now has, and answer it next: "So why did the cheap model win?" Never a teaser with no answer. |
| Headings that say the point | "Results" | "The small model won on cost and tied on accuracy" |
| Talk to the reader | "Users should configure the token." | "Set your token first." |
| Earned wit | A pun in every heading | One wry line where the material is ironic: "The fix was one line. Finding it took three days." |
| A tiny story | "The pipeline had a bug." | "The pipeline reported 100% accuracy. It was grading its own answers." |

Vivid means concrete, not idiomatic. Idioms and cultural references trip non-native readers
(`tech-writing.md`); a real number or a real story works for everyone.

## Where fun stops

- **Procedures, error messages, safety text, legal text:** fun means fast. Action, condition and
  consequence first. No wit.
- **Bad news and apologies:** plain and direct. Do not make the reader's problem a joke.
- **Never invent** a story, number, quote or comparison to make it livelier. Use the owner's real
  material, or leave the sentence plain.

## Check

Read the opening on its own. Point to the detail that shows why the answer matters; if there is
none, add a verified one or cut the throat-clearing. Keep later examples where they help the reader
follow the reasoning, and cut ones that only decorate (interesting but irrelevant details cost
readers a little understanding, g = -0.16 across 50 studies, per the 2026-11-21 Sol review).
