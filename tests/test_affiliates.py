"""Commercial links must never turn an unverified verdict into a recommendation."""
import json

import pytest

from dct.pipeline import parse_companies, run_pipeline
from dct.providers import MockProvider
from dct.site import SiteGenerator
from tests.test_launch import FIXTURE


def test_affiliate_links_only_recommend_verified_operating_companies(tmp_path):
    result = run_pipeline(parse_companies(["Acme Gadgets", "Pets.com", "Nobody Inc"]),
                          MockProvider(FIXTURE), cache=None)
    out = tmp_path / "site"
    SiteGenerator(affiliate_links={
        "acme-gadgets": "https://merchant.example/shop?publisher=approved&campaign=dct",
        "pets-com": "https://merchant.example/closed",
        "nobody-inc": "https://merchant.example/unverified",
    }).build(result, str(out))
    html = (out / "companies/acme-gadgets.html").read_text()
    assert html.index("We may earn a commission") < html.index('rel="sponsored nofollow noopener"')
    assert 'publisher=approved&amp;campaign=dct' in html
    assert 'data-umami-event="affiliate-click"' in html
    assert 'data-umami-event-company="acme-gadgets"' in html
    assert "merchant.example" not in (out / "companies/pets-com.html").read_text()
    assert not (out / "companies/nobody-inc.html").exists()
    assert "merchant.example" not in (out / "index.html").read_text()


def test_affiliates_disabled_without_configuration(monkeypatch, tmp_path):
    monkeypatch.delenv("DCT_AFFILIATE_LINKS", raising=False)
    result = run_pipeline(parse_companies(["Acme Gadgets"]), MockProvider(FIXTURE), cache=None)
    SiteGenerator().build(result, str(tmp_path))
    assert "affiliate-click" not in (tmp_path / "companies/acme-gadgets.html").read_text()


def test_environment_configuration_and_explicit_disable(monkeypatch):
    monkeypatch.setenv("DCT_AFFILIATE_LINKS", json.dumps({"acme-gadgets": "https://merchant.example/"}))
    assert SiteGenerator().affiliate_links["acme-gadgets"] == "https://merchant.example/"
    assert SiteGenerator(affiliate_links={}).affiliate_links == {}


@pytest.mark.parametrize("url", ["javascript:alert(1)", "http://merchant.example", "https://user:password@merchant.example", "https:///missing", "https://merchant.example/\n", None])
def test_invalid_commercial_destinations_fail_loudly(url):
    with pytest.raises(ValueError):
        SiteGenerator(affiliate_links={"acme-gadgets": url})
