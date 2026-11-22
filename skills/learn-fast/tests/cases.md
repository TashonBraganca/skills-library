# learn-fast: test prompts

For a paired run (with and without the skill, same model and grader) once the owner approves live
testing. Written 2026-11-19 during the round 8 review.

## Should fire, with the expected behaviour

- "Explain how attention works in transformers." -> story.md and terms.txt first; an opener with a one-sentence answer and an everyday scene; 3 to 7 steps on one running case; no terms or numbers in the opener and steps 1 to 2; real terms and maths under Go deeper; explain_check.py PASS; one optional question.
- "Teach me this paper: <arXiv link>." -> same; the catch (what was actually measured) on the default path; the critique and tables under Go deeper.
- "I don't get KL divergence, teach me." -> same, with the owner's GRPO work as the running example if it fits.
- "Walk me through sparse autoencoders like I'm new." -> ladder starts from something they know (a plain autoencoder).

## Should stay quiet

- "What does the --since flag do in papers.py?" (quick fact: chat answer, no page)
- "Write the docs for this API." (writing, not learn-fast)

## Failure to watch for

- An accurate expert digest in step form: several terms or numbers per step, symbols on screen, a diagram with dozens of labels (the AtlasKV page, 2026-11-20).

- Steps that do not follow from each other (swap test fails).
- A diagram redrawn per step instead of one growing scene.
- Decorative animation, or animation under reduced motion.
- Locking content behind a quiz.

## Paired tests from the Sol research review (2026-11-21)

Run each with and without learn-fast, writing active in both arms, same tools and model. Generation
and grading both on GPT-6.1-Terra high (owner's rule). Ask the owner before running. Blind the pair.

1. Paper: "Teach me AtlasKV v2 (https://arxiv.org/html/2510.17934v2). I know what a language model
   does. I don't know attention. Make a short visual page I can follow on my phone. What did they
   actually prove at a billion facts?"
   Pass: opening says what AtlasKV does in one plain sentence; one request runs through group
   selection, surviving facts and their use; the default path shows how skipping the right group
   hides its fact; it says the billion-triple result is GPU memory, not grounding or answer quality;
   Go deeper cites Figure 4 and Appendix B.4.1 (the 100,000-candidate grounding test).
2. Moving mechanism: "Make me a small interactive explainer for how a mechanical watch ticks. I get
   that winding stores energy. Show me what keeps it from all coming out at once."
   Pass: separates the spring's power from the balance wheel's pace; the figure shows a wheel held,
   released briefly, held again; the balance wheel triggers the release and gets a small push back;
   Back/Next show the same states both ways and reduced motion keeps them; an optional prediction
   asks what happens if the balance stops, with the reason.
3. Numbers in chat: "Explain this in chat. A factory sensor catches 90% of faulty parts and flags
   10% of good parts too. Only 1% of parts are faulty. If mine gets flagged, is it probably faulty?"
   Pass: first sentence gives about 8% (one in twelve); one 1,000-part case with 10 faulty and 990
   good; derives 9 true and 99 false alarms over 108 alarms; says in plain words why the big pool of
   good parts makes most alarms; stays in chat and answers before any practice.
