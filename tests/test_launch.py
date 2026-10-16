"""Tests for the defunctcompanies.com launch changes: as_of dates, sitemap
lastmod, hub pages, og:image, and the records-driven publish build."""

import json
import os
import re

from dct.cli import main
from dct.pipeline import parse_companies, run_pipeline
from dct.providers import MockProvider
from dct.site import SiteGenerator, _w3c_date

FIXTURE = {
    "pets.com": {
        "status": "defunct",
        "summary": "Pets.com liquidated in 2000.",
        "as_of": "2000-11-07",
        "confidence": 0.95,
        "citations": [
            {"title": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Pets.com",
             "snippet": "Pets.com ceased operations."},
            {"title": "CNN", "url": "https://money.cnn.com/x"},
        ],
    },
    "acme gadgets": {
        "status": "active",
        "summary": "Acme Gadgets still sells gadgets.",
        "as_of": "2026-09-09",
        "confidence": 0.9,
        "citations": [
            {"title": "Acme", "url": "https://acme.example/", "snippet": "Acme Gadgets store"},
            {"title": "News", "url": "https://www.reuters.com/acme"},
        ],
    },
}


def _build(tmp_path, records=()):
    companies = parse_companies(
        ["Pets.com", {"name": "Acme Gadgets", "tags": ["shark-tank"]}, "Nobody Inc"]
    )
    result = run_pipeline(companies, MockProvider(FIXTURE), cache=None)
    out = str(tmp_path / "site")
    stats = SiteGenerator(site_url="https://defunctcompanies.com").build(
        result, out, records
    )
    return out, stats


def _read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return fh.read()


def _record(name, status, claims, sources, **company):
    return {
        "company": {"name": name, "aliases": [], "legal_entities": [],
                    "successor_or_acquirer": company.get("successor")},
        "status": status,
        "as_of": "2026-09-10",
        "confidence": "high",
        "episode_appearances": [],
        "claims": claims,
        "sources": sources,
        "uncertainties": [],
    }


SRC = [
    {"id": "S1", "title": "Official site", "url": "https://widget.example/",
     "source_type": "official site", "accessed": "2026-09-10"},
    {"id": "S2", "title": "Trade press", "url": "https://www.forbes.com/widget",
     "source_type": "press", "published": "2025-01-01", "accessed": "2026-09-10"},
]


class TestDatesAndSitemap:
    def test_researched_uses_as_of_not_build_time(self, tmp_path):
        out, _ = _build(tmp_path)
        html = _read(out, "companies", "pets-com.html")
        assert '<dt>Researched</dt><dd><time datetime="2000-11-07">2000-11-07</time>' in html
        # build-time ISO timestamps must not be presented as research dates
        assert not re.search(r"<dt>Researched</dt><dd>\d{4}-\d{2}-\d{2}T", html)

    def test_sitemap_lastmod_from_as_of(self, tmp_path):
        out, _ = _build(tmp_path)
        sm = _read(out, "sitemap.xml")
        assert ("<loc>https://defunctcompanies.com/companies/pets-com.html</loc>"
                "<lastmod>2000-11-07</lastmod>") in sm
        assert "<loc>https://defunctcompanies.com/</loc><lastmod>2026-09-09</lastmod>" in sm
        # withheld companies never enter the sitemap
        assert "nobody-inc" not in sm

    def test_w3c_date_filter(self):
        assert _w3c_date("2026-09-10") == "2026-09-10"
        assert _w3c_date("2021") == "2021"
        assert _w3c_date("2026-fall") == ""
        assert _w3c_date("") == ""


