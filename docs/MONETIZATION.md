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

## Sole trader setup authorized

Michael confirmed there is no existing Awin account and authorized individual
sole trader enrollment under the Defunct Company Tracker publisher brand. Use
Michael Smolkin for legal identity and awin@michaelcli.com for account email.
The initial Company Name field explicitly allows a website name for publishers
without a registered business, so it contains Defunct Company Tracker.
Tax residency remains unconfirmed; the form disables personal/login fields
until a country is selected. The owner has been asked to confirm it.
No account exists yet; do not describe the brand-field draft as enrollment.
New-password entry is owner handoff under the browser's credential rules. Tax
IDs/W-9/banking must be entered directly into the provider, never chat or git.

## Current Awin handoff: final verification

US residency confirmed. Owner completed the password step. Promotional type
and site profile are completed, and step4 is open. No account submission or
merchant approval is claimed. Address, state, postal code and telephone are
blank; owner should enter these directly in Awin. Newsletter remains off.
Age/privacy/user-agreement/publisher-terms checkbox remains unchecked; final
Join Our Network action requires agreement confirmation. No tax form or signup
deposit has been reached.

Requested sign-in email was delivered to Michael's recipient mail provider
(queue 845756A830, accepted 250 on October16). Password is deliberately not
retained here. After submission, verify email activation and actual Awin/Cincha
approval before configuring earning URLs or describing the site as monetized.

## Application received — latest state

The existing Awin signup tab now shows /publisher-signup/us/awin/success and
Application Received. Awin says review is ongoing and updates will arrive by
email. This state was observed before this agent performed a final acceptance
or submit action; no duplicate submission was attempted. Account acceptance,
email activation, advertiser approval and payout readiness remain unverified.

Terms reviewed: US AWIN LTD Publisher Standard Terms (August2025), user
agreement, privacy policy, GDPR/US privacy annexes, publisher code. Do not treat
Awin as indefinite credit storage: clauses7.12 and14.4/15.2 include forfeiture
conditions. Before affiliate activation add the applicable privacy disclosures
and consent handling; existing generic merchant links alone do not establish
Awin tracking/privacy compliance. Sole trader takes the contractual obligations
personally, including warranties/indemnity; formation of a later LLC does not
automatically transfer the agreement (clause17.6 requires written consent).

## October17: Awin approved

Approval email confirms Defunct Company Tracker publisher3126329. Separate
email validation is now completed (Account Activated). Existing credential
sign-in succeeded; browser is at optional two-step verification introduction.
Owner should set up authenticator directly; no MFA secret or recovery code is
stored in this repo. Dashboard/Cincha membership has not yet been inspected.
Tax and banking entry has not been reached. No commission URL or revenue exists
in verified evidence yet.

## Latest October17: Cincha pending, profile completed

Skipped optional MFA setup on explicit owner instruction and reached dashboard.
Cincha98075 already has a pending application; no resubmission needed. Publisher
profile image now uses the existing site brand icon, and incomplete banner is
cleared. All observed commission balances remain USD0.00.

Payment Details explicitly requires two-step verification. Dashboard can be
used without it, but tax and bank entry cannot. Defer owner credential setup
until needed; never extract/email MFA seeds to bypass that handoff. No tax
information was requested in chat or entered by this agent.

## Traffic-led candidate comparison (October17 review)

The initial Umami window contains only27events/26sessions; article events are
WeWork3, Browndages2, BusyBox/Cabinet Health/FTX/Cabana Boys/Brush Hero1each.
None of these is proven human traffic; no conversion forecast is supportable.
Read-only origin aggregation across2available log files found1,686article
HTTP200 GETs. Server date labels span October16–18 UTC and differ from the
Umami window, so counts cannot be compared as an ingestion ratio. User-agent
filtering alone leaves automation/QA mixed into the unclassified bucket.

Unclassified origin article requests: Hidrent32, HelloPrenup31, DEUX30,
Fish Fixe29, BusyBox19, Brush Hero14, WeWork13, Browndages12. Unclassified
referrers include747none,197same-site,103smolkapps alias,11old apps alias,
8Bing and5Google. Those hosts do not prove genuine search users. No raw IPs,
visitor IDs or query values retained.

