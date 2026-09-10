# Queue eleven independent coverage review

Checked 2026-09-09; follow-up source review 2026-09-10 UTC. The cloud batch
completed at exchange `d3638a45-ceb5-47f6-bf75-a743b6ff4ff7` and its actual
78,137-byte ZIP was downloaded. All 25 internal checksums and all four draft
schemas/source references passed. Do not resend it. These checks establish
artifact integrity, not factual verification; batch eleven is not published.

## Candidate counts are layer-specific

The original downloaded `company_ledger.csv` has 182 rows. Adding the six entries
in `episode-companion-queue.csv` gives 188 IDs in those two layers only. This is
NOT the complete deduplicated project queue. The site contains researched Shark
Tank companies missing from that original ledger, including Brazyn, BRCĒ, Bravo,
Brass Roots and others. It also contains 13 legacy non-Shark-Tank companies.

Reconcile the returned cloud queue, original ledger, companion supplement and
published research records by aliases and legal identity before reporting an
overall candidate count. Do not add every missing spelling as a new company, or
subtract all site records as if each were a Shark Tank company. The current 65
site records and 54 published pages are site totals, not corpus coverage totals.

An explicit alias comparison of 48 structured research records against the
182-row original ledger found 27 unmatched names. The review candidates and
normalization method are saved in `ledger-reconciliation-candidates.json`.
This is not proof that all 27 are distinct additions; verify identities and the
remote queue before merging. Unlike the earlier quick site-name check, this
comparison reads aliases from both sides, including the ledger's Hidrent alias.

The running cloud batch extracted its original ledger from the original ZIP and
printed SHA-256 `17950f59334447d0336af8d794e3676594dbd6f062dbaf29f0b5e5fb8af36b1f`.
Local `shasum -a 256` produced the identical value. The discrepancy therefore
cannot be explained by different original-ledger bytes; later research/queue
layers still need to be reconciled with that same baseline.

## Independent episode roster checks

| Episode | Companies in retrieved roster | Source strength |
| --- | --- | --- |
| S14E5 | Plufl; Bridal Babes; Big Bee, Little Bee; Pretty Rugged | ABC primary roster |
| S8E24 | Bridal Buddy; Laid Brand; Rocketbook; Wine and Design | TVmaze secondary roster; primary reconciliation pending |
| S9E9 | Glovestix; BrilliantPad; BRAVO; Hoopmaps | TVmaze secondary episode list; primary reconciliation pending |
| S7E26 | FashionTap; brellaBox; My Fruity Faces; Brightwheel | Previously reviewed secondary roster; primary reconciliation pending |

Sources:

- https://abc.com/news/bc50125d-fd09-4e25-af88-09cc951330c7/category/2887649
- https://www.tvmaze.com/episodes/1150189/shark-tank-8x24-bridal-buddy-laid-brand-rocketbook-wine-and-design-shark-profiles
- https://www.tvmaze.com/shows/329/shark-tank/episodes
- https://www.tvmaze.com/episodes/695039/shark-tank-7x26-fashiontap-brellabox-my-fruity-faces-brightwheel

ABC's S14E5 heading misspells Big Bee, Little Bee as Big Big, Little Bee; its linked
domain and description identify the existing company. This is not a new company
or evidence of a deliberate historical edit. Preserve the discrepancy without
creating a duplicate. TVmaze's S8E24 title also includes Shark Profiles, which
should not be imported as a pitched business.

The local original ledger has no name matches for Bridal Buddy, BrilliantPad,
Laid Brand, Rocketbook or Wine and Design. The cloud's shared queue may already
contain them. Compare its returned artifact before adding duplicates.

## Primary historical lead for BrilliantPad

The company's November 9, 2017 crowdfunding update identifies its broadcast as
Season 9 Episode 9 and describes Lori Greiner's offer. This is an early company
statement, not by itself proof of completed investment.

https://www.indiegogo.com/en/projects/alancook-6669236/brilliantpad-self-cleaning-indoor-dog-potty/updates/27

The current company FAQ calls the episode 914. Treat production/broadcast
numbering as a reconciliation question, not a second appearance:
https://www.brilliantpad.com/fr/pages/details2

Direct retrieval check: the Indiegogo update's page body returned no text, but
indexed text retains the November 9, 2017 update, its $500,000/5% offer language,
and Season 9 Episode 9 reference. Attribute this as a company offer announcement;
it is not independent evidence of closed financing. The FAQ's Watch episode link
now redirects to ABC's generic episode guide, not an episode-specific record.

The FAQ currently combines Smart/Professional product navigation with body text
describing a dog-triggered version as still being field-tested. Do not use that
entire page as a contemporaneous snapshot of one product generation. No dated
before/after capture was obtained; this does not establish when edits occurred.

## Next action

### Independently retrieved investment evidence

- Brightwheel's May 2, 2016 company release says it raised $600,000 from Mark
  Cuban and Chris Sacca, welcomes them to the team and includes statements from
  both investors. This is company-confirmed financing, materially stronger than
  an episode recap. The publication date is not necessarily the closing date.
  https://www.globenewswire.com/news-release/2016/05/02/1253520/0/en/Billionaire-Investors-Mark-Cuban-and-Chris-Sacca-Invest-600-000-in-Early-Education-Platform-Brightwheel.html
