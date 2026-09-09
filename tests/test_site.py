import os

from dct.pipeline import parse_companies, run_pipeline
from dct.providers import MockProvider
from dct.site import SiteGenerator, _jsonld_for
from dct.models import Citation, Company, Status, StatusReport
from dct.verify import verify_report

FIXTURE = {
    "pets.com": {
        "status": "defunct",
        "summary": "Pets.com liquidated in 2000.",
        "as_of": "2000",
        "confidence": 0.95,
        "citations": [
            {
                "title": "Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Pets.com",
                "snippet": "Pets.com ceased operations.",
            },
            {"title": "CNN", "url": "https://money.cnn.com/x"},
        ],
    },
}


def _result(tmp_path=None):
    companies = parse_companies(["Pets.com", "Imaginary Unverifiable Co"])
    return run_pipeline(companies, MockProvider(FIXTURE), cache=None)


class TestSiteBuild:
    def test_builds_expected_files(self, tmp_path):
        out = str(tmp_path / "site")
        stats = SiteGenerator(site_url="https://example.com").build(_result(), out)

        assert os.path.exists(os.path.join(out, "index.html"))
        assert os.path.exists(os.path.join(out, "methodology.html"))
        assert os.path.exists(os.path.join(out, "assets", "style.css"))
        assert os.path.exists(os.path.join(out, "sitemap.xml"))
        # the verified company gets an article; the unverifiable one does NOT
        assert os.path.exists(os.path.join(out, "companies", "pets-com.html"))
        assert not os.path.exists(
            os.path.join(out, "companies", "imaginary-unverifiable-co.html")
        )
        assert stats["articles"] == 1
        assert stats["withheld"] == 1

    def test_article_contains_sources_and_status(self, tmp_path):
        out = str(tmp_path / "site")
        SiteGenerator().build(_result(), out)
        html = open(
            os.path.join(out, "companies", "pets-com.html"), encoding="utf-8"
        ).read()
        assert "Pets.com" in html
        assert "badge-defunct" in html
        assert "en.wikipedia.org/wiki/Pets.com" in html
        assert "Sources" in html
        # JSON-LD present
        assert "schema.org" in html

    def test_index_lists_verified_and_hides_unverified(self, tmp_path):
        out = str(tmp_path / "site")
        SiteGenerator().build(_result(), out)
        html = open(os.path.join(out, "index.html"), encoding="utf-8").read()
        assert "companies/pets-com.html" in html
        # the unverified one appears only in the collapsed <details>, by name
        assert "Imaginary Unverifiable Co" in html
        assert "could not be verified" in html

    def test_sitemap_has_absolute_urls(self, tmp_path):
        out = str(tmp_path / "site")
        SiteGenerator(site_url="https://example.com").build(_result(), out)
        sm = open(os.path.join(out, "sitemap.xml"), encoding="utf-8").read()
        assert "https://example.com/index.html" in sm
        assert "https://example.com/companies/pets-com.html" in sm

    def test_canonical_and_robots_use_configured_site_url(self, tmp_path):
        out = str(tmp_path / "site")
        SiteGenerator(site_url="https://example.com").build(_result(), out)
        index = open(os.path.join(out, "index.html"), encoding="utf-8").read()
        article = open(
            os.path.join(out, "companies", "pets-com.html"), encoding="utf-8"
        ).read()
        methodology = open(
            os.path.join(out, "methodology.html"), encoding="utf-8"
        ).read()
        robots = open(os.path.join(out, "robots.txt"), encoding="utf-8").read()
        assert "https://www.youtube.com/watch?v=AoZdeYKGuR4" in index
        assert '<link rel="canonical" href="https://example.com/" />' in index
        assert '<meta property="og:url" content="https://example.com/" />' in index
        assert (
            '<link rel="canonical" href="https://example.com/companies/pets-com.html" />'
            in article
        )
        assert (
            '<link rel="canonical" href="https://example.com/methodology.html" />'
            in methodology
        )
        assert "Sitemap: https://example.com/sitemap.xml" in robots

    def test_html_escaping_of_company_name(self, tmp_path):
        # a company name with HTML must not break out of the page
        evil = StatusReport(
            company=Company(name="Evil <script>alert(1)</script> Co"),
            status=Status.DEFUNCT,
            summary="x",
            citations=[Citation(title="W", url="https://en.wikipedia.org/wiki/x")],
            confidence=0.9,
            as_of="2000",
        )
        verify_report(evil)
        from dct.pipeline import PipelineResult

        res = PipelineResult(reports=[evil])
        out = str(tmp_path / "site")
        SiteGenerator().build(res, out)
        slug = evil.company.slug
        html = open(
            os.path.join(out, "companies", f"{slug}.html"), encoding="utf-8"
        ).read()
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html


class TestJsonLd:
    def test_terminal_company_has_dissolution_date(self):
        r = StatusReport(
            company=Company(name="Pets.com"),
            status=Status.DEFUNCT,
            summary="gone",
            citations=[
                Citation(title="W", url="https://en.wikipedia.org/wiki/Pets.com")
            ],
            as_of="2000",
        )
        import json as _json

        node = _json.loads(_jsonld_for(r, "https://example.com"))
        assert node["@type"] == "Organization"
        assert node["dissolutionDate"] == "2000"
        assert node["name"] == "Pets.com"

    def test_renamed_company_is_not_marked_dissolved(self):
        r = StatusReport(
            company=Company(name="Hidrent"),
            status=Status.RENAMED,
            summary="Now Helpful Heroes",
            citations=[Citation(title="Official", url="https://helpfulheroes.com/")],
            as_of="2026",
            successor="Helpful Heroes",
        )
        import json as _json

        node = _json.loads(_jsonld_for(r, "https://example.com"))
        assert "dissolutionDate" not in node