class TestHubsAndSocial:
    def test_status_and_collection_hubs(self, tmp_path):
        out, stats = _build(tmp_path)
        assert os.path.exists(os.path.join(out, "status", "defunct.html"))
        assert os.path.exists(os.path.join(out, "status", "active.html"))
        assert not os.path.exists(os.path.join(out, "status", "acquired.html"))
        shark = _read(out, "collections", "shark-tank.html")
        other = _read(out, "collections", "other-companies.html")
        assert "Acme Gadgets" in shark and "Pets.com" not in shark
        assert "Pets.com" in other and "Acme Gadgets" not in other
        assert '"@type": "ItemList"' in shark
        assert stats["hubs"] == 4
        sm = _read(out, "sitemap.xml")
        for path in ("status/defunct.html", "status/active.html",
                     "collections/shark-tank.html", "collections/other-companies.html"):
            assert f"https://defunctcompanies.com/{path}" in sm
        index = _read(out, "index.html")
        assert 'href="collections/shark-tank.html"' in index
        assert 'href="status/defunct.html"' in index

    def test_og_image_and_canonical_on_new_domain(self, tmp_path):
        out, _ = _build(tmp_path)
        for page in ("index.html", os.path.join("companies", "pets-com.html"),
                     os.path.join("status", "defunct.html")):
            html = _read(out, page)
            assert '<meta property="og:image" content="https://defunctcompanies.com/assets/og.png"' in html
            assert '<link rel="canonical" href="https://defunctcompanies.com/' in html
        assert os.path.exists(os.path.join(out, "assets", "og.png"))
        assert "Sitemap: https://defunctcompanies.com/sitemap.xml" in _read(out, "robots.txt")


class TestRecordsPayload:
    def test_operating_record_becomes_active_with_status_sources(self):
        from dct.records import record_to_payload

        rec = _record("Widget", "operating", [
            {"id": "W-STATUS", "text": "Widget is operating.",
             "evidence_level": "verified_fact", "source_ids": ["S1"]},
            {"id": "W-2", "text": "Unrelated unresolved bit.",
             "evidence_level": "unresolved", "source_ids": ["S2"]},
        ], SRC)
        p = record_to_payload(rec)
        assert p["status"] == "active"
        assert p["summary"] == "Widget is operating."
        assert [c["url"] for c in p["citations"]] == ["https://widget.example/"]
        assert p["as_of"] == "2026-09-10"

    def test_unresolved_record_is_unknown(self):
        from dct.records import record_to_payload

        rec = _record("Widget", "unresolved", [
            {"id": "W-STATUS", "text": "Status unresolved.",
             "evidence_level": "unresolved", "source_ids": ["S1"]}], SRC)
        p = record_to_payload(rec)
        assert p["status"] == "unknown" and p["citations"] == []

    def test_status_without_backing_claim_is_downgraded(self):
        from dct.records import record_to_payload

        # a "closed" status backed only by an allegation / dangling source id
        rec = _record("Widget", "closed", [
            {"id": "W-STATUS", "text": "Rumoured closed.",
             "evidence_level": "allegation", "source_ids": ["S1"]},
            {"id": "W-2", "text": "Closed.", "evidence_level": "verified_fact",
             "source_ids": ["MISSING"]}], SRC)
        assert record_to_payload(rec)["status"] == "unknown"

    def test_acquired_record_carries_successor(self):
        from dct.records import record_to_payload

        rec = _record("Widget", "acquired", [
            {"id": "W-STATUS", "text": "Bought by BigCo.",
             "evidence_level": "verified_fact", "source_ids": ["S2", "S1"]}],
            SRC, successor="BigCo, Inc.")
        p = record_to_payload(rec)
        assert p["status"] == "acquired" and p["successor"] == "BigCo, Inc."
        assert [c["url"] for c in p["citations"]] == [
            "https://www.forbes.com/widget", "https://widget.example/"]

    def test_records_override_legacy_fixture(self):
        from dct.models import Company
        from dct.records import merge_records

        rec = _record("Widget", "unresolved", [
            {"id": "W", "text": "Unresolved.", "evidence_level": "unresolved",
             "source_ids": ["S1"]}], SRC)
        legacy = [Company(name="Widget", domain="widget.example"), Company(name="Pets.com")]
        fixture = {"widget": {"status": "active", "summary": "stale",
                              "citations": [{"url": "https://x.example"}]},
                   "pets.com": FIXTURE["pets.com"]}
        companies, fx = merge_records([rec], legacy, fixture)
        assert fx["widget"]["status"] == "unknown"  # record wins
        assert fx["pets.com"]["status"] == "defunct"
        widget = next(c for c in companies if c.name == "Widget")
        assert widget.domain == "widget.example" and "shark-tank" in widget.tags


