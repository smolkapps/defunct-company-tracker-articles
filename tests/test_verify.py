"""Tests for the fact-verification layer — the project's most important guard."""

from dct.models import Citation, Company, Status, StatusReport
from dct.verify import VerifyConfig, verify_report, verify_all


def _report(
    status, citations, *, confidence=0.9, as_of="2010", successor=None, name="Acme Corp"
):
    return StatusReport(
        company=Company(name=name),
        status=status,
        summary=f"{name} is {status.value}.",
        citations=list(citations),
        confidence=confidence,
        as_of=as_of,
        successor=successor,
    )


WIKI = Citation(
    title="Acme Corp - Wikipedia",
    url="https://en.wikipedia.org/wiki/Acme",
    snippet="Acme Corp was dissolved.",
)
NEWS = Citation(
    title="Acme shuts down",
    url="https://www.reuters.com/x",
    snippet="Acme Corp ceased operations.",
)


class TestHappyPath:
    def test_defunct_with_two_credible_sources_verifies(self):
        r = _report(Status.DEFUNCT, [WIKI, NEWS])
        verify_report(r)
        assert r.verified
        assert r.publishable
        assert r.verification_score >= 0.5

    def test_active_with_one_source_verifies(self):
        r = _report(Status.ACTIVE, [WIKI], as_of="2024")
        verify_report(r)
        assert r.verified


class TestSourcelessRejection:
    def test_confident_defunct_with_no_sources_is_rejected(self):
        # the headline case: model is 99% sure but cites nothing -> NOT published
        r = _report(Status.DEFUNCT, [], confidence=0.99)
        verify_report(r)
        assert not r.verified
        assert not r.publishable
        assert any("insufficient sources" in f for f in r.flags)

    def test_active_with_no_sources_rejected(self):
        r = _report(Status.ACTIVE, [], confidence=0.99)
        verify_report(r)
        assert not r.verified


class TestMalformedCitations:
    def test_fabricated_url_is_dropped_and_claim_fails(self):
        fake = Citation(title="source: trust me", url="trust-me")
        r = _report(Status.DEFUNCT, [fake], confidence=0.95)
        verify_report(r)
        # the malformed citation is pruned, leaving zero -> unverified
        assert r.citations == []
        assert not r.verified
        assert any("malformed" in f for f in r.flags)

    def test_duplicate_urls_do_not_corroborate(self):
        dup = Citation(title="A", url="https://en.wikipedia.org/wiki/Acme")
        dup2 = Citation(title="B", url="https://en.wikipedia.org/wiki/Acme")
        r = _report(Status.DEFUNCT, [dup, dup2])
        verify_report(r)
        assert len(r.citations) == 1  # deduped


class TestUnknownStatus:
    def test_unknown_is_unverified_but_not_flagged_as_error(self):
        r = _report(Status.UNKNOWN, [], confidence=0.0, as_of="")
        verify_report(r)
        assert not r.verified
        assert not r.publishable
        assert any("unknown" in f.lower() for f in r.flags)
        # should NOT demand sources for an honest "we don't know"
        assert not any("insufficient sources" in f for f in r.flags)


class TestTransitionSuccessor:
    def test_acquired_without_successor_is_penalized(self):
        r = _report(Status.ACQUIRED, [WIKI, NEWS], successor=None)
        verify_report(r)
        assert any("successor" in f for f in r.flags)

    def test_acquired_with_successor_scores_higher(self):
        without = _report(Status.ACQUIRED, [WIKI, NEWS], successor=None)
        verify_report(without)
        with_succ = _report(Status.ACQUIRED, [WIKI, NEWS], successor="Oracle")
        verify_report(with_succ)
        assert with_succ.verification_score > without.verification_score


class TestConfidenceFloor:
    def test_low_confidence_is_flagged(self):
        r = _report(Status.DEFUNCT, [WIKI, NEWS], confidence=0.1)
        verify_report(r)
        assert any("low provider confidence" in f for f in r.flags)


class TestThreshold:
    def test_threshold_can_be_tightened(self):
        r = _report(
            Status.DEFUNCT, [WIKI]
        )  # single source, no extra signals beyond as_of
        verify_report(r, VerifyConfig(verify_threshold=0.99))
        assert not r.verified

    def test_terminal_requires_more_when_configured(self):
        cfg = VerifyConfig(min_citations_terminal=2)
        one = _report(Status.DEFUNCT, [WIKI])
        verify_report(one, cfg)
        assert not one.verified  # only 1 source, terminal needs 2
        two = _report(Status.DEFUNCT, [WIKI, NEWS])
        verify_report(two, cfg)
        assert two.verified


class TestScoringSignals:
    def test_multiple_domains_and_high_signal_boost(self):
        single = _report(Status.DEFUNCT, [WIKI], as_of="")
        verify_report(single)
        multi = _report(Status.DEFUNCT, [WIKI, NEWS], as_of="2010")
        verify_report(multi)
        assert multi.verification_score > single.verification_score


def test_verify_all_grades_each():
    reports = [
        _report(Status.DEFUNCT, [WIKI, NEWS]),
        _report(Status.DEFUNCT, []),
    ]
    out = verify_all(reports)
    assert out[0].verified
    assert not out[1].verified
