# Queue ten independent source review

Reviewed 2026-09-09 (America/New_York). This is an editorial checkpoint, not a
publication or completeness claim. Original downloaded drafts remain unchanged.

## Required corrections before integration

### Later verification and local integration

The records are now registered in the local site fixtures. Build succeeds with
65 tracked companies, 54 publishable articles and 11 research-only pages. All 115
tests pass without skips; all four queue-ten records pass schema/format checks.
Brazyn and BRCĒ render operating pages; brellaBox and Brewers Cow render noindex
research-only pages. No deployment has occurred yet.

The Forbes failed-closing passage was recovered through indexed article text.
It is now an attributed credible report, not a direct founder quotation. Direct
page opening still redirects unsuccessfully. Brazyn's recap ask/offer and the
other pitches now have claim-level sources; BRCĒ's initial equity-ask conflict
is explicitly retained with both secondary sources.

The [USPTO Official Gazette](https://patentsgazette.uspto.gov/week36/OG/html/1538-2/US12408733-20250909.html)
directly confirms BRCE ATHLETIC CORP. as patent filer/assignee and identifies both
inventors. It does not establish current Michigan corporate standing. An unrelated
California PDF returned by search was inspected and excluded, not matched by guess.
These updates supersede the earlier staging-only and failed-retrieval notes below.

- BRCĒ: final investment closing is unresolved, not strongly corroborated.
  [MSU](https://msutoday.msu.edu/news/2026/03/student-entrepreneurs-land-deal-shark-tank)
  describes investment during the appearance;
  [MEDC](https://www.michiganbusiness.org/reports-data/success-stories/brce/)
  likewise locates the $300,000/20% outcome in the episode. Later publication dates
  do not independently establish post-filming closing. Use `deal_closed: null`.
- Brazyn: attribute the reported failed closing to the Forbes profile's reporting,
  not a direct founder quotation unless the underlying interview supports that
  attribution. Forbes retrieval failed during this review; retain the earlier
  review's observation as a lead, not a newly verified retrieval.
- brellaBox: [Shark Tank Tales](https://sharktanktales.com/business/brellabox/update/)
  reports April 2018 cessation but supplies no linked primary closure evidence.
  Shark Tank Blog returned 403. Repetition does not establish independent sourcing.
  Keep closure attributed and current verdict unresolved pending corroboration.
  State dissolution and commercial cessation are separate questions; a dissolution
  filing is not the only acceptable evidence of commercial cessation.
- Brewers Cow: [Gazette Review](https://gazettereview.com/2016/03/brewers-cow-ice-cream-update/)
  reports an investor search, website return, and a company response about
  restructuring. Its displayed publication date is December 5, 2016, but its
  follow-up heading says 2018. Do not date that company response to 2016 without
  an archived version or underlying message. Neither the edit date nor intent is
  established by this mismatch. Keep reported closure and legal standing distinct;
  the draft's broad 2016–2024 timeline interval is not a verified cessation date.

## Episode-completeness gap found

The original 182-row clip-derived ledger lacks six episode companions:

- S17E12: Cranel, The Chair Blanket, Paco & Pepper. BRCĒ is already represented.
  [ABC's complete roster](https://abc.com/news/a437da6c-65cb-41f1-bd6d-1b5b77a4956b/category/2887649)
  establishes all four names and the March 4, 2026 episode.
- S9E6: Novel Effect, Drain Wig, Father Figure. Brazyn is already represented.
  [TVmaze's roster](https://www.tvmaze.com/episodes/1338941/shark-tank-9x06-brazyn-life-novel-effect-drain-wig-father-figure)
  establishes these secondary-source candidates; primary/video reconciliation
  remains required.
- S7E26: FashionTap, brellaBox, My Fruity Faces, Brightwheel are already in the
  ledger, consistent with [TVmaze](https://www.tvmaze.com/episodes/695039/shark-tank-7x26-fashiontap-brellabox-my-fruity-faces-brightwheel).
  This checks names for one episode, not completion of their status research.

New candidates belong in the research queue even without a dedicated video clip.
Do not assign invented video URLs, verdicts, or registry results. Reconcile every
included episode similarly; these three checks are not a corpus-wide audit.

## Remaining work

Structured staging records are now in
`src/dct/data/research_batch_2026-09-09_queue-10.json`. Their four records pass schema,
format and claim-reference checks; the full 115-test suite passes with none skipped.
The new regression check protects unresolved deal closing, closure corroboration,
and the Brewers Cow date conflict. These checks do not verify historical claims.

The records are not yet registered in `sample_companies.json` / `sample_fixture.json`,
so they are not new public pages. Remaining editorial checks include cited support
for pitch ask/offer details, Brazyn's reported failed closing, entity-specific
registry records, and retained draft uncertainty text. Broader draft research stays
in the original ZIP rather than being discarded or silently promoted to fact.

Complete those checks, register the records, verify rendered pages, then publish.
Transfer the six added candidates and these corrections to the
existing project Chat before commissioning subsequent work. Preserve the original
archive and distinguish its 182-row count from the expanded working queue.
