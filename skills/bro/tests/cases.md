# bro: test prompts (from the Sol research review, 2026-11-21)

Generation and grading on GPT-6.1-Terra high. Same transcript and settings in both arms; only one arm
gets bro. Grade the first output before any hook rewrite. A missing first-sentence answer or an
invented claim fails the case.

1. Lost mid-task. Prior reply: duplicate renewal charges traced to retries after a timeout; a patch
   giving retries the same payment ID passed all 12 local tests; nothing went live; waiting for
   finance to provide a staging account to replay a timed-out charge. User: "wtf ar eu. doing i ahev
   no idea what r u fixing". Pass: sentence one says the work is to stop retries charging a renewal
   twice; 12 passing local tests; not live; finance must provide a staging account first; at most
   five lines and 70 words, no heading or apology first.
2. Overstated pilot. User: "ok but tldr? does this show checkout got faster for everyone? Median
   checkout time fell from 4.0 to 3.2 seconds for 120 desktop users in staging. Mobile wasn't tested.
   The team used a warm cache. There's no rollout decision scheduled." Pass: sentence one limits the
   result to desktop staging or says it cannot show a speedup for everyone; both medians and 120
   users; warm cache and untested mobile kept; no production claim or invented action; at most five
   lines and 70 words.
3. Long recommendation (350 to 450 words) on turning on automatic invoice retries today: 30 of 30
   staging retries passed, no real charge tested, flag stays off until Maya from payments signs off
   on a live trial with one internal account, 10-minute wait, manual retry stays, a duplicate in the
   trial keeps the flag off. Pass: sentence one says leave it off today; opener has 30 of 30 and no
   real charge; opener names Maya and the one-account trial; opener at most five lines and 70 words,
   no heading; body has the 10-minute delay, manual fallback and stop condition, and never claims the
   trial ran.

## Should stay quiet

- "Summarize this 40-page PDF into a report" (writing or research, not a restatement)
- "/bro" typed by the owner goes through the command wrapper, not the router
