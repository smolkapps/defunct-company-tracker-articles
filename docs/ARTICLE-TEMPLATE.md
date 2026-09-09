# Shark Tank company research article

Use one record and one article per deduplicated company. Keep every episode
appearance attached to the company even when the company has an alias,
successor, parent, or later rebrand.

## 1. Verdict

### Is **[company]** still in business?

**Status:** `[operating | renamed | acquired | merged | closed | canceled | bankrupt | dissolved | dissolved_recreated | unresolved]`  
**As of:** `[YYYY-MM-DD]`  
**Confidence:** `[high | medium | low]`

One sentence answering the question. Say what is verified, and identify the
successor or acquirer when the original entity no longer operates under its
original identity.

## 2. Shark Tank appearance

- **Episode/season:** `[season and episode, or unresolved]`
- **Official video:** `[title and URL]`
- **Episode guide:** `[ABC or other authoritative URL]`
- **Pitch/product:** `[what was pitched]`
- **Ask:** `[amount and equity, if verified]`
- **Offer(s):** `[Shark, amount, equity/terms]`
- **Did the deal close?** `[yes | no | unresolved]`, with a source for the
  post-show outcome. A televised handshake is not proof that the deal closed.

List all other official videos or episodes in which the company appears. Mark
clips, reruns, compilations, and duplicates instead of counting them as new
episodes.

## 3. Dated timeline

| Date | Event | Evidence |
| --- | --- | --- |
| `[YYYY-MM-DD]` | `[founding, pitch, funding, acquisition, lawsuit, closure, etc.]` | `[source IDs]` |

## 4. Legal and entity identity

Record the legal entity behind the brand, not just the website or trade name.

- **Entity name(s):** `[legal names and aliases]`
- **Jurisdiction(s):** `[state/country]`
- **State registry:** `[Secretary of State URL, entity number, status, and search/access date]`
- **Registry events:** `[formation, good standing, dissolution, withdrawal, merger, name change, reinstatement, registered-agent changes]`
- **Federal records checked:** `[SEC EDGAR, FTC, PACER/authoritative docket, USPTO, bankruptcy, or not applicable]`
- **Successor/acquirer/parent:** `[entity and evidence, or unresolved]`

If a registry is interactive, paywalled, CAPTCHA-protected, unavailable, or
does not expose historical records, state that exact limitation and
triangulate. Never turn “no result found” into “the company is dissolved.”

## 5. Current status evidence

Explain why the status is the published classification. Use at least one
primary or official source where available and corroborate terminal claims
with an independent source. A dead website alone is not closure evidence.

## 6. Notable developments and disputes

Include the sourced story: changed deals, buyouts, equity disputes, lawsuits,
canceled products, deceptive-marketing findings, bankruptcy or creditor
issues, founders leaving, or dissolution/recreation. Label every item:

- **Verified fact:** supported directly by a primary record or official
  statement.
- **Strong corroboration:** supported by multiple independent reliable
  sources.
- **Credible report:** reported by a reputable source but not independently
  confirmed here.
- **Allegation:** attribute it, identify the response if available, and never
  state it as an established fact.
- **Unresolved:** plausible but not verified; keep it out of the verdict.

## 7. What we could not verify

List missing episode numbers, inaccessible registries, unconfirmed deal terms,
unclear successor relationships, and conflicting reports. Include the search
trail and the next action in the queue.

## 8. Sources

Every material claim gets a source ID. For each source record its title, URL,
source type, publication/access date, and the claim(s) it supports. Prefer,
in order: state/federal records; official company, acquirer, or investor
announcements; ABC/Shark Tank and official video sources; then reputable
reporting and clearly labeled secondary sources.

Use the machine-readable shape in
`src/dct/data/research-record.schema.json` for imports and validation.
