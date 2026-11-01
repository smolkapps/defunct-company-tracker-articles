# Current local run report — 2026-10-16

## Outcome

Existing launch work was audited without duplication. Production build reports
113 tracked companies, 94 published and 19 withheld. This continuation published
zero additional companies; the existing 12 additions from queues 20–23 were
already present. 48 queue companies remain pending.

Public HTTP checks confirmed apex/article 200, dedicated Umami tag, correct
canonicals, 103 sitemap URLs with lastmod, and old-domain 301 preserving path
and query. Nginx log paths exist in repository configuration; actual server log
writes and analytics ingestion were not inspected.

Added optional direct-merchant affiliate config, disclosure, sponsored links
and Umami affiliate-click attributes. It is disabled by default and restricted
to verified active articles. No approved links, earnings or live activation
are claimed. Documentation: docs/MONETIZATION.md.

## Checks

150 tests passed; npm production build succeeded using .venv/bin/python.
Desktop preview inspected earlier; 390×844 responsive preview showed visible
disclosure/link and no document horizontal overflow. No console warnings/errors
were recorded. Physical mobile, real attribution/payout and provider enrollment
remain unverified. No code changed after that passing suite/build.

## Michael's decisions / access

- Confirm affiliate links as the revenue model, or choose sponsorship/tips.
- Provide an approved merchant tracking link/account access or authorize the
  specific enrollment flow once its terms can be reviewed. Cincha Awin 98075
  is the strongest verified candidate so far.
- Explicitly authorize deployment before enabling the prepared integration live.
  Earlier no-push/no-deploy/no-SSH/server-change restrictions remain in force.
- The older legacy-company and search-console decisions remain unchanged.

Local commits only. No push, deployment, SSH, server/DNS change, payment,
account registration or outreach occurred in this continuation. The goal
“Monetize the website” remains incomplete pending a real approved revenue path.

## Superseding checkpoint — October21,2026 partnership follow-through

Earlier approval/authority and deployment restrictions above are historical.
Project deployment is now authorized. partners@defunctcompanies.com is configured
on the existing mail responder with verified DNS/signing/inbound capture and an
owned sender notice accepted by Michael's provider. No external outreach sent.

The responder now loads saved inbound/sent history and registered initial inquiry
purpose for all three review stages, with site/correspondent isolation. It writes
an idempotent private website-review queue. ACTIVE daily project automation
`defunct-partnership-follow-through` checks that queue and Awin evidence, records
outcomes and makes verified authorized site updates. See docs/PARTNERSHIP-LEDGER.md.
48 responder tests passed locally and live,0skips. Real partner LLM replies and
future scheduled runs remain unverified. No approved earning link/commission.
No contracts, spending, tax/bank submission or git push. This step added0companies;
existing94published/19withheld remain. BusyBox outreach remains unsent; Cincha
approval requires a fresh account check before placement.
