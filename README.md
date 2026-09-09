# Defunct Company Tracker

Generate a **source-cited, fact-verified static website** that tracks whether
companies are **active, acquired, or defunct**. Each status is researched by an
internet-capable LLM, then run through a verification layer that **refuses to
publish unsourced or fabricated claims**.

> "Is it still in business?" — answered with citations, or not answered at all.

## Why the verification layer matters

An internet-capable model will happily declare a company "defunct" with total
confidence and zero (or hallucinated) sources. Publishing that as fact is the
whole failure mode this project exists to avoid. So every researched result is
graded before it can reach the site:

- A non-`unknown` status is **only published when backed by at least one
  well-formed source URL**. No source → withheld.
- Malformed / fabricated source URLs are **discarded before grading** — a
  "source: trust me" string counts for nothing.
- **Terminal claims** (defunct / bankrupt / acquired) are held to a higher bar,
  because wrongly declaring a living company dead is the most damaging error.
- Acquisition / merger / rename claims must **name the successor entity**.
- The model's self-reported confidence is an input, **never** the sole basis.

Companies that fail verification are not hidden silently — they're listed (with
the reason) in a collapsed section on the index, and simply don't get an
article page presenting them as fact. See `methodology.html` on the built site.

## Install

```bash
pip install -e .            # core (offline mock + site generator)
pip install -e ".[llm]"     # + real Anthropic provider
pip install -e ".[test]"    # + pytest
```

## Quick start (no API key needed)

```bash
dct demo --out site         # builds a real site from bundled sample data
open site/index.html
```

The demo uses a bundled fixture of well-known companies (Pets.com, Blockbuster,
Lehman Brothers, Instagram, Sun Microsystems, …). Unknown or unverifiable
companies are withheld from publication; that behavior is covered by the test
fixture rather than by a fake production entry.

The tracker’s origin is the Shark Tank Fish Fixe clip
(`https://www.youtube.com/watch?v=AoZdeYKGuR4`). That video is the starting
anchor, not the whole corpus: the intended expansion covers every company in
the defined official Shark Tank video/episode collection. Fish Fixe, Hello
Prenup, DEUX, and Hidrent/Helpful Heroes are retained as the first verified
records while the episode manifest and deduplicated company ledger expand.

The reusable research contract is in
[`docs/ARTICLE-TEMPLATE.md`](docs/ARTICLE-TEMPLATE.md), with the machine-readable
record shape in
[`src/dct/data/research-record.schema.json`](src/dct/data/research-record.schema.json).

## Real research

Set an API key and point it at your own list of companies:

```bash
export DCT_LLM_API_KEY=sk-...           # enables the live LLM provider
dct build companies.json --out site --site-url https://your.site
```

`companies.json` is either a bare list or an object with a `companies` key:

```json
{
  "companies": [
    "Pets.com",
    { "name": "Sun Microsystems", "aliases": ["Sun"], "founded": 1982 }
  ]
}
```

Without `DCT_LLM_API_KEY` set, the tool transparently falls back to the offline
**mock provider**, so it always runs — it just returns `unknown` (and therefore
withholds) for anything it has no fixture data for. That is the honest result
when there's no data, by design.

## Commands

| Command | Purpose |
| --- | --- |
| `dct build COMPANIES.json` | research + generate the static site |
| `dct research COMPANIES.json` | research + dump verified reports as JSON |
| `dct demo` | build the bundled sample site with **no API key** |
| `dct status` | show whether a live LLM provider is configured |

Useful flags: `--out DIR`, `--cache FILE` / `--no-cache`, `--ttl DAYS`,
`--force` (ignore cache), `--fixture FILE` (drive the mock provider),
`--site-url URL`, `--site-name NAME`.

## Caching

Results are cached to a local JSON file (`--cache`, default `.dct-cache.json`)
with a TTL (default 90 days), since corporate status changes over months, not
seconds. The cache key includes the provider name and a hash of the company's
identifying fields, so switching providers or correcting aliases naturally
re-researches. Use `--force` to bypass.

## Architecture

```
companies.json
   └─> Provider.research()        # AnthropicProvider (live) | MockProvider (offline)
         └─> verify_report()      # the gate: sources required, malformed pruned
               └─> ReportCache    # TTL'd, atomic-write JSON
                     └─> SiteGenerator  # Jinja2 -> index + per-company articles
```

- `dct.models` — `Status` enum (closed set; unknowns coerce to `UNKNOWN`),
  `Company`, `Citation`, `StatusReport`.
- `dct.providers` — provider abstraction. Network lives only in
  `AnthropicProvider._call_model`; the response **parsing** is the pure,
  unit-tested `parse_model_payload` / `extract_json`.
- `dct.verify` — deterministic, pure verification grading.
- `dct.cache` — TTL'd JSON cache with atomic writes and corruption resilience.
- `dct.pipeline` — orchestration: cache → provider → verify → cache.
- `dct.site` — static HTML/CSS/JSON-LD/sitemap generator.

## Tests

```bash
python -m pytest -q
```

Everything is tested offline with a mock provider and saved fixtures — no
network, no API key. The live provider's only non-trivial logic (parsing the
model's JSON) is tested directly against fixture payloads.

## License

MIT — see [LICENSE](LICENSE).
