"""Core domain models for the defunct-company tracker.

These are intentionally plain dataclasses (no pydantic) so the package stays
dependency-light and the (de)serialization is fully under our control — which
matters because the cache file is the source of truth between runs and we want
its schema to be stable and human-diffable.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class Status(str, enum.Enum):
    """The only business statuses we are willing to publish.

    Anything an LLM hands back that does not map cleanly onto one of these is
    coerced to UNKNOWN by :func:`Status.coerce` rather than trusted verbatim —
    an open enum is an invitation to hallucinated labels like "probably gone".
    """

    ACTIVE = "active"
    ACQUIRED = "acquired"
    MERGED = "merged"
    DEFUNCT = "defunct"
    BANKRUPT = "bankrupt"
    RENAMED = "renamed"
    UNKNOWN = "unknown"

    @classmethod
    def coerce(cls, raw: Any) -> "Status":
        """Best-effort map an arbitrary value onto a known status.

        Unknown / empty / unmappable values become :attr:`UNKNOWN`. We never
        raise here: a bad label from the model must degrade to "unknown", not
        crash the pipeline or — worse — get silently published.
        """
        if isinstance(raw, Status):
            return raw
        if raw is None:
            return cls.UNKNOWN
        key = str(raw).strip().lower()
        if not key:
            return cls.UNKNOWN
        # direct value match
        for member in cls:
            if member.value == key:
                return member
        # a few common synonyms the models like to emit
        synonyms = {
            "alive": cls.ACTIVE,
            "operating": cls.ACTIVE,
            "operational": cls.ACTIVE,
            "live": cls.ACTIVE,
            "running": cls.ACTIVE,
            "shut down": cls.DEFUNCT,
            "shutdown": cls.DEFUNCT,
            "closed": cls.DEFUNCT,
            "dead": cls.DEFUNCT,
            "ceased": cls.DEFUNCT,
            "dissolved": cls.DEFUNCT,
            "out of business": cls.DEFUNCT,
            "bought": cls.ACQUIRED,
            "purchased": cls.ACQUIRED,
            "acquihired": cls.ACQUIRED,
            "acqui-hired": cls.ACQUIRED,
            "insolvent": cls.BANKRUPT,
            "chapter 11": cls.BANKRUPT,
            "chapter 7": cls.BANKRUPT,
            "rebranded": cls.RENAMED,
        }
        return synonyms.get(key, cls.UNKNOWN)

    @property
    def is_alive(self) -> bool:
        return self is Status.ACTIVE

    @property
    def is_terminal(self) -> bool:
        """A status that means the original entity no longer trades as such."""
        return self in {
            Status.DEFUNCT,
            Status.BANKRUPT,
            Status.ACQUIRED,
            Status.MERGED,
            Status.RENAMED,
        }


@dataclass(frozen=True)
class Company:
    """An input company to research."""

    name: str
    aliases: tuple[str, ...] = ()
    # optional hints that improve disambiguation but are never required
    domain: str | None = None
    founded: int | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Company.name must be a non-empty string")

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Company":
        if isinstance(d, str):  # allow a bare string in the input list
            return cls(name=d)
        aliases = d.get("aliases") or ()
        if isinstance(aliases, list):
            aliases = tuple(aliases)
        return cls(
            name=d["name"],
            aliases=tuple(aliases),
            domain=d.get("domain"),
            founded=d.get("founded"),
            notes=d.get("notes"),
        )


@dataclass(frozen=True)
class Citation:
    """A single supporting source for a status claim."""

    title: str
    url: str
    # free-text snippet the model says supports the claim
    snippet: str | None = None
    published: str | None = None

    def __post_init__(self) -> None:
        if not self.url or not str(self.url).strip():
            raise ValueError("Citation.url must be non-empty")

    @property
    def is_well_formed(self) -> bool:
        return is_http_url(self.url)

    @property
    def domain(self) -> str:
        return url_domain(self.url)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Citation":
        return cls(
            title=d.get("title") or d.get("url", ""),
            url=d["url"],
            snippet=d.get("snippet"),
            published=d.get("published"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "published": self.published,
        }


@dataclass
class StatusReport:
    """The researched result for one company, as produced by a provider and
    then graded by the verifier."""

    company: Company
    status: Status
    summary: str
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.0  # provider-reported, 0..1
    as_of: str = ""  # year/date the status is believed accurate as of
    successor: str | None = None  # e.g. acquirer / renamed-to entity
    raw_status: str | None = None  # what the provider literally returned

    # --- verification outputs (filled by verify.py) ---
    verified: bool = False
    verification_score: float = 0.0  # 0..1
    flags: list[str] = field(default_factory=list)
    retrieved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    @property
    def publishable(self) -> bool:
        """Whether this report is allowed onto the public site as fact."""
        return self.verified and self.status is not Status.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d["status"] = self.status.value
        d["company"] = {
            "name": self.company.name,
            "aliases": list(self.company.aliases),
            "domain": self.company.domain,
            "founded": self.company.founded,
            "notes": self.company.notes,
        }
        d["citations"] = [c.to_dict() for c in self.citations]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StatusReport":
        company = Company.from_dict(d["company"])
        citations = [Citation.from_dict(c) for c in d.get("citations", [])]
        return cls(
            company=company,
            status=Status.coerce(d.get("status")),
            summary=d.get("summary", ""),
            citations=citations,
            confidence=float(d.get("confidence", 0.0)),
            as_of=d.get("as_of", ""),
            successor=d.get("successor"),
            raw_status=d.get("raw_status"),
            verified=bool(d.get("verified", False)),
            verification_score=float(d.get("verification_score", 0.0)),
            flags=list(d.get("flags", [])),
            retrieved_at=d.get("retrieved_at", ""),
        )


# --------------------------------------------------------------------------- #
# small pure helpers (kept here so models has no internal imports)
# --------------------------------------------------------------------------- #

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", text.strip().lower()).strip("-")
    return s or "company"


_URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


def is_http_url(url: str) -> bool:
    return bool(_URL_RE.match(url.strip())) if url else False


def url_domain(url: str) -> str:
    if not url:
        return ""
    m = re.match(r"^https?://([^/]+)", url.strip(), re.IGNORECASE)
    host = m.group(1) if m else url
    return host.lower().lstrip("www.") if host.startswith("www.") else host.lower()


def content_hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:16]
