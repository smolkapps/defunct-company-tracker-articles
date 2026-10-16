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

A disabled direct-merchant implementation is prepared pending the owner's revenue-model preference (asked in chat). Before activation, obtain approved tracking links and verify provider
attribution and payout eligibility. Review actual traffic before expanding to
more programs. Sponsorships require honest audience evidence; no fabricated
reach claims. Tips require an owner-approved destination.

## Authority and completion

The active goal is to monetize the website. Earlier explicit restrictions still
prohibit git push, deployment, SSH, server/DNS changes and paid services. Local
preparation and commits are allowed. No account applications, outgoing messages,
payment changes or live monetization activation were performed in this audit.
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
