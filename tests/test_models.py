import pytest

from dct.models import (
    Citation,
    Company,
    Status,
    StatusReport,
    content_hash,
    is_http_url,
    slugify,
    url_domain,
)


class TestStatusCoerce:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("active", Status.ACTIVE),
            ("ACTIVE", Status.ACTIVE),
            ("  Defunct ", Status.DEFUNCT),
            ("acquired", Status.ACQUIRED),
            ("shut down", Status.DEFUNCT),
            ("out of business", Status.DEFUNCT),
            ("bought", Status.ACQUIRED),
            ("acqui-hired", Status.ACQUIRED),
            ("chapter 11", Status.BANKRUPT),
            ("rebranded", Status.RENAMED),
            ("cancelled", Status.CANCELED),
            ("dissolved and recreated", Status.DISSOLVED_RECREATED),
            ("operating", Status.ACTIVE),
            (Status.MERGED, Status.MERGED),
        ],
    )
    def test_known_and_synonyms(self, raw, expected):
        assert Status.coerce(raw) is expected

    @pytest.mark.parametrize("raw", [None, "", "   ", "probably gone", "who knows", 42])
    def test_unmappable_becomes_unknown(self, raw):
        assert Status.coerce(raw) is Status.UNKNOWN

    def test_terminal_and_alive_flags(self):
        assert Status.ACTIVE.is_alive
        assert not Status.DEFUNCT.is_alive
        for s in (
            Status.DEFUNCT,
            Status.BANKRUPT,
            Status.ACQUIRED,
            Status.MERGED,
            Status.RENAMED,
            Status.CANCELED,
            Status.DISSOLVED_RECREATED,
        ):
            assert s.is_terminal
        assert not Status.ACTIVE.is_terminal
        assert not Status.UNKNOWN.is_terminal


class TestCompany:
    def test_slug(self):
        assert Company(name="Pets.com").slug == "pets-com"
        assert Company(name="Sun Microsystems, Inc.").slug == "sun-microsystems-inc"

    def test_empty_name_rejected(self):
        with pytest.raises(ValueError):
            Company(name="  ")

    def test_from_dict_variants(self):
        assert Company.from_dict("Acme").name == "Acme"
        c = Company.from_dict({"name": "Beta", "aliases": ["B", "Be"], "founded": 1999})
        assert c.aliases == ("B", "Be")
        assert c.founded == 1999


class TestCitation:
    def test_wellformed(self):
        c = Citation(title="t", url="https://example.com/x")
        assert c.is_well_formed
        assert c.domain == "example.com"

    def test_url_required(self):
        with pytest.raises(ValueError):
            Citation(title="t", url="")

    def test_malformed_url(self):
        assert not Citation(title="t", url="not a url").is_well_formed
        assert not Citation(title="t", url="ftp://x.com").is_well_formed


class TestHelpers:
    def test_slugify_edge(self):
        assert slugify("   ") == "company"
        assert slugify("!!!") == "company"

    def test_is_http_url(self):
        assert is_http_url("https://a.com")
        assert is_http_url("http://a.com/path?q=1")
        assert not is_http_url("javascript:alert(1)")
        assert not is_http_url("")

    def test_url_domain_strips_www(self):
        assert url_domain("https://www.example.com/p") == "example.com"
        assert url_domain("https://sub.example.com") == "sub.example.com"

    def test_content_hash_stable_and_short(self):
        h1 = content_hash("a", "b")
        h2 = content_hash("a", "b")
        h3 = content_hash("b", "a")
        assert h1 == h2 != h3
        assert len(h1) == 16


class TestStatusReportRoundTrip:
    def _report(self):
        return StatusReport(
            company=Company(name="Pets.com", aliases=("Pets",)),
            status=Status.DEFUNCT,
            summary="liquidated 2000",
            citations=[
                Citation(title="W", url="https://en.wikipedia.org/wiki/Pets.com")
            ],
            confidence=0.9,
            as_of="2000",
        )

    def test_to_from_dict(self):
        r = self._report()
        d = r.to_dict()
        assert d["status"] == "defunct"
        assert d["company"]["name"] == "Pets.com"
        r2 = StatusReport.from_dict(d)
        assert r2.status is Status.DEFUNCT
        assert r2.company.aliases == ("Pets",)
        assert r2.citations[0].url == "https://en.wikipedia.org/wiki/Pets.com"

    def test_publishable_requires_verified(self):
        r = self._report()
        assert not r.publishable  # not verified yet
        r.verified = True
        assert r.publishable
        r.status = Status.UNKNOWN
        assert not r.publishable  # unknown never publishable even if verified
