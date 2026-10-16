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

## Next Steps
1. Commit Umami, SEO, and nginx redirect changes on `launch-defunctcompanies`, merge into `main`, and push both branches to `origin`.
2. Apply `deploy/nginx/old-subdomain-redirect.conf` on `167.233.238.194` (`nginx -t && systemctl reload nginx`) and verify 301 redirect.
3. Research and review new batches of queued Shark Tank companies from `docs/episode-companion-queue.csv` and `.work-artifacts/initial-work-release/company_ledger.csv` (Goal 1 — top priority), validate against `research-record.schema.json` and `verify_report`, commit and push as we go.
4. Build and deploy `dist/` with Umami wired in to `167.233.238.194`, verify HTTP 200 and live Umami tag, write `AGENT-RUN-REPORT.md`, and sync/document MacBook state.

