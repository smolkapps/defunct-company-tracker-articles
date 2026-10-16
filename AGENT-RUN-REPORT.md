# Defunct Company Tracker — Agent Run Report

**Date:** 2026-10-16  
**Target Domain:** https://defunctcompanies.com  
**Remote Host:** Hetzner Ubuntu 24.04 (`167.233.238.194`)  
**Git Branch:** `launch-defunctcompanies` (merged into `main` and pushed to `origin`)  
**Commit Range:** `540f536` -> `1411823`  

---

## 1. Executive Summary

All four prioritized goals and updated operational permissions have been executed, verified against the test suite, built, pushed to GitHub, and deployed live to production at https://defunctcompanies.com:

1. **Content Expansion (Goal 1):** Researched and added four new reviewed Shark Tank batches (**Queues 20, 21, 22, and 23**) covering 12 companion companies across four televised episodes. All 12 companies passed the verification gate (`verify_report`) with full citations and documentation.
   - **Total Tracked Companies:** **113** (up from 101, +12)
   - **Published Articles:** **94** (up from 82, +12)
   - **Withheld / Research-Only Pages:** **19** (unresolved records, unchanged)
   - **Total Pages Generated:** **122** (94 articles + 19 withheld + 7 hubs + index + methodology)
   - **Sitemap URLs:** **103** in `sitemap.xml` (all 94 published articles, 7 status/collection hubs, index, and methodology)
2. **Umami Analytics Support (Goal 2):** Implemented optional CLI/config/env-driven analytics integration (`src/dct/site.py`, `src/dct/cli.py`, `package.json`, and templates). Injected into every page when set, omitted when unset. Configured on the live server using dedicated website property `d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014` on `https://umami.smolkin.org`.
3. **Old Subdomain 301 Redirect (Goal 3):** Installed and enabled `/etc/nginx/sites-available/defunct-company-tracker-articles.apps.smolkin.org` on `167.233.238.194`. Verified that requests preserve `$request_uri` and return HTTP 301 to `https://defunctcompanies.com$request_uri`.
4. **Safe SEO Improvements (Goal 4):**
   - Enriched `<title>` and `<meta name="description">` tags across home, methodology, hubs, and article pages.
   - Added schema.org JSON-LD structured data: `WebSite` on homepage, `WebPage` on methodology, `BreadcrumbList` on all company articles, and `mainEntityOfPage` on `Organization` blocks.
   - Added contextual internal links: article breadcrumbs to category and status hubs, bidirectional "Other companies from this Shark Tank episode" cross-links, and "More verified companies" related links.
   - Added `<lastmod>` to `sitemap.xml` for `methodology.html`.
5. **Testing & Live Deployment:**
   - Test suite expanded from 135 to **141 passing tests** (`tests/test_launch.py`).
   - Merged `launch-defunctcompanies` into `main` and pushed both branches to `origin` (`git@github.com:smolkapps/defunct-company-tracker-articles.git`).
   - Deployed `dist/` to `/var/www/defunctcompanies.com/` on `167.233.238.194` owned by `www-data:www-data`.
   - Verified live responses: `https://defunctcompanies.com/` returns HTTP 200 with active Umami tracking script.

---

## 2. Research & Review Breakdown (Queues 20–23)

### Queue 20 — Season 12, Episode 14 Companions (Air Date: 2021-02-19)
Completes the companion roster for Byoot (previously reviewed in Queue 18).
- **Pashion** (Pashion Footwear Inc., CIK 0001970090, DE): Verified active e-commerce storefront at `pashionfootwear.com` selling convertible high-heel shoes; SEC Form C-AR filings verified through 2024. Declined Kevin O'Leary's $500,000 royalty offer on air.
- **Souper Cubes** (Souper Products, LLC, USPTO Reg. 5545717): Verified active brand with national brick-and-mortar retail and direct store at `soupercubes.com`. Received Lori Greiner's Golden Ticket deal ($400,000 for 5% equity).
- **Sienna Sauce** (Tortoise Investments, L.L.C. / Sienna Sauce LLC, USPTO Serial 90028169): Verified active direct-to-consumer store at `siennasauceco.com`. Kendra Scott's on-air offer ($100,000 for 20%) did not close during post-broadcast due diligence.

### Queue 21 — Season 11, Episode 4 Companions (Air Date: 2019-10-20)
Completes the companion roster for Bug Bite Thing (previously reviewed in Queue 15).
- **Knife Aid** (Knife Aid, Inc., California SOS C413196): Verified active mail-in knife sharpening service at `knifeaid.com`. The on-air deal with Lori Greiner and Rohan Oza ($500,000 for 20%) did not close post-show.
- **Plop Star** (Tandem, Inc., USPTO Serial 87654291): Verified active direct-to-consumer sales of portable toilet deodorizing tablets at `plopstar.com`. All Sharks passed on the televised pitch.
- **Snacklins** (Snacklins LLC, DC entity 2015): Verified active plant-based snack brand in national grocery distribution and online at `snacklins.com`. Mark Cuban's investment ($250,000 for 5% equity + 5% advisory shares) closed and is featured in the Mark Cuban Companies portfolio.

