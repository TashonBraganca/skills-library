# Evidence register

Keep it while you work. It is the only thing the final answer may cite from.
A source belongs in the register only after you opened it and found the claim in it.

## Columns

| id | ask | claim | provenance group | URL and version | locator | source date | excerpt or value | evidence basis | fit and limits | stance |
|---|---|---|---|---|---|---|---|---|---|---|

`report_check.py` reads the columns by name: `id`, `ask` (one ask id such as Q1), `URL`, `locator`,
`excerpt or value` and `stance` must be there.

- **claim**: one checkable statement, in your words.
- **url**: full durable link. For Reddit use `https://www.reddit.com/r/<sub>/comments/<id>`. For arXiv use the `/abs/` link and the version.
- **source date**: when the source was published or last updated. Not today's date.
- **locator**: section, table cell, page, code lines, or timestamp. Record whether the whole relevant artifact, selected sections, or only the abstract was read.
- **excerpt or value**: a short supporting passage, the exact table cell, code lines, or a labeled figure estimate with units.
- **stance**: `supports`, `contradicts`, or `context` for the claim.
- **evidence basis**: author measurement, vendor estimate, independent reproduction, changed-setting evaluation, versioned docs or code, or firsthand report.
- **number rows**: for every empirical number, also record `experiment, arm, split, metric, unit,
  value` and any transform (ratio to %, rounding). These feed `claims.py check`.
- **fit and limits**: same setting, partial match, or different setting, and why. Add caveats such as vendor-run, single seed, auto-captions, archive lag. Keep unopened leads in the search log, not here.

## Rules

- Every row needs a versioned locator and a short supporting passage, exact table cell, code lines, or labeled figure estimate with units.
- Group rows by underlying measurement, run, dataset or incident (the provenance group). Several reports show recurrence only across distinct cases; state shared components and how you found them.
- Count a repeated claim once against its underlying evidence. Keep a separate row for new measurements or observations with their own provenance.
- Add `contradicts` rows as eagerly as `supports` rows. If the register has no contradicting row for a serious option, say that you searched and found none, and list the queries.
- At the end, every factual claim in the answer maps to register rows. A factual claim without a row is removed or stated as an open question. An inference names the rows it rests on and its assumption.

## Null results

Keep a second list: route, query, requested and effective window, caps, status (complete sample, partial, blocked, or zero matching in sample), fallback, and the claim affected. A sample can be complete for the call and still have narrow coverage. A blocked fetch is a failure, not a null result.
