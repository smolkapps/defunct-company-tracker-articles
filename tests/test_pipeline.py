import json

import pytest

from dct.cache import ReportCache
from dct.models import Status
from dct.pipeline import load_companies, parse_companies, run_pipeline
from dct.providers import MockProvider

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
            {
                "title": "CNN",
                "url": "https://money.cnn.com/x",
                "snippet": "Pets.com to shut down.",
            },
        ],
    },
    "sun microsystems": {
        "status": "acquired",
        "summary": "Acquired by Oracle in 2010.",
        "as_of": "2010",
        "successor": "Oracle",
        "confidence": 0.9,
        "citations": [
            {
                "title": "Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Sun_Microsystems",
                "snippet": "Oracle acquired Sun Microsystems.",
            },
        ],
    },
}


class TestParseCompanies:
    def test_bare_list(self):
        cs = parse_companies(["Acme", {"name": "Beta"}])
        assert [c.name for c in cs] == ["Acme", "Beta"]

    def test_object_with_companies(self):
        cs = parse_companies({"companies": [{"name": "Gamma"}]})
        assert cs[0].name == "Gamma"

    def test_dedupes_by_slug(self):
        cs = parse_companies(["Acme", "ACME", {"name": "acme"}])
        assert len(cs) == 1

    def test_bad_input_raises(self):
        with pytest.raises(ValueError):
            parse_companies(42)

    def test_load_from_file(self, tmp_path):
        f = tmp_path / "co.json"
        f.write_text(json.dumps({"companies": ["Acme"]}))
        assert load_companies(str(f))[0].name == "Acme"


class TestRunPipeline:
    def test_end_to_end_verifies(self):
        companies = parse_companies(["Pets.com", "Sun Microsystems", "Nonexistent Co"])
        provider = MockProvider(FIXTURE)
        result = run_pipeline(companies, provider, cache=None)

        assert result.n_researched == 3
        by_name = {r.company.name: r for r in result.reports}
        assert by_name["Pets.com"].status is Status.DEFUNCT
        assert by_name["Pets.com"].publishable
        assert by_name["Sun Microsystems"].status is Status.ACQUIRED
        # the imaginary company yields UNKNOWN and is not publishable
        assert by_name["Nonexistent Co"].status is Status.UNKNOWN
        assert not by_name["Nonexistent Co"].publishable

        assert len(result.publishable) == 2
        assert len(result.unpublishable) == 1

    def test_summary_counts(self):
        companies = parse_companies(["Pets.com", "Nonexistent Co"])
        result = run_pipeline(companies, MockProvider(FIXTURE), cache=None)
        s = result.summary()
        assert s["total"] == 2
        assert s["publishable"] == 1
        assert s["status_defunct"] == 1
        assert s["status_unknown"] == 1

    def test_ordering_publishable_terminal_first(self):
        companies = parse_companies(["Nonexistent Co", "Pets.com"])
        result = run_pipeline(companies, MockProvider(FIXTURE), cache=None)
        # publishable terminal (Pets.com) must sort before the unknown one
        assert result.reports[0].company.name == "Pets.com"


class TestPipelineCaching:
    def test_second_run_hits_cache(self, tmp_path):
        path = str(tmp_path / "c.json")
        companies = parse_companies(["Pets.com"])
        provider = MockProvider(FIXTURE)

        first = run_pipeline(companies, provider, cache=ReportCache(path))
        assert first.n_researched == 1 and first.n_cached == 0

        second = run_pipeline(companies, provider, cache=ReportCache(path))
        assert second.n_cached == 1 and second.n_researched == 0
        assert second.reports[0].publishable

    def test_force_refresh_bypasses_cache(self, tmp_path):
        path = str(tmp_path / "c.json")
        companies = parse_companies(["Pets.com"])
        provider = MockProvider(FIXTURE)
        run_pipeline(companies, provider, cache=ReportCache(path))
        forced = run_pipeline(
            companies, provider, cache=ReportCache(path), force_refresh=True
        )
        assert forced.n_researched == 1 and forced.n_cached == 0

    def test_cache_key_isolated_by_provider(self, tmp_path):
        path = str(tmp_path / "c.json")
        companies = parse_companies(["Pets.com"])
        run_pipeline(companies, MockProvider(FIXTURE), cache=ReportCache(path))
        # an empty-fixture mock has the SAME provider name, so it WILL hit cache;
        # this documents that switching the underlying data without changing the
        # provider name reuses the cache (use --force to override).
        again = run_pipeline(companies, MockProvider({}), cache=ReportCache(path))
        assert again.n_cached == 1
