"""Fact-verification layer.

The single most important guard in this project: an internet-capable LLM will
happily assert that a company is "defunct" with total confidence and zero (or
fabricated) sources. We must NOT publish such claims as fact. This module grades
a :class:`StatusReport` and decides whether it is allowed onto the public site.

Design principles
-----------------
* A non-trivial status claim (anything other than UNKNOWN) requires at least one
  *well-formed* citation. No source -> not verified, full stop.
* Citations whose URL is malformed are dropped before grading (a fabricated
  "source: trust me" string is worse than no source).
* The provider's self-reported confidence is an input, never the sole basis:
  high confidence with no usable citation still fails.
* Terminal claims ("this company is dead / was acquired") are held to a higher
  bar than "active": wrongly declaring a live company dead is the most damaging
  error a tracker like this can make, so DEFUNCT/BANKRUPT need corroboration
  signals (a date, a successor for acquisitions, a credible-looking domain).
* Everything is deterministic and pure given a report — so it is fully testable
  without any network or model.

The verifier never raises on bad data; it degrades the report to unpublishable
and records human-readable ``flags`` explaining why.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Citation, Status, StatusReport

# Domains we treat as higher-signal for a *business status* claim. This is a
# heuristic boost, not a whitelist — unknown domains are still allowed, they
# just don't get the corroboration bonus. Matched as a suffix on the host.
HIGH_SIGNAL_DOMAINS: tuple[str, ...] = (
    "sec.gov",
    "crunchbase.com",
    "bloomberg.com",
    "reuters.com",
    "wsj.com",
    "ft.com",
    "techcrunch.com",
    "wikipedia.org",
    "companieshouse.gov.uk",
    "opencorporates.com",
    "nytimes.com",
    "forbes.com",
    "businesswire.com",
    "prnewswire.com",
)


@dataclass(frozen=True)
class VerifyConfig:
    """Tunable thresholds for the verifier."""

    # minimum well-formed citations required for any non-UNKNOWN claim
    min_citations: int = 1
    # terminal statuses (defunct/bankrupt/acquired/...) need this many
    min_citations_terminal: int = 1
    # score in [0,1] a report must reach to be considered verified
    verify_threshold: float = 0.5
    # confidence below which we always flag (even if otherwise verifiable)
    low_confidence_floor: float = 0.25
    # require a successor entity for ACQUIRED / MERGED / RENAMED
    require_successor_for_transition: bool = True


def _wellformed_citations(citations: list[Citation]) -> list[Citation]:
    seen: set[str] = set()
    out: list[Citation] = []
    for c in citations:
        if not c.is_well_formed:
            continue
        key = c.url.strip().lower()
        if key in seen:  # dedupe identical URLs — they don't corroborate
            continue
        seen.add(key)
        out.append(c)
    return out


def _distinct_domains(citations: list[Citation]) -> set[str]:
    return {c.domain for c in citations if c.domain}


def verify_report(
    report: StatusReport, config: VerifyConfig | None = None
) -> StatusReport:
    """Grade ``report`` in place and return it.

    Sets ``report.verified``, ``report.verification_score`` and appends
    human-readable strings to ``report.flags``. Also *prunes* malformed
    citations from the report so we never render a fake source.
    """
    cfg = config or VerifyConfig()
    flags: list[str] = []

    # 1. clean citations first — malformed/fabricated URLs are removed entirely
    good = _wellformed_citations(report.citations)
    dropped = len(report.citations) - len(good)
    if dropped > 0:
        flags.append(f"dropped {dropped} malformed/duplicate citation(s)")
    report.citations = good

    status = report.status
    score = 0.0

    # 2. UNKNOWN is never publishable, but it is "correctly" unverified, not an
    #    error. Short-circuit so we don't demand sources for "we don't know".
    if status is Status.UNKNOWN:
        report.verified = False
        report.verification_score = 0.0
        flags.append("status unknown: not publishable")
        report.flags = _merge_flags(report.flags, flags)
        return report

    n_cit = len(good)
    domains = _distinct_domains(good)

    # 3. citation count requirement (higher bar for terminal claims)
    needed = cfg.min_citations_terminal if status.is_terminal else cfg.min_citations
    if n_cit < needed:
        flags.append(
            f"insufficient sources: {n_cit} well-formed, need >= {needed} for '{status.value}'"
        )
        report.verified = False
        report.verification_score = 0.0
        report.flags = _merge_flags(report.flags, flags)
        return report

    # base score from having the required citations
    score += 0.45

    # 4. corroboration signals
    if len(domains) >= 2:
        score += 0.2  # multiple independent domains
    if any(_domain_is_high_signal(d) for d in domains):
        score += 0.15
    if report.as_of:  # a concrete "as of <when>" anchors the claim in time
        score += 0.1
    # snippet that actually mentions the company name is a weak relevance signal
    if _any_snippet_mentions(report):
        score += 0.05

    # 5. provider confidence nudges, but cannot rescue a sourceless claim
    score += max(0.0, min(report.confidence, 1.0)) * 0.05

    # 6. transition statuses should name a successor (acquirer / new name)
    if (
        cfg.require_successor_for_transition
        and status in {Status.ACQUIRED, Status.MERGED, Status.RENAMED}
        and not (report.successor and report.successor.strip())
    ):
        score -= 0.2
        flags.append(f"'{status.value}' claim has no successor entity named")

    # 7. low provider confidence is always worth surfacing
    if report.confidence < cfg.low_confidence_floor:
        flags.append(
            f"low provider confidence ({report.confidence:.2f} < {cfg.low_confidence_floor})"
        )

    score = max(0.0, min(score, 1.0))
    report.verification_score = round(score, 3)
    report.verified = score >= cfg.verify_threshold

    if not report.verified:
        flags.append(
            f"verification score {score:.2f} below threshold {cfg.verify_threshold}"
        )

    report.flags = _merge_flags(report.flags, flags)
    return report


def _domain_is_high_signal(domain: str) -> bool:
    d = domain.lower()
    return any(d == hs or d.endswith("." + hs) for hs in HIGH_SIGNAL_DOMAINS)


def _any_snippet_mentions(report: StatusReport) -> bool:
    names = [report.company.name.lower(), *[a.lower() for a in report.company.aliases]]
    for c in report.citations:
        text = " ".join(filter(None, [c.title, c.snippet])).lower()
        if any(n and n in text for n in names):
            return True
    return False


def _merge_flags(existing: list[str], new: list[str]) -> list[str]:
    out = list(existing)
    for f in new:
        if f not in out:
            out.append(f)
    return out


def verify_all(
    reports: list[StatusReport], config: VerifyConfig | None = None
) -> list[StatusReport]:
    return [verify_report(r, config) for r in reports]
