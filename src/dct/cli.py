"""Command-line interface for the defunct-company tracker.

    dct build  COMPANIES.json [--out site] [--cache .cache.json] [--no-cache]
               [--site-url URL] [--force] [--fixture FIXTURE.json]
    dct research COMPANIES.json [--out reports.json] [...]
    dct demo   [--out site]          # build the bundled sample, no API key
    dct status                       # show whether a live provider is available

`build` runs the full pipeline and emits a static site. `research` runs the
pipeline and dumps the verified reports as JSON (no HTML). `demo` uses the
bundled sample data + fixtures so the whole thing runs with zero credentials.

The provider is chosen automatically: live LLM when ``DCT_LLM_API_KEY`` is set,
otherwise the offline mock (seeded by ``--fixture`` if given, else empty so all
statuses come back unverified/UNKNOWN — which is the honest result with no data).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from . import __version__
from .cache import ReportCache
from .pipeline import load_companies, run_pipeline
from .providers import AnthropicProvider, MockProvider, default_provider
from .site import SiteGenerator

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
# sample data is bundled inside the package so `dct demo` works when installed
SAMPLE_COMPANIES = os.path.join(_PKG_DIR, "data", "sample_companies.json")
SAMPLE_FIXTURE = os.path.join(_PKG_DIR, "data", "sample_fixture.json")


def _load_fixture(path: str | None) -> dict[str, dict[str, Any]] | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _make_provider(args) -> Any:
    """Honour an explicit --fixture by forcing the mock provider; else auto."""
    fixture = _load_fixture(getattr(args, "fixture", None))
    if getattr(args, "mock", False) or (
        fixture is not None and not AnthropicProvider.available()
    ):
        return MockProvider(fixture)
    return default_provider(fixture)


def cmd_build(args) -> int:
    companies = load_companies(args.companies)
    provider = _make_provider(args)
    cache = None if args.no_cache else ReportCache(args.cache, ttl_days=args.ttl)
    result = run_pipeline(companies, provider, cache=cache, force_refresh=args.force)
    gen = SiteGenerator(
        site_name=args.site_name,
        site_url=args.site_url or "",
    )
    stats = gen.build(result, args.out)
    print(f"provider: {provider.name}")
    print(json.dumps({**result.summary(), **stats}, indent=2))
    print(f"site written to: {os.path.abspath(args.out)}")
    return 0


def cmd_research(args) -> int:
    companies = load_companies(args.companies)
    provider = _make_provider(args)
    cache = None if args.no_cache else ReportCache(args.cache, ttl_days=args.ttl)
    result = run_pipeline(companies, provider, cache=cache, force_refresh=args.force)
    payload = {
        "summary": result.summary(),
        "reports": [r.to_dict() for r in result.reports],
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {len(result.reports)} reports to {args.out}")
    else:
        print(text)
    return 0


def cmd_demo(args) -> int:
    args.companies = SAMPLE_COMPANIES
    args.fixture = SAMPLE_FIXTURE
    args.mock = True
    args.no_cache = True
    args.cache = ".dct-cache.json"
    args.ttl = 90.0
    args.force = True
    args.site_url = args.site_url or ""
    args.site_name = args.site_name or "Defunct Company Tracker (demo)"
    return cmd_build(args)


def cmd_status(args) -> int:
    available = AnthropicProvider.available()
    print(
        json.dumps(
            {
                "version": __version__,
                "live_provider_available": available,
                "api_key_env": AnthropicProvider.API_KEY_ENV,
                "active_provider": "anthropic" if available else "mock",
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dct", description=__doc__.splitlines()[0])
    p.add_argument("--version", action="version", version=f"dct {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp):
        sp.add_argument("--cache", default=".dct-cache.json", help="cache file path")
        sp.add_argument("--no-cache", action="store_true", help="disable caching")
        sp.add_argument("--ttl", type=float, default=90.0, help="cache TTL in days")
        sp.add_argument(
            "--force", action="store_true", help="ignore cache, re-research"
        )
        sp.add_argument("--fixture", help="mock provider fixture JSON (forces mock)")
        sp.add_argument(
            "--mock", action="store_true", help="force the offline mock provider"
        )
        sp.add_argument(
            "--site-url", default="", help="absolute site URL for sitemap/JSON-LD"
        )
        sp.add_argument("--site-name", default="Defunct Company Tracker")

    b = sub.add_parser("build", help="research companies and generate the static site")
    b.add_argument("companies", help="path to companies JSON")
    b.add_argument("--out", default="site", help="output directory")
    add_common(b)
    b.set_defaults(func=cmd_build)

    r = sub.add_parser(
        "research", help="research companies and dump verified reports JSON"
    )
    r.add_argument("companies", help="path to companies JSON")
    r.add_argument("--out", help="write reports JSON here (default: stdout)")
    add_common(r)
    r.set_defaults(func=cmd_research)

    d = sub.add_parser("demo", help="build the bundled sample site with no API key")
    d.add_argument("--out", default="site", help="output directory")
    d.add_argument("--site-url", default="")
    d.add_argument("--site-name", default="")
    d.set_defaults(func=cmd_demo)

    s = sub.add_parser("status", help="show whether a live LLM provider is configured")
    s.set_defaults(func=cmd_status)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"error: file not found: {e.filename}", file=sys.stderr)
        return 2
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
