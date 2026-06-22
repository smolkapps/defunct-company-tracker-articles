import json

import pytest

from dct.models import Company, Status
from dct.providers import (
    AnthropicProvider,
    MockProvider,
    default_provider,
    extract_json,
    parse_model_payload,
    SYSTEM_PROMPT,
)

COMPANY = Company(name="Pets.com")


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        text = 'Here you go:\n```json\n{"status": "defunct"}\n```\nhope that helps'
        assert extract_json(text)["status"] == "defunct"

    def test_fenced_without_lang(self):
        assert extract_json('```\n{"x": 2}\n```') == {"x": 2}

    def test_embedded_object(self):
        assert extract_json('prefix {"k": "v"} suffix') == {"k": "v"}

    @pytest.mark.parametrize("bad", ["", "   ", "no json here", "not even close"])
    def test_garbage_raises(self, bad):
        with pytest.raises(ValueError):
            extract_json(bad)


class TestParseModelPayload:
    def test_full_payload(self):
        payload = {
            "status": "acquired",
            "summary": "bought by Oracle",
            "as_of": "2010",
            "successor": "Oracle",
            "confidence": 0.9,
            "citations": [
                {
                    "title": "W",
                    "url": "https://en.wikipedia.org/wiki/Sun",
                    "snippet": "s",
                }
            ],
        }
        r = parse_model_payload(payload, COMPANY)
        assert r.status is Status.ACQUIRED
        assert r.successor == "Oracle"
        assert len(r.citations) == 1
        assert r.raw_status == "acquired"

    def test_citation_without_url_skipped(self):
        payload = {
            "status": "defunct",
            "citations": [{"title": "no url"}, {"url": "https://x.com"}],
        }
        r = parse_model_payload(payload, COMPANY)
        assert len(r.citations) == 1

    def test_confidence_clamped(self):
        assert (
            parse_model_payload(
                {"status": "active", "confidence": 5}, COMPANY
            ).confidence
            == 1.0
        )
        assert (
            parse_model_payload(
                {"status": "active", "confidence": -3}, COMPANY
            ).confidence
            == 0.0
        )
        assert (
            parse_model_payload(
                {"status": "active", "confidence": "x"}, COMPANY
            ).confidence
            == 0.0
        )

    def test_empty_successor_becomes_none(self):
        r = parse_model_payload({"status": "acquired", "successor": "  "}, COMPANY)
        assert r.successor is None

    def test_unknown_status_coerced(self):
        r = parse_model_payload({"status": "maybe gone?"}, COMPANY)
        assert r.status is Status.UNKNOWN


class TestMockProvider:
    def test_known_company(self):
        fixture = {
            "pets.com": {
                "status": "defunct",
                "summary": "gone",
                "citations": [{"url": "https://x.com"}],
            }
        }
        p = MockProvider(fixture)
        r = p.research(COMPANY)
        assert r.status is Status.DEFUNCT
        assert p.name == "mock"

    def test_unknown_company_returns_unknown(self):
        r = MockProvider({}).research(COMPANY)
        assert r.status is Status.UNKNOWN
        assert r.citations == []

    def test_alias_lookup(self):
        fixture = {
            "sun": {
                "status": "acquired",
                "successor": "Oracle",
                "citations": [{"url": "https://x.com"}],
            }
        }
        c = Company(name="Sun Microsystems", aliases=("Sun",))
        r = MockProvider(fixture).research(c)
        assert r.status is Status.ACQUIRED

    def test_from_json_file(self, tmp_path):
        f = tmp_path / "fix.json"
        f.write_text(
            json.dumps(
                {
                    "pets.com": {
                        "status": "defunct",
                        "citations": [{"url": "https://x.com"}],
                    }
                }
            )
        )
        p = MockProvider.from_json_file(str(f))
        assert p.research(COMPANY).status is Status.DEFUNCT


class TestSystemPrompt:
    def test_prompt_demands_sources_and_json(self):
        assert "source" in SYSTEM_PROMPT.lower()
        assert "json" in SYSTEM_PROMPT.lower()
        assert "unknown" in SYSTEM_PROMPT.lower()
        assert "never invent urls" in SYSTEM_PROMPT.lower()


class TestLiveProviderGating:
    def test_unavailable_without_key(self, monkeypatch):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        assert not AnthropicProvider.available()
        with pytest.raises(RuntimeError):
            AnthropicProvider()

    def test_available_with_key(self, monkeypatch):
        monkeypatch.setenv("DCT_LLM_API_KEY", "sk-test")
        assert AnthropicProvider.available()
        p = AnthropicProvider()  # construction must not hit the network
        assert p.name == "anthropic"
        assert p.api_key == "sk-test"

    def test_default_provider_is_mock_without_key(self, monkeypatch):
        monkeypatch.delenv("DCT_LLM_API_KEY", raising=False)
        assert isinstance(default_provider(), MockProvider)

    def test_default_provider_is_live_with_key(self, monkeypatch):
        monkeypatch.setenv("DCT_LLM_API_KEY", "sk-test")
        assert isinstance(default_provider(), AnthropicProvider)
