"""On-disk cache for status reports.

Why a cache at all: each live research call costs money and latency, and a
company's corporate status changes on the order of months, not seconds. The
cache is a single JSON file mapping a stable key -> serialized StatusReport,
with a TTL so stale entries are transparently re-researched.

The key intentionally includes the provider name and a hash of the company's
identifying fields, so switching providers (mock -> live) or correcting a
company's aliases naturally misses the cache and re-researches, rather than
serving a result computed under different assumptions.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Iterator

from .models import Company, StatusReport, content_hash


def cache_key(company: Company, provider_name: str) -> str:
    return content_hash(
        provider_name,
        company.name.strip().lower(),
        "|".join(sorted(a.strip().lower() for a in company.aliases)),
        (company.domain or "").strip().lower(),
    )


def _parse_iso(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class ReportCache:
    """A tiny JSON-file cache. Not concurrent-safe; one writer at a time."""

    def __init__(self, path: str, ttl_days: float | None = 90.0) -> None:
        self.path = path
        self.ttl_days = ttl_days
        self._data: dict[str, dict] = {}
        self._loaded = False

    # --- persistence ------------------------------------------------------- #

    def load(self) -> "ReportCache":
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                if isinstance(raw, dict):
                    self._data = raw.get("entries", raw)
            except (json.JSONDecodeError, OSError):
                # a corrupt cache should never break a run; start fresh
                self._data = {}
        self._loaded = True
        return self

    def save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        payload = {
            "version": 1,
            "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "entries": self._data,
        }
        # atomic write so an interrupted run can't truncate the cache
        d = os.path.dirname(os.path.abspath(self.path)) or "."
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False, sort_keys=True)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    # --- access ------------------------------------------------------------ #

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def _is_fresh(self, entry: dict) -> bool:
        if self.ttl_days is None:
            return True
        retrieved = _parse_iso(entry.get("retrieved_at", ""))
        if retrieved is None:
            return False
        age_days = (datetime.now(timezone.utc) - retrieved).total_seconds() / 86400.0
        return age_days <= self.ttl_days

    def get(self, company: Company, provider_name: str) -> StatusReport | None:
        self._ensure_loaded()
        key = cache_key(company, provider_name)
        entry = self._data.get(key)
        if entry is None:
            return None
        if not self._is_fresh(entry):
            return None
        try:
            return StatusReport.from_dict(entry)
        except (KeyError, ValueError, TypeError):
            return None

    def put(self, report: StatusReport, provider_name: str) -> None:
        self._ensure_loaded()
        key = cache_key(report.company, provider_name)
        self._data[key] = report.to_dict()

    def __contains__(self, item: tuple[Company, str]) -> bool:
        company, provider_name = item
        return self.get(company, provider_name) is not None

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._data)

    def values(self) -> Iterator[StatusReport]:
        self._ensure_loaded()
        for entry in self._data.values():
            try:
                yield StatusReport.from_dict(entry)
            except (KeyError, ValueError, TypeError):
                continue
