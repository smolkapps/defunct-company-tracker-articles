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
