# Monetization checkpoint — 2026-10-16

## Verified starting point

The site is already live at https://defunctcompanies.com. Local tests pass
(141 tests); production build emits 94 published articles, 19 withheld pages,
7 hubs and 103 sitemap URLs. Public homepage and Souper Cubes article return
200, include the dedicated Umami website ID, and use the correct canonical.
The old subdomain returns 301 preserving path and query. Do not redo deployment.

Optional direct-merchant affiliate support is now prepared locally; no approved links are configured. No sponsor, payment or tip integration exists.
Revenue, engaged audience size, dashboard ingestion and origin log writes have
not been verified. A script tag is not evidence of recorded human visits or sales.

## Concrete revenue candidates

Sources checked 2026-10-16:

| Candidate | Verified program | Next requirement |
| --- | --- | --- |
| Cincha Travel | Awin advertiser 98075 lists 15% per sale and 30-day attribution: https://ui.awin.com/merchant-profile/98075 | Confirm publisher eligibility and approved account; obtain an issued tracking link. |
| Pashion | Convertible Club lists tiered commission on first-time customer sales and Instagram/TikTok posting tasks: https://pashionfootwear.com/pages/convertible-club | Confirm a reference publisher qualifies; do not assume a creator program accepts this site. |
| Souper Cubes | Public loyalty/referral pages found; publisher affiliate eligibility not established. https://www.soupercubes.com/pages/loyalty | Find explicit publisher terms before treating this as revenue. |

Program existence does not establish our enrollment, payout access or approval.
Do not invent affiliate identifiers, reuse another site's account without
approval, claim commissions are active, or use customer referral programs as
publisher affiliate programs without checking their terms.

## Proposed first experiment

Prefer a small set of approved merchant links on relevant, verified operating
company articles. Preserve editorial status decisions and source citations.
Show a clear commission disclosure before links, mark links sponsored, and
measure outbound clicks separately from purchases. An outbound click is intent,
not earned revenue. Withheld and closed-company pages should not receive
shopping recommendations merely because a similarly named product exists.

Michael delegated the revenue-model choice; use relevant merchant affiliate links as the first experiment. Before activation, obtain approved tracking links and verify provider
attribution and payout eligibility. Review actual traffic before expanding to
more programs. Sponsorships require honest audience evidence; no fabricated
reach claims. Tips require an owner-approved destination.

## Authority and completion

The active goal is to monetize the website. Michael subsequently authorized choosing the revenue model and deploying it (2026-10-16). Necessary deployment/server inspection is now authorized. Git push, unrelated server/DNS work, spending and outreach are not inferred from that authorization. Provider agreements and sensitive account details still require the appropriate owner action. No application has been submitted and no live monetization has been activated.
Historical WORKLOG deployment permissions describe a different agent's run and
do not override the current restrictions.

Completion requires a real approved revenue path enabled on the public site,
verified attribution/fulfillment as appropriate, and an honest measurement plan.
Research or a local disabled implementation alone does not complete the goal.

## Local configuration

Set `DCT_AFFILIATE_LINKS` to a JSON object mapping company slugs to approved
HTTPS merchant/network tracking URLs. It defaults to `{}` and adds nothing.
Example shape only (not a real earning link):

```sh
DCT_AFFILIATE_LINKS='{"cincha-travel":"https://example.com/approved-tracking-link"}' DCT_PYTHON=.venv/bin/python npm run build
```

The Python `SiteGenerator(affiliate_links={...})` argument overrides the environment;
an explicit empty dict disables it. Only published ACTIVE reports display links.
The disclosure precedes the link, with sponsored/nofollow attributes and Umami
`affiliate-click` / company-slug event attributes. Umami must be configured for
events to be collected. Do not use this generic block for Amazon: Amazon-specific
disclosures and approved site/account setup must be implemented first.

Verification: 150 tests passed; production build passed with no commercial config.
A separate temporary preview used an example.com destination and the disclosure
was inspected in the in-app browser. No commission link was clicked, no analytics
ingestion or attribution was proven. At 390×844, the disclosure block fits within the viewport (350px wide, no document horizontal overflow). Browser console returned no warnings/errors. These are responsive browser checks, not physical-device or attribution verification.

## Reopened activation — October 16

Deployment is now authorized. Read-only SSH confirmed nginx serves
`/var/www/defunctcompanies.com` directly, not its `current` subdirectory;
`current` is not a symlink. The current deploy script assumes the latter.
Before deploying, either prepare a reviewed migration to release directories
with rollback or deploy to the actual root with a full backup. Do not report a
symlink switch as a live deployment without checking nginx's effective root.

Origin access logging is active: the file contained 2,203 requests on October 16
at inspection (710 with clearly automated user agents, 1,493 other/unknown).
These are request counts, not human users or affiliate-ready traffic. No client
IPs or raw log lines were retained.

Awin signup for Cincha was opened in the agent-owned browser. It requires a
company/payee name and tax residency in addition to identity/login fields. No
fields submitted; existing-account status and tax residency requested from
Michael. Use `awin@michaelcli.com` only if a new account is actually needed.
Never guess residency or create a duplicate publisher account. The dedicated
Grok Bot app currently shows signed-out state, so its prior work is inaccessible.

Application description prepared from verified site facts:

> Defunct Company Tracker (defunctcompanies.com) is an independent reference
> site publishing source-cited company status articles, including Shark Tank
> companies. It currently has 94 published articles and 19 explicitly withheld
> research records. We propose disclosed editorial affiliate links on relevant
> verified operating-company articles. We do not claim an established audience,
> paid search program, coupon operation or existing affiliate revenue.

Before submitting, confirm legal account details, review current program terms
and any fee, and obtain action-time agreement confirmation if required by the
browser. Approval is an external provider decision; an application is not an
approved earning link.