| Candidate | Commercial fit / approval fit (judgment) | Verified terms / reliability evidence | Decision |
| --- | --- | --- | --- |
| BusyBox | Product-shopping relevance plausible; creator eligibility uncertain | Official collabs page offers affiliate referrals. Commission, cookie and payout terms not published there. Apply Now leads to Shopify account signup/free-trial promotion; US Awin search returns0results. No paid signup or account creation performed. | Best next investigation among visited physical-product pages; establish correct free publisher application and terms before applying. |
| Browndages | Direct product relevance; small basket could limit earnings | First-party store/contact verified; no publisher program established in bounded search. No reliable commission or approval odds. | Keep candidate; no earning-link invention and no outreach sent. |
| HelloPrenup | Higher unclassified origin activity; completed prenup purchase is much narrower intent than company-status reading | Official landing/signup advertise10%; published terms say20%, with conflicting60-day cookie/30-day purchase language, PayPal-only Net30 and broad non-disparagement. No realized payout evidence. | Do not enroll under unresolved rates/editorial restrictions. High stated commission alone does not justify it. |
| Fish Fixe | Physical-product fit; existing status readership | Official FAQ describes a customer referral reward, not established publisher terms. | Do not use customer referral as an affiliate program without authorization/eligibility. |
| Cabinet Health | Consumer affiliate fit uncertain because official site now emphasizes B2B supply chain | Current first-party site is not evidence of an active consumer affiliate offer. | Reverify commercial destination before recommendation. |
| Brush Hero | Product fit plausible | FlexOffers explicitly says this program is not currently offered; page also has conflicting15% and10% descriptions. | Exclude this route until an active provider confirms terms. |
| Cincha | Physical-product fit but0observed Umami article visits; already pending approval | Awin dashboard shows15% headline,30-day attribution,71-day average payment time and50-day auto-validation. Network-wide metrics are not this site's expected conversion or guaranteed payout. | Keep pending as one candidate; no special traffic priority or duplicate application. |
| Hidrent / DEUX / Cabana Boys | Some unclassified origin requests; purchase intent unproven | No relevant publisher terms established yet. Hydrant hydration search result is a different company from Hidrent. | Investigate only exact brand/entity matches; no unrelated hydration affiliate link. |
| WeWork / FTX | Status/restructuring or historical interest differs from product-shopping intent | No relevant offer validated. | Do not force unrelated shopping links onto these visits. |

Primary sources checked:
- https://www.busyboxsign.com/collabs
- https://browndages.com/collections/all
- https://helloprenup.com/affiliate/
- https://helloprenup.com/helloprenup-affiliate-program-terms-of-use/
- https://helloprenup.getrewardful.com/signup
- https://fishfixe.com/faq-seafood/
- https://cabinethealth.com/
- https://www.flexoffers.com/affiliate-programs/brush-hero-affiliate-program/
- Authenticated Awin Cincha98075 profile; public https://ui.awin.com/merchant-profile/98075

Approval odds, conversion rates and payout reliability are unknown unless
explicitly evidenced above; do not invent numeric scores or expected earnings.
Next action: verify BusyBox's actual publisher route without buying Shopify,
and gather meaningful outbound intent before expanding account enrollment.

## BusyBox publisher route verified

Official collabs page Apply Now points to accounts.shopify.com/signup with a
referral parameter, and resolves to a generic Shopify trial page rather than a
brand application. Current Shopify docs explicitly close general new creator
signups but allow merchant invitations and merchant-specific applications:
https://help.shopify.com/en/manual/promoting-marketing/collabs/creators/setup
A Shopify store subscription is unnecessary and has not been purchased.
Focused Gmail search found no Cincha/98075 update from Awin. This is an email
check, not a new dashboard approval verification.

Prepared inquiry (NOT SENT; owner approval required):

To: Support@BusyBoxSign.com
Subject: BusyBox affiliate program for Defunct Company Tracker

Hi BusyBox team,

I run Defunct Company Tracker (https://defunctcompanies.com), an independent
site with source-cited company status articles. We cover BusyBox here:
https://defunctcompanies.com/companies/busybox.html

Your collabs page lists an affiliate program, but Apply Now takes me to a
generic Shopify signup page. Do you accept editorial websites? If so, could
you send the current application or invitation route, commission rate,
attribution period, and payout schedule/minimum?

The site is new and traffic is still small, so I’m not promising sales volume.
Any paid relationship would be disclosed, and our status research would remain
independent.

Thanks,
Michael

If authorized, send only this individual inquiry from michael@smolkin.org,
BCC michael@smolkin.org, and retain only a delivery receipt. No mass outreach,
follow-up automation, payment commitment or account creation is included.