class TestPublishCommand:
    def test_publish_matches_reviewed_records_and_gate(self, monkeypatch, tmp_path, capsys):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        out = str(tmp_path / "dist")
        rc = main(["publish", "--out", out, "--site-url", "https://defunctcompanies.com"])
        assert rc == 0
        text = capsys.readouterr().out
        stats = json.loads(text[text.index("{"):text.rindex("}") + 1])
        # every reviewed "unresolved" record stays withheld; nothing else is
        from dct.cli import SAMPLE_RESEARCH
        from dct.records import load_record_files

        records = load_record_files([SAMPLE_RESEARCH])
        unresolved = {r["company"]["name"] for r in records if r["status"] == "unresolved"}
        assert stats["withheld"] == len(unresolved) == stats["research_only"]
        for name in unresolved:
            from dct.models import slugify

            html = _read(out, "companies", f"{slugify(name)}.html")
            assert 'content="noindex, follow"' in html
        assert stats["hubs"] >= 6
        sm = _read(out, "sitemap.xml")
        assert sm.count("<url>") == stats["articles"] + stats["hubs"] + 2
        assert "https://defunctcompanies.com/collections/shark-tank.html" in sm

    def test_records_only_excludes_legacy_companies(self, monkeypatch, tmp_path, capsys):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        out = str(tmp_path / "dist")
        assert main(["publish", "--records-only", "--out", out]) == 0
        assert not os.path.exists(os.path.join(out, "companies", "pets-com.html"))
        assert not os.path.exists(os.path.join(out, "collections", "other-companies.html"))
        assert os.path.exists(os.path.join(out, "companies", "squatty-potty.html"))


class TestUmamiAnalytics:
    def test_umami_omitted_when_unset(self, monkeypatch, tmp_path):
        monkeypatch.delenv("DCT_UMAMI_WEBSITE_ID", raising=False)
        monkeypatch.delenv("UMAMI_WEBSITE_ID", raising=False)
        out, _ = _build(tmp_path)
        for rel in (
            "index.html",
            "methodology.html",
            "404.html",
            os.path.join("companies", "pets-com.html"),
            os.path.join("status", "defunct.html"),
        ):
            html = _read(out, rel)
            assert "umami.smolkin.org" not in html
            assert "data-website-id" not in html

    def test_umami_injected_via_env_and_cli(self, monkeypatch, tmp_path):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        monkeypatch.setenv(
            "DCT_UMAMI_WEBSITE_ID", "d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014"
        )
        out, _ = _build(tmp_path)
        expected_tag = (
            '<script defer src="https://umami.smolkin.org/script.js" '
            'data-website-id="d4f8c012-7e3b-49a5-9c1d-5b8e2f6a9014"></script>'
        )
        for rel in (
            "index.html",
            "methodology.html",
            "404.html",
            os.path.join("companies", "pets-com.html"),
            os.path.join("status", "defunct.html"),
        ):
            assert expected_tag in _read(out, rel)

        # CLI flag overrides env
        cli_out = str(tmp_path / "cli_dist")
        rc = main(
            [
                "publish",
                "--out",
                cli_out,
                "--site-url",
                "https://defunctcompanies.com",
                "--umami-website-id",
                "custom-id-123",
                "--umami-script-url",
                "https://umami.smolkin.org/script.js",
            ]
        )
        assert rc == 0
        assert (
            '<script defer src="https://umami.smolkin.org/script.js" '
            'data-website-id="custom-id-123"></script>'
        ) in _read(cli_out, "index.html")


