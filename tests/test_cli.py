import json
import os

import pytest

from dct.cli import main


class TestStatusCommand:
    def test_status_reports_mock_without_key(self, monkeypatch, capsys):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        rc = main(["status"])
        out = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert out["live_provider_available"] is False
        assert out["active_provider"] == "mock"


class TestDemoCommand:
    def test_demo_builds_site(self, monkeypatch, tmp_path, capsys):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        out_dir = str(tmp_path / "site")
        rc = main(["demo", "--out", out_dir])
        assert rc == 0
        assert os.path.exists(os.path.join(out_dir, "index.html"))
        # the bundled fixture has several verified companies -> articles exist
        assert os.path.exists(os.path.join(out_dir, "companies", "pets-com.html"))
        assert os.path.exists(
            os.path.join(out_dir, "companies", "lehman-brothers.html")
        )
        # the deliberately-imaginary company must NOT get an article
        assert not os.path.exists(
            os.path.join(out_dir, "companies", "acme-imaginary-holdings.html")
        )


class TestBuildAndResearch:
    def test_build_with_fixture(self, monkeypatch, tmp_path, capsys):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        companies = tmp_path / "co.json"
        companies.write_text(json.dumps({"companies": ["Pets.com", "Unknown Co"]}))
        fixture = tmp_path / "fix.json"
        fixture.write_text(
            json.dumps(
                {
                    "pets.com": {
                        "status": "defunct",
                        "summary": "gone in 2000",
                        "as_of": "2000",
                        "confidence": 0.9,
                        "citations": [
                            {
                                "title": "W",
                                "url": "https://en.wikipedia.org/wiki/Pets.com",
                            },
                            {"title": "C", "url": "https://money.cnn.com/x"},
                        ],
                    }
                }
            )
        )
        out_dir = str(tmp_path / "site")
        rc = main(
            [
                "build",
                str(companies),
                "--out",
                out_dir,
                "--fixture",
                str(fixture),
                "--no-cache",
            ]
        )
        assert rc == 0
        assert os.path.exists(os.path.join(out_dir, "companies", "pets-com.html"))

    def test_research_to_file(self, monkeypatch, tmp_path):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        companies = tmp_path / "co.json"
        companies.write_text(json.dumps(["Unknown Co"]))
        out = tmp_path / "reports.json"
        rc = main(
            ["research", str(companies), "--out", str(out), "--no-cache", "--mock"]
        )
        assert rc == 0
        payload = json.loads(out.read_text())
        assert payload["summary"]["total"] == 1
        assert payload["reports"][0]["status"] == "unknown"

    def test_missing_file_returns_2(self, capsys):
        rc = main(["build", "/no/such/file.json", "--no-cache"])
        assert rc == 2

    def test_bad_json_returns_2(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{ not json")
        rc = main(["build", str(bad), "--no-cache"])
        assert rc == 2
