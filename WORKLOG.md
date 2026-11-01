# Defunct Company Tracker — Launch & Expansion Worklog

## Goal
Expand and launch **https://defunctcompanies.com** (Defunct Company Tracker) on the `launch-defunctcompanies` branch, merge into `main`, push to `origin` (`github.com/smolkapps/defunct-company-tracker-articles`), deploy to the live Hetzner server (`167.233.238.194`), wire in Umami analytics, apply the 301 redirect from `defunct-company-tracker-articles.apps.smolkin.org` to `https://defunctcompanies.com` (preserving path), and sync the final repository state and test verification back to Michael's MacBook (`~/Documents/projects/2026/defunct-company-tracker-articles`).

Priority order:
1. **Grow the content:** Research queued Shark Tank companies not yet published using the repo's research and review pipeline (`src/dct/data/research_batch_*.json`, `src/dct/data/research-record.schema.json`, `docs/ARTICLE-TEMPLATE.md`, `dct publish`). Every claim must be sourced and pass `verify_report`. Never invent facts.
2. **Add optional Umami analytics support:** Driven by CLI/config/env (`https://umami.smolkin.org/script.js` + website ID), outputting nothing when unset, and wired in on the live site.
3. **Old subdomain 301 redirect:** Ensure `deploy/nginx/old-subdomain-redirect.conf` cleanly 301s `defunct-company-tracker-articles.apps.smolkin.org` to `https://defunctcompanies.com` with the same path, and apply it on `167.233.238.194`.
4. **SEO improvements:** Cheap, safe improvements to titles, meta descriptions, JSON-LD, internal links, and the sitemap.

---

## Chronological Log

### 2026-10-16 01:51–02:00 EDT — Initial Audit & Environment Setup
- **Action:** Checked `git status -sb`, `git log`, `LAUNCH-ASSESSMENT.md`, `deploy/README.md`, `PROJECTS.md`, and portfolio `STATUS.md`.
- **Result:**
  - Branch `launch-defunctcompanies` is checked out at commit `e3c0f94` (`Prepare defunctcompanies.com launch`), one commit ahead of `main` (`1dcccd3`, 19th Shark Tank batch).
  - Working tree had no uncommitted tracked changes, only untracked `.work-artifacts/` (added `.work-artifacts/` to `.gitignore`).
  - Recreated `.venv` for ARM64 (`Michaels-Mac-Studio.local`, Python 3.13) and installed `.[test]`; all **135 existing tests pass**.
- **Action:** Audited live server `root@167.233.238.194` via `ssh -i ~/.ssh/bookmap-hetzner`.
- **Result:**
  - `/var/www/defunctcompanies.com` is live behind Cloudflare and Certbot TLS (`/etc/nginx/sites-available/defunctcompanies.com`).
  - `umami-db-1` on `167.233.238.194` holds 9 websites (`apps.smolkin.org` shared fleet ID `0ee0e19b-b29b-4c98-b3f6-a92a43b4ba5a`, plus standalone domain properties such as `hireaclawd.com` `064997eb-dfc6-49f9-b4cd-19ffe59307b6` and `mungerarchive.com` `79218702-a441-4a4c-9b13-d41e172a81a4`, all owned by `user_id = 41e2b680-648e-4b09-bcd7-3e2b10c06264`).
  - `apps.smolkin.org` uses a regex wildcard `server_name ~^(?<app>[a-z0-9-]+)\.apps\.smolkin\.org$;` with cert `/etc/letsencrypt/live/apps-smolkin/{fullchain,privkey}.pem`. Exact-match server blocks in `sites-available/` symlinked to `sites-enabled/` take precedence over the wildcard regex without modifying other sites.

### 2026-10-16 02:01–02:14 EDT — Umami Analytics, SEO Improvements, and 301 Redirect Config
- **Action:** Provisioned dedicated Umami website property in `umami-db-1` on `167.233.238.194` for `defunctcompanies.com`:
  - `website_id`: `d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014`
  - `name`: `Defunct Company Tracker`
  - `domain`: `defunctcompanies.com`
  - (Also noted shared `apps.smolkin.org` fleet property ID `0ee0e19b-b29b-4c98-b3f6-a92a43b4ba5a`.)
- **Action:** Implemented optional Umami analytics support in `src/dct/site.py`, `src/dct/cli.py`, `src/dct/templates/base.html`, `src/dct/templates/404.html`, and `package.json`:
  - Driven by `--umami-website-id` / `--umami-script-url` CLI flags, `SiteGenerator(umami_website_id=..., umami_script_url=...)`, or `DCT_UMAMI_WEBSITE_ID` / `UMAMI_WEBSITE_ID` and `DCT_UMAMI_SCRIPT_URL` / `UMAMI_SCRIPT_URL` environment variables.
  - Default script URL: `https://umami.smolkin.org/script.js`.
  - Outputs nothing when website ID is unset.
- **Action:** Implemented safe SEO improvements across `src/dct/site.py` and templates (`index.html`, `methodology.html`, `hub.html`, `article.html`, `base.html`):
  - Enriched `<title>` and `<meta name="description">` across home, methodology, hub, and company article pages.
  - Added `WebSite` JSON-LD on `index.html`, `WebPage` JSON-LD on `methodology.html`, `BreadcrumbList` JSON-LD on `article.html`, and `mainEntityOfPage` + `parentOrganization` (for acquired companies) on `Organization` JSON-LD.
  - Added internal links: breadcrumb links from articles to their collection and status hubs, "Other companies from this Shark Tank episode" links, "More verified companies" links, and richer footer links.
  - Added `<lastmod>` to `methodology.html` in `sitemap.xml`.
- **Action:** Updated `deploy/nginx/old-subdomain-redirect.conf` to 301 `defunct-company-tracker-articles.apps.smolkin.org` to `https://defunctcompanies.com$request_uri` on ports 80 and 443 using `/etc/letsencrypt/live/apps-smolkin/{fullchain,privkey}.pem`.
- **Result:** Added unit tests in `tests/test_launch.py`; **139 passed**.