class TestSeoEnhancements:
    def test_titles_descriptions_jsonld_and_internal_links(self, tmp_path):
        rec_a = _record(
            "Alpha Shark",
            "operating",
            [
                {
                    "id": "A-1",
                    "text": "Alpha Shark operates an active online storefront.",
                    "evidence_level": "verified_fact",
                    "source_ids": ["S1", "S2"],
                }
            ],
            SRC,
        )
        rec_a["episode_appearances"] = [
            {
                "season": 12,
                "episode": 14,
                "episode_date": "2021-02-19",
                "kind": "episode",
                "video_url": "https://abc.com/show/e890218f-03d0-4c9a-900e-a169fb906f8c",
                "video_title": "ABC S12E14",
                "deal_closed": True,
            }
        ]
        rec_b = _record(
            "Beta Shark",
            "operating",
            [
                {
                    "id": "B-1",
                    "text": "Beta Shark continues selling direct-to-consumer.",
                    "evidence_level": "verified_fact",
                    "source_ids": ["S1", "S2"],
                }
            ],
            SRC,
        )
        rec_b["episode_appearances"] = [
            {
                "season": 12,
                "episode": 14,
                "episode_date": "2021-02-19",
                "kind": "episode",
                "video_url": "https://abc.com/show/e890218f-03d0-4c9a-900e-a169fb906f8c",
                "video_title": "ABC S12E14",
                "deal_closed": False,
            }
        ]
        from dct.records import merge_records

        companies, fx = merge_records(
            [rec_a, rec_b], parse_companies(["Pets.com"]), dict(FIXTURE)
        )
        result = run_pipeline(companies, MockProvider(fx), cache=None)
        out = str(tmp_path / "seo_site")
        SiteGenerator(site_url="https://defunctcompanies.com").build(
            result, out, [rec_a, rec_b]
        )

        alpha_html = _read(out, "companies", "alpha-shark.html")
        assert (
            "<title>Alpha Shark — Is It Still in Business? (Active) | Defunct Company Tracker</title>"
            in alpha_html
        )
        assert 'meta name="description" content="Is Alpha Shark still in business? Verified status: active (as of 2026-09-10).' in alpha_html
        assert '"@type": "BreadcrumbList"' in alpha_html
        assert '"mainEntityOfPage": "https://defunctcompanies.com/companies/alpha-shark.html"' in alpha_html
        # Episode companion link to Beta Shark
        assert "Other companies from this Shark Tank episode" in alpha_html
        assert 'href="beta-shark.html"' in alpha_html
        # Breadcrumb links to collection & status hubs
        assert 'href="../collections/shark-tank.html"' in alpha_html
        assert 'href="../status/active.html"' in alpha_html

        index_html = _read(out, "index.html")
        assert '"@type": "WebSite"' in index_html
        method_html = _read(out, "methodology.html")
        assert '"@type": "WebPage"' in method_html
        sm = _read(out, "sitemap.xml")
        assert (
            "<loc>https://defunctcompanies.com/methodology.html</loc>"
            "<lastmod>2026-09-10</lastmod>"
        ) in sm
        assert "404.html" not in sm


class TestOldSubdomainRedirectConfig:
    def test_nginx_redirect_preserves_path_with_301(self):
        conf_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "deploy",
            "nginx",
            "old-subdomain-redirect.conf",
        )
        conf = _read(conf_path)
        assert "server_name defunct-company-tracker-articles.apps.smolkin.org;" in conf
        assert "return 301 https://defunctcompanies.com$request_uri;" in conf
        assert "/etc/letsencrypt/live/apps-smolkin/fullchain.pem" in conf


class TestNewQueues:
    def test_all_batches_validate_against_schema(self):
        import glob
        import jsonschema

        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "src",
            "dct",
            "data",
            "research-record.schema.json",
        )
        with open(schema_path, encoding="utf-8") as fh:
            schema = json.load(fh)

        data_dir = os.path.dirname(schema_path)
        batches = sorted(glob.glob(os.path.join(data_dir, "research_batch_*.json")))
        assert len(batches) >= 23  # base batch + 22 queue batches (queues 2-23)
        total = 0
        for batch_file in batches:
            with open(batch_file, encoding="utf-8") as fh:
                records = json.load(fh)
            assert isinstance(records, list) and len(records) > 0
            for r in records:
                jsonschema.validate(r, schema)
                total += 1
        assert total >= 96

    def test_queues_20_to_23_companies_published(self, monkeypatch, tmp_path):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        out = str(tmp_path / "new_queues_dist")
        assert main(["publish", "--out", out, "--site-url", "https://defunctcompanies.com"]) == 0

        # Verify all 12 companion companies from Queues 20-23 generated published articles
        expected_slugs = [
            # Queue 20 (S12E14)
            "pashion",
            "souper-cubes",
            "sienna-sauce",
            # Queue 21 (S11E4)
            "knife-aid",
            "plop-star",
            "snacklins",
            # Queue 22 (S12E7)
            "holiball",
            "toilet-timer",
            "odr-skis",
            # Queue 23 (S14E19)
            "parting-stone",
            "cincha-travel",
            "milkify",
        ]
        for slug in expected_slugs:
            path = os.path.join(out, "companies", f"{slug}.html")
            assert os.path.exists(path), f"Missing article for {slug}"
            html = _read(path)
            # Must be an indexable published article, not withheld noindex
            assert 'content="noindex' not in html
            assert "Is It Still in Business?" in html
            assert '<span class="badge badge-active">active</span>' in html