- Bridal Buddy: Looper's article, updated February 15, 2023, reports the deal
  never fully closed. That passage is author narrative, not a direct founder
  quotation. If the cloud cites a different founder interview, retrieve that
  interview before calling the outcome founder-confirmed.
  https://www.looper.com/930063/whatever-happened-to-bridal-buddy-after-shark-tank/
- The older Gazette Review recap describes Kevin as involved in manufacturing
  and a product bundle. This conflicts with the later failed-closing account;
  it does not independently establish ownership. Preserve the discrepancy and
  avoid repeating unsourced manufacturing claims as verified facts.
  https://gazettereview.com/2018/05/bridal-buddy-after-shark-tank/
- Bridal Buddy's current official About page names Bridal Buddy, LLC and dates
  the product launch to mid-2015. It is useful company-identity/history evidence,
  but does not confirm current Pennsylvania standing or investment closing.
  https://bridalbuddy.com/pages/about-us

Review the completed batch's queue and roster table against these observations.
Preserve the original sources and resolve the count discrepancy before reporting
a global inventory total. No new verdicts or pages were published by this review.

## Follow-up claim decisions (2026-09-10 UTC)

- **Bridal Buddy:** Inc.'s June 5, 2018 article explicitly attributes the failed
  $75,000/30% Lori Greiner/Kevin O'Leary deal to Heather Stenlake. This resolves
  the earlier attribution question: describe it as founder-reported non-closing,
  not as inspection of a termination contract. Keep the contradictory older
  Gazette Review recap identified as a reporting conflict.
  https://www.inc.com/magazine/201806/emily-canal/paparazzi-proposals-engagement-photos.html
- **BrilliantPad:** Devlin Design's dated December 20, 2018 client-news post
  identifies its design/engineering role and states that Lori invested $500,000.
  This verifies what a business collaborator reported, not an executed closing.
  The draft's contrary Shark Tank Blog source could not be independently read
  in this follow-up: web retrieval failed twice, then direct HTTP returned 403.
  Do not mark that side independently verified or infer failure to close from
  the retrieval failure. BPAD2 and BPAD4 are the same URL, not two independent
  sources. The draft's production-code interpretation of 914 also remains
  unverified; preserve the FAQ/broadcast-number discrepancy instead.
  https://www.devlin-design.com/news/2018/12/20/devlin-design-product-appears-on-shark-tank-s9e9
  https://www.sharktankblog.com/business/brilliant-pad/
- **Brightwheel:** The currently retrieved terms identify DSSV, Inc. as the
  contracting party and display May 12, 2026 as the update date. This supports
  current self-identification, not state standing or proof of that exact wording
  on the displayed historical date. Experience Early Learning's official page
  confirms it is part of brightwheel, but its retrieved body supplies no 2023
  transaction date. Verify the acquisition date separately before dating the
  timeline; do not infer it from this current integration page.
  https://mybrightwheel.com/terms/
  https://blog.experienceearlylearning.com/brightwheel-and-experience-curriculum/

Remaining before batch integration: retrieve the unresolved opposing BrilliantPad
account or label its independent verification gap; review the legal-identity
documents and remaining timeline claims for all four records; normalize records
to the repository schema, add regression checks, build and visually inspect.
The full project queue still needs reconciliation beyond the 188-row layer.

## Government-document identity checks (2026-09-10 UTC)

The following relevant PDF pages were independently retrieved and their text
inspected. Screenshot requests returned references but no inspectable images in
this tool session; visual table verification remains pending.

- **Bridal Babes trademark:** PDF page 23 (zero-based 22) of the USPTO's
  August 21, 2025 KAVIAR office-action bundle contains an attached BRIDAL BABES
  registration record: serial 88575389, registration 6051723, registered May 12,
  2020, registrant Ashley R Young individually (also known as Ashley R Smith).
  This is an attached historical registration extract, not a refusal against
  Bridal Babes and not proof of current ownership in September 2026. Do not
  attach the enclosing KAVIAR application number 99073708 to Bridal Babes.
  https://tmng-al.uspto.gov/resting2/api/casedoc/cms/case/99073708/office-action/OfficeAction7734969.pdf
- **Bridal Babes grant recipient:** PDF page 48 (zero-based 47), Schedule I of
  Philanthropic Ventures Foundation's 2024 Form 990 public copy, lists Bridal
  Babes Group Inc., Laurel, Maryland, EIN 88-4195838, with a $25,000 cash grant
  for the Nancy Twine Dream Makers Founder Grant. This is the foundation's
  reported recipient identity, not a state corporate standing certificate.
  No record reviewed here establishes a trademark transfer from the individual
  registrant to this corporation or identifies the current ecommerce contractor.
  https://www.venturesfoundation.org/wp-content/uploads/2025/11/2024-pvf-form-990-public-disclosure-copy.pdf