### 2026-10-16 13:30–13:42 EDT — Companion Queue Research & Review (Queues 20–23)
- **Action:** Audited the 60 pending companies in `docs/episode-companion-queue.csv`. Grouped by episode to complete companion rosters for previously researched companies:
  - **Queue 20 (S12E14, 2021-02-19):** Researched **Pashion** (operating, convertible heels; SEC Form C-AR CIK 0001970090; declined O'Leary royalty offer), **Souper Cubes** (operating, silicone freezing trays; USPTO Reg. 5545717; Lori Greiner Golden Ticket deal), and **Sienna Sauce** (operating, gourmet sauces; USPTO Serial 90028169; Kendra Scott on-air offer did not close in due diligence). Together with Byoot (Queue 18), completes S12E14.
  - **Queue 21 (S11E4, 2019-10-20):** Researched **Knife Aid** (operating, mail-in sharpening; CA C413196; Lori Greiner/Rohan Oza offer did not close), **Plop Star** (operating, toilet deodorizing tablets; USPTO Serial 87654291 under Tandem, Inc.; all Sharks passed), and **Snacklins** (operating, plant-based crisps; DC entity 2015; Mark Cuban Companies portfolio). Together with Bug Bite Thing (Queue 15), completes S11E4.
  - **Queue 22 (S12E7, 2020-12-04):** Researched **Holiball** (operating, giant inflatable ornaments; Mark Cuban Companies portfolio), **Toilet Timer** (operating, Katamco LLC; on-air offer from Mark Cuban), and **ODR Skis** (operating, ski-skates at odrskis.com; all Sharks passed). Together with Buckle Me Baby Coats (Queue 14), completes S12E7.
  - **Queue 23 (S14E19, 2023-04-07):** Researched **Parting Stone** (operating, solidified cremated remains; Lori Greiner & Kevin O'Leary deal), **Cincha Travel** (operating, luggage travel belts; Barbara Corcoran deal), and **Milkify** (operating, breast milk freeze-drying; Lori Greiner & Gwyneth Paltrow convertible note deal). Together with Burlap & Barrel (Queue 17), completes S14E19.
- **Action:** Created structured research files:
  - `src/dct/data/research_batch_2026-10-16_queue-20.json`
  - `src/dct/data/research_batch_2026-10-16_queue-21.json`
  - `src/dct/data/research_batch_2026-10-16_queue-22.json`
  - `src/dct/data/research_batch_2026-10-16_queue-23.json`
- **Action:** Created companion review documents:
  - `docs/QUEUE-20-COVERAGE-REVIEW.md`
  - `docs/QUEUE-21-COVERAGE-REVIEW.md`
  - `docs/QUEUE-22-COVERAGE-REVIEW.md`
  - `docs/QUEUE-23-COVERAGE-REVIEW.md`
- **Action:** Updated `docs/episode-companion-queue.csv` marking the 12 companies with their reviewed batch status.
- **Action:** Added `TestNewQueues` in `tests/test_launch.py`; all **141 tests pass**.
- **Result:**
  - Total tracked companies: **113** (up from 101).
  - Published articles: **94** (up from 82, all 12 pass verification gate as active).
  - Withheld: **19** (exact 19 unresolved records, unchanged).
  - Total sitemap URLs: **103** (94 articles + 7 hubs + index + methodology).


### 2026-10-16 13:43–13:47 EDT — Production Build, Deployment, and Live Verification
- **Action:** Committed Queues 20–23 research batches, coverage reviews, queue updates, and tests in commit `1411823` (`Add reviewed twentieth through twenty-third Shark Tank batches`). Merged `launch-defunctcompanies` into `main` and pushed both branches to GitHub `origin`.
- **Action:** Executed production static site build with live Umami tracking enabled:
  ```bash
  DCT_UMAMI_WEBSITE_ID=d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014 DCT_PYTHON=.venv/bin/python3 npm run build
  ```
  Generated 122 pages (94 published articles, 19 withheld research-only records, 7 collection/status hubs, index, methodology, and 103-entry sitemap.xml).
- **Action:** Deployed `dist/` to the live Hetzner host (`167.233.238.194`):
  ```bash
  rsync -avz --delete dist/ root@167.233.238.194:/var/www/defunctcompanies.com/
  ssh -i ~/.ssh/bookmap-hetzner root@167.233.238.194 "chown -R www-data:www-data /var/www/defunctcompanies.com"
  ```
- **Action:** Installed and enabled `/etc/nginx/sites-available/defunct-company-tracker-articles.apps.smolkin.org` on `167.233.238.194`, symlinked to `sites-enabled/`, verified `nginx -t`, and reloaded nginx.
- **Action:** Verified live endpoints over public network:
  - `curl -sI https://defunctcompanies.com/` -> `HTTP/2 200`
  - `curl -sI https://defunctcompanies.com/companies/souper-cubes.html` -> `HTTP/2 200`
  - Verified Umami tracking tag present in live HTML: `<script defer src="https://umami.smolkin.org/script.js" data-website-id="d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014"></script>`
  - `curl -sI https://defunct-company-tracker-articles.apps.smolkin.org/companies/souper-cubes.html` -> `HTTP/2 301`, `location: https://defunctcompanies.com/companies/souper-cubes.html`
- **Action:** Tested inbound SSH connectivity to Michael's MacBook (`MBP.local` / `100.64.0.3`). Direct inbound SSH requires public key installation in MacBook's `~/.ssh/authorized_keys`. Prepared clipboard-piped command (`pbcopy`) for fast pull and test execution on MBP.
- **Action:** Wrote detailed `AGENT-RUN-REPORT.md` covering executive summary, research breakdown, metrics before vs. after, live verification, and decision items.

---

## Current State & Next Steps

### Current State
- **Live Site:** https://defunctcompanies.com is fully operational with 94 published verified company articles and active Umami analytics.
- **Old Subdomain Redirect:** `defunct-company-tracker-articles.apps.smolkin.org` cleanly 301s to `https://defunctcompanies.com` with path preservation.
- **Git State:** `launch-defunctcompanies` and `main` branches are aligned with `origin` on GitHub (`git@github.com:smolkapps/defunct-company-tracker-articles.git`).
- **Tests:** 141 tests passing in `.venv/bin/pytest`.

### Next Steps (for Michael)
1. Pull and test on MacBook via clipboard command:
   ```bash
   cd ~/Documents/projects/2026/defunct-company-tracker-articles && git fetch origin && git checkout launch-defunctcompanies && git pull origin launch-defunctcompanies && .venv/bin/pytest
   ```
2. Consider submitting `https://defunctcompanies.com/sitemap.xml` to Google Search Console and Bing Webmaster Tools.
3. Review decisions in `AGENT-RUN-REPORT.md` regarding legacy non-Shark Tank companies and future companion queue processing.




## 2026-10-16 — Monetization continuation (current scope)

- Current user goal: monetize the website; do not duplicate completed launch work.
- Current authority: local changes/commits only; no push, deploy, SSH, server/DNS or paid-service changes. This supersedes the operational scope in the historical Goal section for this run.
- Reverified 141 passing tests and successful production build: 94 published, 19 withheld, 7 hubs. Public checks confirmed live analytics tag, correct canonical, 103 sitemap URLs and path/query-preserving old-domain 301. Actual log ingestion and earnings remain unverified.
- No revenue integration exists. Researched primary merchant/network program pages; Cincha Awin is a concrete publisher candidate, Pashion requires creator eligibility review. Details and completion requirements saved in docs/MONETIZATION.md.
- Asked Michael for revenue-model preference. Next: implement the chosen bounded integration using real approved destination(s), verify locally, then seek only the final authority needed for live activation.
- Portfolio catalog still contains the former domain/counts; update locally to verified public state, preserving unrelated entries.

### Optional direct-merchant affiliate preparation
- Added disabled-by-default DCT_AFFILIATE_LINKS JSON config and Python override. Validates HTTPS links and displays only on verified active articles. Adds preceding disclosure, sponsored link attributes and company-specific Umami click event attributes.
- Added 9 tests covering default omission, config precedence, unsafe destinations, active/closed/unverified separation and escaped tracking query strings. 150 tests pass; production build succeeds.
- Inspected Cincha preview disclosure in the in-app browser with example.com URL; no real tracking links configured or clicked. Closed preview tab/server. Mobile QA, merchant approval/link issuance and live activation remain outstanding. No push/deploy/SSH.

### Responsive verification and activation boundary
- Rechecked clean branch at 07e81ca. Opened the task-owned local preview at 390×844; DOM confirmed innerWidth 390, no document horizontal overflow, and affiliate block within x=20..370. Inspected mobile screenshot; disclosure and shop link visible. Desktop screenshot was clipped by the browser display surface, so retain earlier desktop inspection rather than claim a new full-width visual pass. Console reported no warnings/errors. Closed preview and restored viewport.
- No merchant tracking URL, affiliate approval, revenue-model answer or deployment authorization has arrived. These remain required for live revenue activation. Do not turn placeholder links into production offers or repeat implementation work.

### October 16 — Owner authorized monetization deployment
- Michael delegated revenue-model selection and explicitly authorized deployment. This supersedes the earlier deployment restriction for necessary monetization work. No new spending/outreach or git push inferred.
- Chose relevant direct merchant affiliates; current configured links remain empty. Awin Cincha application opened read-only in agent-owned browser; requires confirmed account/payee/tax residency. Asked Michael for existing account or accurate details. No submission or agreement acceptance.
- Dedicated Grok app is signed out; no bot message sent. Many local coding-agent processes were active, so no additional local worker was spawned.
- SSH confirmed actual nginx root /var/www/defunctcompanies.com and absent current symlink: repo deployment assumptions differ from live setup. Active origin log verified with aggregate-only output: 2,203 requests, not human demand.
- Next: resolve account access, obtain approved earning link, complete appropriate release verification, deploy against actual root with backup, and verify attribution.

### October 16 — Sole trader enrollment authorized
- Michael confirmed no existing Awin account and authorized sole trader setup using Defunct Company Tracker as the publisher brand and his real name for legal details.
- Opened Cincha-linked Awin signup in the agent-owned in-app browser and entered the publisher brand. Awin explicitly permits a website name here for an unregistered business.
- Tax-residency choice is required before personal/login fields are enabled. Asked Michael to confirm the country; do not infer residency from location.
- Account email will be [private account address omitted] per standing registration guidance. No account has been created, no password entered, no agreement accepted, no deposit paid and no tax/bank data requested in chat.
- Browser tab retained for handoff. Once residency is confirmed, continue permitted setup; owner must handle new-password entry under browser rules and directly enter sensitive tax information when required.

### US residency confirmed — password handoff
- Michael completed the required residency selection directly; the selected state was verified without retaining the private enrollment detail here.
- Filled authorized name and [private account address omitted] plus email confirmation. Publisher brand remains Defunct Company Tracker.
- Password fields left empty, no account submission performed. Shown and retained in-app browser tab for owner to enter new password and confirmation directly. Browser rules require owner handoff for new credential entry.
- Tax ID/W-9/bank entry has not been reached. Resume promotional profile preparation after owner completes password step; inspect before any agreement/deposit action.

### October 16 — Credentials email delivered; Awin final verification reached
- User completed the new-password step directly, supplied existing sign-in details and explicitly requested a credentials email to himself. No password copied into repository/docs/artifacts.
- Email sent only to michael@smolkin.org via verified Postfix/OpenDKIM on ctdsu; deduplicated To/BCC envelope. Message-ID <179218853924.50290.2274493853410184992@smolkin.org>, queue 845756A830; DKIM added for smolkin.org and recipient mail provider accepted with 250 2.0.0 Ok at 2026-10-16T22:09:03Z. Email correctly says application not yet submitted/approved.
- Completed promotional setup: primary region United States, Editorial Content primary type, https://defunctcompanies.com, factual source-cited editorial description, relevant Clothing Accessories/Home & Garden/Gadgets sectors. No audience/revenue claims.
- Reached step4 final verification. Missing required private address/telephone; terms/age consent checkbox remains unchecked and Join Our Network not pressed. Optional newsletter remains unchecked. No deposit displayed on this step.
- Preserve signup tab for owner to enter address/telephone directly; do not collect those or tax IDs in chat. Terms acceptance requires action-time owner confirmation under browser policy, despite general signup authority. Tax form not reached.

### October 16 — Awin application receipt observed
- Michael reported completing address/phone and authorized terms review and submission. Reviewed Awin user agreement, privacy policy, US publisher terms (August 2025), GDPR/US privacy annexes and publisher code. US PDF initially blocked with encoded URL; official decoded URL with browser User-Agent/Referer retrieved successfully for text review.
- Before any agreement checkbox/submission action, a read-only browser check found the existing signup tab at /publisher-signup/us/awin/success. AX showed Application Received and review-pending message. This agent did not click the final checkbox or submit; do not attribute that action to this agent or infer who performed it. No duplicate submission attempted.
- Receipt screenshot saved outside repo at /tmp/dct-enrollment-evidence/awin-application-received.jpg; no address/phone/password captured. No signup deposit paid by this agent.
- Important terms: paid commissions depend on advertiser payment and complete tax/bank details; missing payment details for 12 months after a failed self-billed payout can forfeit funds; six months inactivity/no commissions can lead to termination and related forfeiture. Sole-trader warranties/indemnity, publisher privacy/consent requirements and restrictions on off-network advertiser payments require attention.
- Next: actual Awin acceptance/email activation and Cincha advertiser approval, then approved tracking link, privacy/consent implementation and live deployment. Application received is not acceptance, monetization or revenue. Owner enters W-9/tax and banking directly when requested.

### October 17 — Approval verified and email activated
- Verified connected Gmail account belongs to Michael. Focused Awin search found approval email for Defunct Company Tracker, publisher ID3126329, received October16, and separate user-email validation. Authentication headers pass DKIM/DMARC for awin.com.
- Opened official activation link in agent-owned browser; visible Account Activated confirmed success. No activation token retained in repo.
- Signed in with owner-supplied existing password. Reached /idp/us/awin/2fa/intro, offering authenticator setup or skip. No new MFA credential generated or retained. Shown/retained page for owner to set up authenticator directly under browser credential handoff rules. No skip or security change performed.
- Cincha status/link still unverified because dashboard has not yet been reached. Tax/bank form not reached. Continue after owner completes two-step verification; do not repeat signup or email activation.

### October17 — Optional MFA skipped; Cincha confirmed pending
- Michael explicitly instructed skipping optional two-step verification now. Clicked the displayed skip action and reached the approved publisher3126329 dashboard. No authenticator credential created/extracted/emailed.
- Cincha98075 already shows Pending advertiser approval in directory and profile. No duplicate application or outbound message sent; no earning link enabled. Dashboard payable/approved/pending commission balances all USD0.00.
- Profile was 75% complete, missing only image. Uploaded existing public site favicon-192.png through profile chooser and saved. Verified loaded profile image at publisher3126329 image path; incomplete-profile banner disappeared on subsequent account page. No personal image or private source uploaded.
- Checked Payment Details read-only: explicit two-step verification requirement blocks access. Optional skip works for dashboard but not tax/banking settings. Do not imply tax setup can proceed without MFA. No tax/bank fields touched; owner handoff for credential creation remains required when payout setup is needed.
- Saved non-sensitive pending-program and payout-gate screenshots outside repo. Await Cincha's actual approval; complete privacy/consent obligations before tracking activation and deploy.

### October17 — Strategy corrected to traffic-led monetization
- Michael asked whether we were ranking existing article demand and comparing programs instead of arbitrarily prioritizing Cincha. Answer: not yet; earlier focus was driven by an easily verifiable program, not traffic evidence. Corrected priority to traffic-led candidate selection.
- Read-only aggregate Umami query: dedicated site property contains27events/26sessions between2026-10-16T08:05:23Z and2026-10-17T19:01:41Z. All hostname defunctcompanies.com. Article rankings: WeWork3views/3sessions; Browndages2/2; BusyBox, Cabinet Health, FTX, Cabana Boys, Brush Hero1/1 each. Cincha not among observed article events. No marked qa/preview/audit query strings in these article rows; this does not prove human/organic traffic or exclude unmarked owner checks. No raw visitor identifiers retained.
- Dataset is too small/young to estimate conversion or earnings. Next: corroborate bot-filtered origin article demand and referrers, compare relevant programs for visited operating companies, and prioritize commercial fit/approval likelihood/payout reliability rather than the existence of a program. Keep closed-company informational traffic separate from shopping intent.
- In-progress privacy preparation completed as a local draft only: footer-linked noindex privacy/affiliate page reflects analytics/config state and links Awin policy;151tests and production build pass(123pages,94articles,19withheld,103sitemapURLs). No new consent flow or compliance certification claimed. Responsive visual verification and tracking-consent design remain before deployment. No live affiliate links or deployment in this step.

### Traffic-led program comparison completed
- Corroborated article-demand baseline with read-only origin aggregates across2logfiles:1,686article200GETs, but much unclassified/none/internal-referrer traffic and no verified human conversion signal. Logged UTC date span differs from Umami; no ingestion-ratio claim. No raw identifiers saved.
- Compared exact-brand programs in docs/MONETIZATION.md. BusyBox direct affiliate program merits investigation, but current Apply Now leads to Shopify signup/free-trial page and Awin US directory has0matches. No paid account created.
- HelloPrenup's first-party commission/cookie contradictions and broad non-disparagement make it unsuitable for automatic enrollment. Brush Hero FlexOffers says unavailable. Fish Fixe customer referral not assumed publisher-eligible. Browndages active store but no established publisher terms. Cabinet current site emphasizes B2B, so consumer offer needs revalidation.
- Cincha retained only as pending candidate; no revenue claim or unrelated links. Next: verify actual free BusyBox publisher route and continue demand/intent evidence.

### BusyBox application route and bounded next action
- Confirmed first-party Apply Now resolves to generic Shopify signup, while official Shopify docs say new creator self-signups are closed but merchant invitations/applications remain possible. No paid-store signup or new credential created.
- Focused Awin/Cincha Gmail query returned no new matching response; advertiser acceptance still unproven.
- Prepared one truthful BusyBox inquiry in docs/MONETIZATION.md asking correct publisher route, commission, attribution and payout terms. NOT SENT. User authorization is required for third-party email under standing outgoing-email rule; ask once for this specific concrete message.
- No writing-style connector was available in tool inventory; draft uses the user's direct conversational style without claiming retrieved style evidence.

### October 19 — Review new Awin advertiser invitations (in progress)
- Goal: retrieve current SimpleProject and World Businesses for Sale program terms, assess audience relevance and conversion economics, and activate only a worthwhile, properly approved partnership.
- Starting state: branch launch-defunctcompanies at 01980ac; only pre-existing untracked AGENTS.md. Existing optional affiliate implementation and privacy page found; prior records show publisher3126329, Cincha pending, no configured earning links and USD0 observed commission balances on October17. Reverify current account state before relying on it.
- Capacity inspected on actual Mac Studio (18 cores,36GiB); one bounded read-only public-program researcher delegated. No builds or overlapping project edits delegated.
- Connected Gmail profile matches [private account address omitted]. Use task-owned in-app browser or authorized agent-owned Camoufox; preserve personal browsers and unrelated changes. Retrieve terms before any acceptance; binding acceptance needs concrete owner approval under browser policy.
- Next: read invitation messages, inspect authenticated programs and payout/transaction state, record verified terms/unknowns, make a go/no-go decision. No acceptance, tracking configuration, deployment, purchase or third-party message performed.

### October 19 — Invitation terms retrieved; both offers rejected for placement
- Read the three exact Gmail messages in the verified account. Retrieved both complete program-terms PDFs (SimpleProject99013, five pages/Aug20 2025; WBFS116725, three pages/Jun2 2025), verified byte sizes/hashes, extracted all text and inspected rendered pages. Private source files and sanitized aggregates retained under ~/.local/share/codex/dct-awin-review-20261019; no acceptance tokens or credentials added to repo.
- Reviewed current official Awin profiles, merchant affiliate/shipping/pricing pages and network payment rules. Official US LTD August2025 PDF initially403 via web; documented browser-UA/decoded-URL fallback succeeded. No terms accepted. Full findings added to docs/MONETIZATION.md, including attribution, exclusions, reversals, payment/funding/forfeiture, geographic and promotional limits and unresolved conflicts.
- Decision: reject SimpleProject for weak audience relevance and unresolved effective rates/exclusions. Reject WBFS activation for current audience: 20% claim applies to selling-plan purchases, not business sale value; 30-day editorial/60-day creator attribution,60-day validation, variable bonus and ambiguous eligible SKUs/rate need account confirmation. No seller-intent evidence supports forecast. Invitations left unaccepted, not account-side declined.
- Fresh read-only Umami aggregates (Oct16T00:00Z through Oct19T22:24Z exclusive, before review requests):60pageviews48recorded sessions13article views,0affiliate-click events. Known QA/test markers excluded; bots/unmarked owner traffic can remain. No raw visitor identifiers retained.
- Live HTTP audit: all103sitemap URLs/94articles200, no sponsored or Awin/ShareASale hrefs. Static href audit doesn't prove every deployed file or dynamic integration absent. Local privacy.html template is not live (404); future activation must deploy disclosures/appropriate consent and reconcile actual nginx root versus release-script assumptions.
- Dedicated in-app browser is signed out at existing account's password screen; owner sign-in requested for current membership/transactions/payout settings. Current account balance not verified; prior Oct17 dashboardUSD0 remains historical evidence. No actual commission from either invitation verified. No tracking URL issued/clicked or fake transaction/purchase, website code/configuration change, deployment or advertiser outreach.
- Verification: complete terms review, primary-source cross-check, read-only SQL aggregates and live sitemap href audit. No application tests/build/browser layout suite run because this change is documentation-only and no site is being built or deployed. Preserve pre-existing untracked AGENTS.md. Next: do not activate either invitation; if signed in, optionally refresh account balances and effective terms. Revisit only on genuine contextual demand and resolved terms.
- Independent factual review checked public sources, calculations and decision wording. Corrected one overbroad attribution unknown: network clause5.2 establishes most-recent-referral by default, subject to explicit exceptions/hierarchies; WBFS-specific overrides, cross-device and coupon details remain unverified. Documentation whitespace check passed. Source PDFs/aggregates remain private local evidence.

### October 21 — Active goal: real audience, usefulness and monetization
- User clarified invitations should remain available for other sites. Previous work was progress: full terms/economics reviewed and no account-side decline/acceptance performed. Preserve both invitations; don't equate a placement recommendation with declining a partnership.
- Full current goal: resolve site issues, examine last24h traffic and Google/search/AI referrals using stronger bot/owner evidence, improve useful visitor journeys, and pursue a contextual monetization path without artificial transactions. Explicit AEO mining skill loaded; actual background queries will be distinguished from historical referral evidence.
- Actual worktree2e3b8d4 on launch-defunctcompanies; only unrelated untracked AGENTS.md. Capacity checked18cores36GiB/~51%free; bounded read-only UX audit delegated, plus AEO access/mining preparation. No overlapping writes/builds delegated.
- Operations source moved to ~/.local/share/central-telemetry-20261020/operations; read current status/registry/Umami contract. Shared prepared collector holds do not authorize runtime changes; this task uses a bounded on-demand read-only site-specific diagnostic, no collector/runtime/TCC/signing changes. Initial fetch failed due stale /usr/local/bin/gh credential helper; use a per-command correct installed helper without changing global config.
- Next: frozen24h site-only analytics/origin correlation, preserve anonymous visitor data, select fixes from observed paths, verify preview+deployment+activation measurement. Current earning balances still require account evidence; no merchant terms acceptance inferred.
- Frozen diagnostic window [2026-10-20T05:15Z,2026-10-21T05:15Z):15Umami pageviews/15sessions/15visits,4Google referrals (GrooveBook/LARQ/BottleBreacher/Poppi),0customevents,0Bing/DDG/AI referral rows. All single-page sessions; no measured time is not proof of instantaneous bounce. Sources and referrers can be spoofed; no human-count claim.
- Origin same-window525successfulHTML requests after8QArequest exclusions:166declaredbot/automation,359unclassifiedbrowser. All525logged source addresses are Cloudflare ranges; effective nginx -T has0trusted-realip directives. IP-based owner/unique counts are invalid proxy observations, not visitors. No raw IPs/useragents/querystrings exported. Prepared site-only trust/header+manifest MIME fix; not yet executed. Direct remote Cloudflarelist fetch failed; official web lists22networks match repo file and were verified unchanged.
- Useful improvements prepared: search name/aliases before table; collapsible originstory belowlist;3explicitly source-selected official websites (LARQ/Poppi/BigBee), separate official-site-click intent events and nocommission claim; share canonical report URL; privacy/footer rollout; literalwwwdomainbugfixed. Dates of3storefront checks updated without changing historicalstatusasof.
- Preview discovered mobiletableminimumwidth overflow; reused accessible localhorizontal-scrollwrapper. Added actualsystemdarkpalette and stylesheetcachebust. Modelhelper37tests passed; fullsuite157passed after2newnavigation-invariant tests; targetedsite11passed. Newtestfixtures initially omitted requiredsummary and were corrected; no skipped tests. Build94articles19withheld123pages, link/imageguard0errors.
- Independent deployreview caught second-resolution stagecollision and missingemptyarticle guard; corrected to remoteunique mktemp/uniquebackup and pre-SSH company-page guard. Deployment now stages, site-locks, backs up actualroot, delaysfileupdates and restores onfailure; no fictitiouscurrentsymlink. Fullsitehash/liveverification still pending.
- AEO:2seeds+2followups completed in authorizeddedicatedproject using observedInstant1/5,savedgpt-6; ownresearch05:16:23-05:20:44UTC afterfrozenwindow. GrooveBook was cited in syntheticanswer, not organicreferral. Actualbackgroundquerypayloads were unavailable/blank;0querystrings extracted, modelinvented lists excluded. Sources/receipts private ~/.local/share/codex/dct-aeo-20261021. Own2newminingchats retained as evidence; unrelatedchats untouched.
- Monetization investigation: LARQofficial8%/30dayclaims viaImpact strongestexact-brand lead, but actualsignuplandingblank/noaccessiblecontract; noaccountcreation/enrollment. BottleBreacherFlexOffersinactive; Poppicreatorcontact/campusprogram doesn'testablishpublisherterms. BothpriorAwininvitations stillunaccepted by thisagent; another site requires declaredpromotionalspace/advertiserapproval. No affiliatecodes, purchases, actualcommissions or outreach.
- Final validation:159tests passed,0skips; final affected50tests passed afterprivacycitationcorrection. Production94articles19withheld123HTML103sitemapURLs; link/imageguard0errors, shellsyntax/diffwhitespacepass. Live desktop1365×900/mobile390×844 light/dark, Poppi alias1row/clear94/no-match0, no pageoverflow, accessiblelocaltablescroll, actualcanonicalclipboardreadback passed. Root inspectedfinalmobilelight/darkscreens andexistingOG/favicon. Text/link/badgecontrastminimum4.98:1. NativeOSshare usedstub; physicalmobile,Lighthouse,actualunfurl,GSCaccountindexingnotverified. Existing192/512icons retaintransparentcorners/maskableentry; preservedartwork, notbrandingcertification.
- Deployedtoactualdocumentroot withfullbackups at05:33:01,05:36:18 andfinal05:37:21UTC; finalbackup /var/www/defunctcompanies.com.backups/20261021T053721Z-Ec83DmSK. All138originfilesmatchlocalbytehashes,noextras. Publicassetsmatchbytes, privacy/root/robots/sitemap200, brandedunknownURL404, manifest200application/manifest+json. This is delayedper-fileupdate, notatomicwholesiteswitch.
- Executedsite-onlynginxrealIP/manifestfix; nginx-t/reloadpassed, pre-existingunrelatedprotocolwarningspreserved. Backup /var/backups/defunctcompanies-nginx/20261021T053418Z. MarkedpublicCFrequestnowlogsnonCFclient; directoriginforgedCFheaderstaysloopback,rejectsspoof. No historicalclientIPrecoveryclaimed; no otherhost/runtime/collectorchange.
- IndexNow:deployedpublicownershipfile, verifiedHTTP200bytes, submittedONE103-URLPOST05:40:57UTC, HTTP202accepted/keyvalidationpending. Notindexing/ranking/visitors. InitialurllibGET403occurredbeforePOST; browser-UA/curlpublicGETconfirmedfile, notrepeatedsubmissions.
- Liveactivationproof:defaultCamoufoxUBOblockedUmamiscript(NS_ERROR_ABORT); freshownedcontextwithoutdefaultaddonloadedSDK200. Itsnetworkobservermissedsends,butauthoritativeDBread05:45:47confirms1markedCamoufoxpageview05:43:27.788Z+1official-site-click05:43:28.180Z, andindependentinappQApageview05:45:22.791Z+click05:45:29.373Z withcompanylarq/hostwww.livelarq.com. TwoactualvisibleQAclicks, nofakePOSTs,affiliateclicks,purchases orcommission. Firstmerchantnavigationaborted; secondreachedofficialhomepage. Excludemarkersqa=20261021-launch/20261021-iab. Earlier13Camoufoxdocumentvisitsmostlyanalyticsblocked; nohumantrafficclaim.
- Bothinvitationoffersremainuntouchedaccount-side. LARQcontract/currentAwinbalancesstillrequireactualaccountaccess; noacceptanceorcredentialscreated. Fullsource/economics/trafficanalysisandlimitsappendeddocs/MONETIZATION.md; privateaggregatereceipts .work-artifacts/audience-20261021/.
- Canonicaloperationsregistry updatedandpushed318cf79 inisolatedworktree; localunversionedportfolioJSONandmatchinghumanrowsupdatedDCTonly,120unrelatedproductobjectspreserved. Follow-upmarked-QApersistenceproofupdatepending; no sharedoperationscheckout/telemetryworkoverwritten. Next: commit/pushprojectrepair, finishregistryproof, closeownedpreviewserver; reportaccount/contractlimitswithoutclaimingrevenue.
- Completion checkpoint: repair/source/evidence committedcd99f55 andpushedorigin/launch-defunctcompanies; remoterefverifiedmatches,onlypre-existinguntrackedAGENTS.mdremains. Operationsfollow-up ec3735a recordsvalidatedQA-onlyactivation; catalog/humanrowsreconciled. Alltask-ownedCamoufox/inappverificationtabsclosed; ownedpreviewPID2525terminated. NoAwinaccept/decline,outreach,purchase,faketransaction orrevenueclaim. Requesteddiagnosis,focusedrepairs,liveverificationandmonetizationassessmentcomplete; futureworkrequiresanewpost-fixtrafficwindowandactualrelevantpublishercontract/accountaccess, notinventedhumanvisitororcommissioncounts.

## 2026-10-21 — partnerships email responder
Michael requested onboarding this site with partners@ focused on monetization. Implemented in isolated /Users/michael/Documents/projects/email-responder-defunct-partners, branch codex/defunct-partners, source7cb59ea and receipt989fb71; preserved older dirty email-responder checkout. Deployed source through Git-bundle fast-forward without push. Configured site mail MX/SPF/DKIM/DMARC and backed up host mail configuration. partners@ receives into agent mailbox plus Michael; other addresses forward only. Existing judge/triage/BCC/holiday gates unchanged. Existing autonomous mode/master1/delay1minute retained. 42 responder tests passed locally and live, no skips. Owned inbound captured/ingested and guard-declined; signed sender notice accepted by Michael's provider (queue CFA0B6A842). Real partner LLM reply still untested. No BusyBox outreach sent, tax/contract/payment/revenue action. Full rollback and delivery receipt in responder WORKLOG-DEFUNCT.md. No website code or deployment changed.

## 2026-10-21 — sent history and correspondence-to-site follow-through
User requested fixing missing conversational memory and tracking everything needed for website updates. Responder source8d22a22 deployed via Git-bundle fast-forward; additive DB backup queue-pre-history-20261021T170248Z.db retained. Shared bounded site/correspondent-scoped evidence includes initial registered outreach, prior inbound and actually sent replies in triage/drafting/judge. Resolves In-Reply-To-only chains through sent IDs. Held drafts excluded. Added durable idempotent private site_work queue and recorded-purpose initial inquiry import (never sends). 48 tests pass locally/live,0skips. Host services active, clean source. Live tracker has only1owned guard-blocked inbound, no real partner messages/sent replies/inquiries/pending tasks. No outreach or website deployment in this step.
Created ACTIVE daily10:00 project automation defunct-partnership-follow-through to review queue plus Awin messages and implement verified authorized site updates, quiet when unchanged. Future execution is not claimed. Durable procedure/candidate states/limits in docs/PARTNERSHIP-LEDGER.md. No earning link or commission verified. No GitHub push; user-provided untracked AGENTS.md preserved.

## 2026-10-22 — Partnership follow-through automation

- Confirmed no other agent owns this worktree; the sole untracked `AGENTS.md` remains user-provided and untouched.
- Read the canonical operations status, partnership ledger, and private responder queue from its required `/opt/email-responder` working directory. The queue returned zero pending `defunctcompanies` items.
- Verified the connected Gmail identity, then reviewed only recent Awin/Cincha candidate mail. A DKIM-authenticated October21 Awin reminder indicates an advertiser application remains pending; no Cincha approval or issued affiliate link appeared through this review. A new October20 `brkox` invitation and the October19 World Businesses for Sale invitation remain unaccepted. Their terms were not opened or accepted.
- Updated `docs/PARTNERSHIP-LEDGER.md` with non-sensitive evidence, exact activation blockers, and the new invitation state. No site change is justified: no approved relevant program, issued earning link, commission/payout terms, consent review, or queue task exists.
- No outreach, contract action, spending, tax/bank action, git push, build, deployment, or external state change occurred.

## 2026-10-23 — Partnership follow-through automation

- Confirmed no active process owns this project; the existing untracked `AGENTS.md` remains untouched.
- Read the current portfolio operations status, reviewed the private responder queue from `/opt/email-responder` as `clawd`, and verified it has zero pending `defunctcompanies` items.
- Verified the connected Gmail identity and bounded the mailbox review to recent Awin/Cincha evidence. No new approval or issued earning link exists. The October21 Awin reminder still records a pending advertiser application; the brkox and World Businesses for Sale invitations remain unaccepted and their attachments unopened.
- Recorded the non-sensitive evidence and exact activation blocker in `docs/PARTNERSHIP-LEDGER.md`. No site update, queue resolution, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-10-24 — Partnership follow-through automation

- Confirmed no active agent process owns this project; the existing untracked `AGENTS.md` remains user-provided and untouched.
- Read current portfolio operations status and reviewed the private responder queue from `/opt/email-responder` as `clawd`; it returned zero pending `defunctcompanies` items.
- Verified the connected Gmail identity and bounded the mailbox review to recent Awin/Cincha evidence. No approval or issued affiliate link exists. The October21 Awin reminder still records a pending advertiser application. A previously unrecorded October18 Shenzhen Cangyu Technology Co., Ltd. Awin invitation was found; it joins the preserved, unaccepted brkox and World Businesses for Sale invitations. Their attached terms were not opened or acted on.
- Updated `docs/PARTNERSHIP-LEDGER.md` with non-sensitive evidence and the exact activation blocker. No site update, queue resolution, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-10-25 — Partnership follow-through automation

- Confirmed no active process owns this project; the existing untracked `AGENTS.md` remains untouched.
- Read current portfolio operations status and reviewed the private responder queue from `/opt/email-responder` as `clawd`; it returned zero pending `defunctcompanies` items.
- Checked the connected Gmail account and ran bounded searches for Awin/Cincha mail and mail to `[private account address omitted]` after October24. Neither returned a new candidate. No approval, issued affiliate link, commission, attribution or payout evidence is available.
- Recorded the non-sensitive evidence and exact activation blocker in `docs/PARTNERSHIP-LEDGER.md`. No site update, queue resolution, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-10-27 — Partnership follow-through automation

- Confirmed no active process owns this project; the existing untracked `AGENTS.md` remains untouched.
- Reviewed the private responder queue from `/opt/email-responder` as `clawd`; it returned zero pending `defunctcompanies` items.
- Verified the connected Gmail identity and bounded searches for Awin/Cincha, `[private account address omitted]`, and partners@ candidates after October25. All returned no messages, so no approval, issued affiliate link, commission, attribution or payout evidence is available.
- Recorded the exact blocker in `docs/PARTNERSHIP-LEDGER.md`. No site update, test/build, deployment, contract action, spending, tax/bank action, outreach or git push is justified.

## 2026-10-28 — Partnership follow-through automation

- Confirmed no active process owns this project; the existing untracked `AGENTS.md` remains user-provided and untouched.
- Reviewed the private responder queue from `/opt/email-responder` as `clawd`; it returned zero pending `defunctcompanies` items. Verified the connected Gmail identity as `[private account address omitted]`.
- A bounded recent-mail review found one new DKIM-authenticated Awin invitation for TideWe. It is an unaccepted outdoor-gear invitation, has no established tracker-audience fit, and is neither program approval nor an issued tracking link. The linked terms were not opened or accepted.
- Recorded non-sensitive evidence and the continuing activation blocker in `docs/PARTNERSHIP-LEDGER.md`. No site update, queue resolution, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-10-29 — Partnership follow-through automation

- Confirmed no active process owns this project; the existing untracked `AGENTS.md` remains user-provided and untouched.
- Read current portfolio operations status and reviewed the private responder queue from `/opt/email-responder` as `clawd`; it returned zero pending `defunctcompanies` items.
- Verified the connected Gmail identity as `[private account address omitted]`. Bounded searches after October28 found no new Awin/Cincha approval, issued link, or partner-mail candidate; the only match was the already-recorded, unaccepted TideWe invitation.
- Recorded the continuing blocker in `docs/PARTNERSHIP-LEDGER.md`. No site update, queue resolution, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-10-30 — Partnership follow-through automation

- Confirmed no active project-owner process; the existing untracked `AGENTS.md` remains user-provided and untouched.
- Read the current operations status and reviewed the private responder queue as `clawd` from `/opt/email-responder`; it returned zero pending `defunctcompanies` items.
- Verified the connected Gmail identity as `[private account address omitted]`. Bounded searches after October28 found only a new October30 Awin Piscifun invitation. It is unaccepted fishing-gear outreach, not advertiser approval or an issued tracking link; no linked terms were opened or acted on.
- Updated `docs/PARTNERSHIP-LEDGER.md` with non-sensitive evidence and the continuing blocker. No approval, issued earning link, commission, attribution, payout, or credible tracker-audience fit exists; no site update, queue resolution, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-10-31 — Partnership follow-through automation

- Confirmed no active project-owner process; the existing untracked `AGENTS.md` remains user-provided and untouched.
- Read the current portfolio operations status and reviewed the private responder queue as `clawd` from `/opt/email-responder`; it returned zero pending `defunctcompanies` items.
- Verified the connected Gmail identity as `[private account address omitted]`. Bounded searches after October30 found one new Awin brickzonehub invitation. It is unaccepted brick-building retail outreach, not advertiser approval or an issued tracking link; no linked terms were opened or acted on, and no tracker-audience fit is established.
- Updated `docs/PARTNERSHIP-LEDGER.md` with non-sensitive evidence and the continuing blocker. No Cincha approval, issued earning link, commission, attribution, payout, or queue item exists; no site update, test/build, deployment, contract action, spending, tax/bank action, outreach, or git push is justified.

## 2026-11-01 — Canonical main source reconciliation

- Reconciled the completed `launch-defunctcompanies` source at `dd80ce0` and the completed October 31 partnership records into a single checkpoint descended from canonical main `b385abc`. Product source, reviewed research, deployment safeguards and tests are unchanged from the reviewed launch branch.
- Omitted unnecessary private account/login addresses and a personal residency detail from operational documents. Preserved the intended public privacy and merchant business contacts. The original branch/history, source checkout, dirty files and user-provided instructions remain untouched; this checkpoint integrates the reviewed content without introducing the original launch ancestry into public main.
- Verified the actual user context: demand-led monetization, replies grounded in their original outgoing purpose, and durable records for later verified site updates. The separate private Python copy remains separate. No new outreach, queue action, agreement, account change, live research, schedule change or website deployment occurred.
- Fresh offline checks: 159 tests passed, none skipped; fixture build produced 94 published articles, 19 withheld records and 123 HTML pages; site link/image guard reported zero errors; deployment shell and browser JavaScript syntax passed.
- Exercised local alias search, empty results, reset and the reviewed Poppi report at desktop and narrow widths. Fresh narrow light/dark previews have no page overflow; the bounded light preview has no console or request errors and preserves the reviewed canonical and official destination. This is local responsive evidence, not a physical-device or new production-release claim. The current native-share attempt had no completion signal; no fresh native-share success is claimed. Pre-existing Android icon transparency/maskable limitations remain recorded for later site maintenance.
- The partner invitations remain unaccepted. No verified earning link, merchant approval, commission or payout has been established, so monetized links remain disabled unless explicitly configured with verified destinations.
