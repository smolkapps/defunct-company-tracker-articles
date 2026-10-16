"""Derive status payloads directly from reviewed research records.

The reviewed Shark Tank research records (``research_batch*.json``) are the
human-reviewed source of truth. Historically each record also had to be
hand-copied into ``sample_fixture.json`` before its status could be published.
This module removes that hand-sync step: it converts each record into the same
payload shape the providers emit, so the result still goes through
:func:`dct.verify.verify_report` unchanged. The verification gate is not
bypassed or weakened; records only replace the hand-maintained fixture as the
*input*.

Conservative mapping rules (anything doubtful is withheld, never promoted):

* ``unresolved`` -> ``unknown`` (always withheld).
* A non-unresolved status must be backed by at least one claim whose
  evidence level is ``verified_fact``, ``strong_corroboration`` or
  ``credible_report`` *and* which cites at least one source that exists in the
  record; otherwise the status is downgraded to ``unknown``.
* Status citations are only the sources referenced by those backing claims,
  so the page's "Status-Verification Sources" are the ones the reviewer tied to
  the status, not every link in the dossier.
"""

from __future__ import annotations

import glob
import json
from typing import Any, Iterable

from .models import Company

#: research-record status -> provider/site status vocabulary
RECORD_STATUS_MAP: dict[str, str] = {
    "operating": "active",
    "renamed": "renamed",
    "acquired": "acquired",
    "merged": "merged",
    "closed": "defunct",
    "dissolved": "defunct",
    "canceled": "canceled",
    "bankrupt": "bankrupt",
    "dissolved_recreated": "dissolved_recreated",
    "unresolved": "unknown",
}

#: evidence levels strong enough to back a published status
BACKING_LEVELS: tuple[str, ...] = (
    "verified_fact",
    "strong_corroboration",
    "credible_report",
)

#: record confidence label -> numeric provider confidence
CONFIDENCE_MAP: dict[str, float] = {"high": 0.9, "medium": 0.7, "low": 0.4}

SHARK_TANK_TAG = "shark-tank"


def load_record_files(patterns: Iterable[str]) -> list[dict[str, Any]]:
    """Load and concatenate record lists from paths or glob patterns."""
    paths: list[str] = []
    for pattern in patterns:
        matched = sorted(glob.glob(pattern))
        if not matched:
            raise FileNotFoundError(2, "no research records match", pattern)
        paths.extend(p for p in matched if p not in paths)
    records: list[dict[str, Any]] = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if not isinstance(payload, list):
            raise ValueError(f"research record file must contain a list: {path}")
        records.extend(payload)
    return records


def _status_claims(record: dict[str, Any], source_ids: set[str]) -> list[dict]:
    """Claims strong enough to back the record's status, best first.

    A claim whose id mentions ``STATUS`` is the reviewer's explicit status
    statement and is preferred; otherwise claims are kept in record order.
    """
    backing = [
        c
        for c in record.get("claims", [])
        if c.get("evidence_level") in BACKING_LEVELS
        and any(sid in source_ids for sid in c.get("source_ids", []))
    ]
    explicit = [c for c in backing if "STATUS" in str(c.get("id", "")).upper()]
    return explicit + [c for c in backing if c not in explicit]


def record_to_payload(record: dict[str, Any]) -> dict[str, Any]:
    """Convert one reviewed research record into a provider-style payload."""
    raw = str(record.get("status", "")).strip().lower()
    status = RECORD_STATUS_MAP.get(raw, "unknown")
    sources = {s["id"]: s for s in record.get("sources", []) if s.get("id")}
    as_of = str(record.get("as_of") or "")
    confidence = CONFIDENCE_MAP.get(str(record.get("confidence", "")).lower(), 0.5)

    claims = _status_claims(record, set(sources)) if status != "unknown" else []
    if status != "unknown" and not claims:
        # a terminal or active status with no backing claim is not publishable
        status = "unknown"

    if status == "unknown":
        unresolved = next(
            (
                c["text"]
                for c in record.get("claims", [])
                if c.get("evidence_level") == "unresolved"
            ),
            "Current status is unresolved in the reviewed research record.",
        )
        return {
            "status": "unknown",
            "summary": unresolved,
            "as_of": as_of,
            "successor": None,
            "confidence": 0.0,
            "citations": [],
        }

    primary = claims[0]
    cited: list[str] = []
    # the primary status claim's sources first, then other backing claims'
    for claim in claims:
        for sid in claim.get("source_ids", []):
            if sid in sources and sid not in cited:
                cited.append(sid)
    citations = []
    for sid in cited:
        src = sources[sid]
        snippet = src.get("notes") or src.get("source_type")
        citations.append(
            {
                "title": src.get("title") or src["url"],
                "url": src["url"],
                "snippet": snippet,
                "published": src.get("published"),
            }
        )
    successor = (record.get("company") or {}).get("successor_or_acquirer")
    return {
        "status": status,
        "summary": primary["text"],
        "as_of": as_of,
        "successor": successor or None,
        "confidence": confidence,
        "citations": citations,
    }


def record_company(record: dict[str, Any]) -> Company:
    company = record["company"]
    return Company(
        name=company["name"],
        aliases=tuple(company.get("aliases") or ()),
        tags=(SHARK_TANK_TAG,),
    )


def merge_records(
    records: list[dict[str, Any]],
    legacy_companies: list[Company] | None = None,
    legacy_fixture: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[Company], dict[str, dict[str, Any]]]:
    """Combine reviewed records with optional legacy companies/fixture.

    Records always win: a legacy fixture entry for a company that also has a
    reviewed record is ignored. Legacy companies keep their hints (domain,
    founded, aliases) and gain the Shark Tank tag when a record exists for
    them. Legacy companies without a record keep their fixture payload.
    """
    legacy_companies = list(legacy_companies or [])
    fixture: dict[str, dict[str, Any]] = {
        k.strip().lower(): v for k, v in (legacy_fixture or {}).items()
    }
    by_name = {r["company"]["name"].casefold(): r for r in records}

    companies: list[Company] = []
    seen: set[str] = set()
    for c in legacy_companies:
        record = by_name.get(c.name.casefold())
        if record is not None:
            tags = tuple(dict.fromkeys((*c.tags, SHARK_TANK_TAG)))
            c = Company(
                name=c.name,
                aliases=c.aliases or tuple(record["company"].get("aliases") or ()),
                domain=c.domain,
                founded=c.founded,
                notes=c.notes,
                tags=tags,
            )
            fixture[c.name.strip().lower()] = record_to_payload(record)
        companies.append(c)
        seen.add(c.name.casefold())
    for record in records:
        name = record["company"]["name"]
        if name.casefold() in seen:
            continue
        companies.append(record_company(record))
        fixture[name.strip().lower()] = record_to_payload(record)
        seen.add(name.casefold())
    return companies, fixture
