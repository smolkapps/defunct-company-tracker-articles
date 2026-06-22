"""Research pipeline: companies -> verified, cached status reports.

Ties the pieces together:

    load companies
        -> for each: cache hit? else provider.research(...)
        -> verify_report(...)
        -> store in cache
    -> return reports

The pipeline is deliberately provider-agnostic and cache-agnostic (both injected)
so tests can drive it with a MockProvider + a temp cache and assert behaviour end
to end without any network.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .cache import ReportCache
from .models import Company, StatusReport
from .providers import Provider
from .verify import VerifyConfig, verify_report


@dataclass
class PipelineResult:
    reports: list[StatusReport] = field(default_factory=list)
    n_cached: int = 0
    n_researched: int = 0

    @property
    def publishable(self) -> list[StatusReport]:
        return [r for r in self.reports if r.publishable]

    @property
    def unpublishable(self) -> list[StatusReport]:
        return [r for r in self.reports if not r.publishable]

    def summary(self) -> dict[str, int]:
        from collections import Counter

        by_status = Counter(r.status.value for r in self.reports)
        return {
            "total": len(self.reports),
            "publishable": len(self.publishable),
            "unpublishable": len(self.unpublishable),
            "cached": self.n_cached,
            "researched": self.n_researched,
            **{f"status_{k}": v for k, v in sorted(by_status.items())},
        }


def load_companies(path: str) -> list[Company]:
    """Load companies from a JSON file.

    Accepts either a bare list (``["Acme", {"name": "Beta"}]``) or an object
    with a ``companies`` key. Strings and dicts are both allowed per item.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return parse_companies(data)


def parse_companies(data: Any) -> list[Company]:
    if isinstance(data, dict):
        data = data.get("companies", [])
    if not isinstance(data, list):
        raise ValueError("company input must be a list or an object with 'companies'")
    out: list[Company] = []
    seen: set[str] = set()
    for item in data:
        company = Company.from_dict(item)
        if company.slug in seen:  # dedupe by slug, keep first
            continue
        seen.add(company.slug)
        out.append(company)
    return out


def run_pipeline(
    companies: list[Company],
    provider: Provider,
    cache: ReportCache | None = None,
    verify_config: VerifyConfig | None = None,
    *,
    force_refresh: bool = False,
) -> PipelineResult:
    result = PipelineResult()
    for company in companies:
        report: StatusReport | None = None
        if cache is not None and not force_refresh:
            report = cache.get(company, provider.name)
            if report is not None:
                result.n_cached += 1
        if report is None:
            report = provider.research(company)
            verify_report(report, verify_config)
            result.n_researched += 1
            if cache is not None:
                cache.put(report, provider.name)
        result.reports.append(report)

    if cache is not None and result.n_researched > 0:
        cache.save()

    # stable ordering: publishable terminal companies first (the interesting
    # ones for a "defunct tracker"), then by name
    result.reports.sort(
        key=lambda r: (
            not r.publishable,
            not r.status.is_terminal,
            r.company.name.lower(),
        )
    )
    return result