### Queue 22 — Season 12, Episode 7 Companions (Air Date: 2020-12-04)
Completes the companion roster for Buckle Me Baby Coats (previously reviewed in Queue 14).
- **Holiball** (Holiball, LLC): Verified active giant inflatable ornament e-commerce business at `theholiball.com`. Joint investment from Mark Cuban and Barbara Corcoran ($150,000 for 25%) closed and is listed in the Mark Cuban Companies portfolio.
- **Toilet Timer** (Katamco LLC): Verified active novelty bathroom sand timer business at `katamco.com` following an on-air agreement with Mark Cuban ($200,000 for 25%).
- **ODR Skis** (ODR Skis Inc.): Verified active ski-skate and wax business at `odrskis.com`. Founder Kevin Greco left without a deal after all Sharks passed.

### Queue 23 — Season 14, Episode 19 Companions (Air Date: 2023-04-07)
Completes the companion roster for Burlap & Barrel (previously reviewed in Queue 17).
- **Parting Stone** (Parting Stone PBC): Verified active death-care service at `partingstone.com` turning ashes into solidified stones, partnering with hundreds of funeral homes. Lori Greiner and Kevin O'Leary joint investment ($400,000 for 10% + royalty) closed.
- **Cincha Travel** (Cincha LLC): Verified active luggage travel belt business at `cinchatravel.com`. Barbara Corcoran deal ($200,000 for 25%) closed.
- **Milkify** (Milkify Inc.): Verified active concierge breast milk freeze-drying service at `milkify.me`. Lori Greiner and Gwyneth Paltrow deal ($400,000 for 20% convertible note) accepted.

---

## 3. Publication vs. Withholding Statistics

| Category | Before Run | After Run | Delta | Notes |
|---|---|---|---|---|
| **Total Tracked** | 101 | **113** | +12 | 100 Shark Tank + 13 legacy non-Shark Tank companies |
| **Published Articles** | 82 | **94** | +12 | Fully verified, indexable, in sitemap |
| **Withheld (Research-Only)** | 19 | **19** | 0 | Unresolved records kept with `noindex` and out of sitemap |
| **Active Status** | 55 | **67** | +12 | All 12 newly researched companies are active businesses |
| **Acquired Status** | 17 | **17** | 0 | Stable |
| **Defunct Status** | 4 | **4** | 0 | Stable |
| **Bankrupt Status** | 3 | **3** | 0 | Stable |
| **Renamed Status** | 3 | **3** | 0 | Stable |
| **Unknown Status** | 19 | **19** | 0 | Matches 19 withheld records |
| **Hub Pages** | 7 | **7** | 0 | Status and collection hubs |
| **Total Sitemap URLs** | 91 | **103** | +12 | 94 articles + 7 hubs + index + methodology |

---

## 4. Verification and Live Deployment Checks

- **Apex Domain:** `curl -sI https://defunctcompanies.com/` -> `HTTP/2 200`
- **New Article Sample:** `curl -sI https://defunctcompanies.com/companies/souper-cubes.html` -> `HTTP/2 200`
- **Umami Tracking Tag:** Verified on live article HTML:
  ```html
  <script defer src="https://umami.smolkin.org/script.js" data-website-id="d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014"></script>
  ```
- **Old Subdomain 301 Redirect:**
  ```bash
  curl -sI https://defunct-company-tracker-articles.apps.smolkin.org/companies/souper-cubes.html
  # -> HTTP/2 301
  # -> location: https://defunctcompanies.com/companies/souper-cubes.html
  ```

---

## 5. MacBook Sync & Verification

All commits have been pushed to GitHub `origin` (`smolkapps/defunct-company-tracker-articles`) on both `launch-defunctcompanies` and `main`. 

Attempted automated SSH sync from `macstudio` to Michael's MacBook (`MBP.local` / Tailscale `100.64.0.3`): incoming SSH to the MacBook returned `Permission denied (publickey)`, as Mac Studio's public key is not installed in the MacBook's `~/.ssh/authorized_keys`.

To pull the updated state onto Michael's MacBook without overwriting any uncommitted work:

```bash
cd ~/Documents/projects/2026/defunct-company-tracker-articles && \
git fetch origin && \
git checkout launch-defunctcompanies && \
git pull origin launch-defunctcompanies && \
.venv/bin/pytest
```

---

## 6. Decisions for Michael

1. **Legacy Non-Shark Tank Companies (13 companies):** The database currently retains 13 historical non-Shark Tank companies (Pets.com, Blockbuster, Lehman Brothers, Instagram, Sun Microsystems, WhatsApp, Theranos, Facebook, FTX, Quibi, SVB, Compaq, WeWork) grouped into the `other-companies` collection. Confirm whether to retain these as "Famous Failures & Exits" or remove them to make the site 100% Shark Tank-focused.
2. **Remaining Queue Backlog:** 48 companies remain in `docs/episode-companion-queue.csv` pending research batches. All 12 completed companions in this run closed their respective episode rosters.
3. **Google Search Console & Bing Webmaster Tools:** Once ready, submit `https://defunctcompanies.com/sitemap.xml` in Search Console and Bing Webmaster Tools to accelerate indexing of the 103 live URLs.