- **Brilliant Pet 2:** PDF page 2 (zero-based 1) of Illinois DCEO's QNBV reference
  lists Brilliant Pet 2, LLC, program number 94F, with certification eligibility
  October 7 through December 31, 2016. Those column labels are certification
  dates, not formation/dissolution dates. The program number is not a Secretary
  of State entity number. This supports historical program participation only;
  formation jurisdiction and current state standing remain unverified.
  https://dceo.illinois.gov/content/dam/soi/en/web/dceo/expandrelocate/incentives/taxassistance/documents/qnbv-s-2016-2019-reference-for-attestations.pdf

Import these distinctions into the curated records rather than copying the raw
draft's broad legal-identity confidence. Preserve the downloaded draft unchanged.

## Integration checkpoint

`research_batch_2026-09-10_queue-11.json` now contains the first curated record,
Bridal Buddy. Its schema, formats and claim/timeline references pass independent
validation. No fixture/page registration has been added, so it is not published.
The other three records remain to be curated; this is a partial batch, not a
replacement for the four-company scope. Added a regression check protecting
founder-attributed failed closing and the unresolved registry identity.

Brightwheel is now the second curated record in that file. Independently followed
the official press index to its Business Wire acquisition announcement:
https://www.businesswire.com/news/home/20230403005980/en/Brightwheel-Acquires-Experience-Early-Learning-Advances-Early-Education-Space-with-All-in-One-Offering
The retrieved release confirms acquisition, but supplies no visible timestamp or
exact closing date/consideration. The raw April 5, 2023 date was not promoted into
a verified transaction date. The current observation belongs in the retrieval
timeline, not a fabricated historical event date. Brightwheel remains classified
operating, not acquired: it is the buyer. Both staged records pass schema/format
checks and all 11 research tests pass. Bridal Babes and BrilliantPad still need
curation; no batch-eleven page has been registered or published.

Bridal Babes is now the third staged record. Re-read the founder interview: its
investment confirmation is explicit, but the cap-table sentence describes an
earlier aspiration. The curated record does not claim a verified equity percentage
or inspected cap table. Historical individual trademark ownership and the
corporate grant-recipient identity remain separate, with no inferred transfer.
All three records pass schema/format checks and the 11 research tests pass.
BrilliantPad remains unstaged. PDF visual review, remaining claim research,
fixture registration and publication verification are still pending.

All four batch-eleven records are now staged: BrilliantPad was added with null
investment closing, a single explicitly unretrieved contrary-report lead, and
separate historical QNBV/app-developer identity evidence. Its store retrieval
reported a 1.1-year-old crawl, so fresh direct storefront verification is required
before publication. The four records pass schema, format and source-reference
checks. They remain unregistered as pages; this is not a publication checkpoint.

Fresh direct storefront checks succeeded for all four companies. Bridal Buddy
now lists seven catalog results; Bridal Babes lists priced Ivy/Gardenia dresses;
Brightwheel's homepage offers demos. BrilliantPad initially failed with TLS EOF
in requests, but curl returned HTTP 200 and current product links (replacement
rolls from $59.99 rather than the search snapshot's $49.99). This resolves the
stale-crawl publication check, not fulfillment or financial-health verification.
The structured source notes now record these direct observations. No evidence
here dates a historical edit or establishes its motivation.

PDF visual verification is now complete for the three relevant pages. Downloaded
the original PDFs to `/tmp/sharktank-filings.7fbdHJ`, rendered with Poppler and
inspected DCEO page 2, the foundation's PDF page 48 and USPTO page 23. The table
headers confirm certification eligibility rather than corporate dates; the grant
row aligns Bridal Babes Group Inc., its EIN, $25,000 cash and the named grant
purpose; the trademark page confirms the individual registrant and historical
registration identifiers. Structured notes were updated and the completed visual
checks removed from uncertainties. Other legal/history gaps remain unchanged.

The four companies are now registered in the local fixture and company catalog.
The offline build succeeds with 69 total records, 58 article pages and 11
research-only pages. All 116 tests pass. These are local-build counts only;
the public site has not been deployed. Generated-page visual review and live
deployment checks are next. The earlier unregistered-page notes are superseded
by this checkpoint, not evidence of publication.

Local browser QA completed: all four new pages have the expected H1 and
self-canonical, no horizontal overflow at 390px, and no observed pageerror
events. Inspected full mobile screenshots for Bridal Babes and BrilliantPad
and desktop views (1365px) for Brightwheel and Bridal Buddy. Unresolved closing,
legal identity and research gaps remain visible. Desktop views also have no
horizontal overflow. This check did not exhaustively test outbound links or
all network requests. Local server is session 6931 on 127.0.0.1:8879.
Deployment has not occurred. The existing template labels episode-reference
links as Video even where their titles explicitly say not a video; this is a
presentation issue to address without misrepresenting those URLs as clips.

Resolved that presentation issue: the shared appearance field now reads
Appearance source, which accommodates clips, episode guides and press reports
without URL heuristics. Added a rendered-page regression test. All 117 tests
pass and the build succeeds. Inspected the updated 390px Brightwheel view;
the label wraps cleanly and there is no horizontal overflow. Deployment remains
pending; no public-release claim is made.
