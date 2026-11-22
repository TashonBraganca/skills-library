# Why learn-fast is built this way

Each move in SKILL.md, the evidence behind it, and the failure it prevents. Read this when
deciding whether to drop a move for a topic.

## AI tutors: guard the thinking, or it hurts

| Study | Setting | Result | What we take from it |
|---|---|---|---|
| Bastani et al., "Generative AI without guardrails can harm learning", PNAS 122 (2025), e2422633122 ([record](https://econpapers.repec.org/RePEc:nas:journl:v:122:y:2025:p:e2422633122)) | ~1,000 Turkish high-school maths students; plain GPT-4 chat versus a tutor prompted to give hints, not answers | The plain-chat group did better on practice and worse on the later exam without AI (reported as about 17% worse). The hint-only tutor largely removed the harm; secondary reports put its exam effect near zero. | Answers on demand feel like progress and cut independent performance. Hints first, answer only on a second request. Do not expect the guard alone to raise scores. |
| Kestin et al., "AI tutoring outperforms in-class active learning", Scientific Reports (2025) ([Harvard SERL page](https://serl.fas.harvard.edu/publication/ai-tutoring-outperforms-class-active-learning-rct-introducing-novel-research-based)) | 194 Harvard physics students, crossover RCT, two lessons | The scripted AI tutor beat an active-learning class on post-test gains, in less median time; students reported more engagement. | The tutor that won was designed by instructors: active engagement, managed load, scaffolding, accurate feedback, self-pacing. The design, not the model, is what helps. |
| Two-year Khanmigo cluster RCT, 18 Tennessee middle schools (EdWorkingPaper ai26-1551, 2026, [PDF](https://edworkingpapers.com/sites/default/files/ai26-1551.pdf)) | Tutor set to coach, not answer | Small gain (reported as 1.3 national percentile ranks). Students mostly sent bare answers or clicked suggested prompts. | Engagement is the bottleneck, and forced practice did not fix it. Show the novice a complete small case first; offer one prediction question as an option. |

These are secondary-reported figures from the search on 2026-11-19 except where the paper page was
opened; check the paper before quoting a number to anyone.

## Classic learning science (well replicated)

| Move | Evidence | Failure it prevents |
|---|---|---|
| Worked example before practice, then fade steps | Worked-example effect (Sweller and Cooper 1985); fading (Renkl and Atkinson 2003) | Novices drown in problem-solving search; experts get bored by full examples (expertise reversal), so fade faster for experts |
| Predict before reveal | Predict-observe-explain; pretesting effect (a wrong guess first still improves later recall). A 334-student university trial found unrestricted AI access beat access gated on reading first ([IZA DP 18338](https://www.iza.org/publications/dp/18338/ai-tutoring-enhances-student-learning-without-crowding-out-reading-effort)) | Passive reading that feels fluent and leaves nothing. Keep the prediction optional, never a gate |
| Retrieval practice and spacing | Practice testing and distributed practice rated "high utility" in Dunlosky et al. 2013 (doi:10.1177/1529100612453266); testing effect (Roediger and Karpicke 2006) | Forgetting within days; the optional fresh-case question covers this |
| Self-explanation prompts | Chi et al. 1989 and 1994: students who explain steps to themselves learn more | Copying steps without knowing why they work |
| Refuting misconceptions directly | Refutation texts change misconceptions better than plain exposition (Tippett 2010 review) | The owner's prior wrong model survives a correct explanation |
| Words next to pictures, no decoration, split long processes | Mayer's multimedia principles: coherence, signalling, spatial contiguity, segmenting | Split attention and overload |
| Concrete first, then the general rule | Concreteness fading (Fyfe et al. 2014); one experiment showed a transfer gain, another no reliable difference, and Kaminski's abstract-first result is fragile in replication | Abstractions with nothing to hang on. Map the concrete case to the mechanism and test transfer with a fresh case |
| An example from the learner's own world | Relevance and prior knowledge drive encoding | Textbook examples that do not transfer to the owner's work |

## Jargon and load (added 2026-11-21 after the AtlasKV page failed)

These four rows come from the GPT Sol review of 2026-11-21 (`the-skills-god/review/learn-fast-fix/sol.md`). The links are Sol's; open one before quoting it.

| Evidence | Rule |
|---|---|
| Shulman et al. 2020, *Journal of Language and Social Psychology* ([link](https://journals.sagepub.com/doi/10.1177/0261927X20902177)): jargon cut processing fluency and engagement even when definitions were given; a later study found the effect varies by topic ([PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239524)) | Count terms even when defined: at most one new term per step, none in the first two |
| CLEAR readability models ([Crossley et al. 2023](https://link.springer.com/article/10.3758/s13428-022-01802-x)) use word familiarity and frequency that grade formulas miss | Grade level is a style signal only. explain_check.py flags rare words and the topic's term list |
| Gick and Holyoak 1983: one analogy often fails to transfer | Say where the comparison breaks, and check understanding on a new case |
| Mayer and Chandler 2001: learner-paced segments helped transfer; animation studies often give the animated version extra information | Step controls, still pictures by default, motion only to show a change |

The page limits (60 words a step, 5 labels, one term and one number) are starting defaults chosen to
fail the AtlasKV page. Test them with readers before treating them as settled.

## Plain English

Short, active, one-idea sentences cut reading load for everyone, and most for non-native readers.
The owner asked for STE-style English in explanations (2026-11-19), so the STE structural rules apply
to body text. They do not apply to code, formulas or quotes.
