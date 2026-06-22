"""Status providers.

A *provider* turns a :class:`Company` into a raw :class:`StatusReport` (before
verification). There are two concrete kinds:

* :class:`MockProvider` — deterministic, offline, seeded from a fixture dict.
  Used by the whole test suite and by ``--demo`` so the pipeline can be run end
  to end with zero credentials. This is the default when no API key is present.

* :class:`AnthropicProvider` — calls a real internet-capable LLM. It is fully
  stubbed behind the ``DCT_LLM_API_KEY`` environment variable: if the key is
  absent we never import or hit the network. The *parsing* of the model's JSON
  response (the only part with real logic) is factored into the pure function
  :func:`parse_model_payload`, which is unit-tested against saved fixtures
  without any network call.

Keeping the network strictly at the edges (one thin ``_call_model`` method) and
all decision logic in pure functions is what makes this testable offline while
still being a genuine, runnable LLM integration rather than a CLI toy.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Protocol

from .models import Citation, Company, Status, StatusReport

# The instruction we give an internet-capable model. Kept module-level so a test
# can assert it demands sources + JSON, and so it is easy to audit.
SYSTEM_PROMPT = """\
You are a meticulous business-records researcher. For the company named by the
user, determine its CURRENT corporate status using web sources you can cite.

Rules:
- Only assert a status you can back with a real, linkable source.
- If you cannot find reliable evidence, return status "unknown" — do NOT guess.
- Prefer primary/credible sources (SEC filings, Companies House, Crunchbase,
  major news outlets, the company's own site, Wikipedia).
- Never invent URLs. If you have no URL, omit the citation.

Respond with ONLY a JSON object of this exact shape:
{
  "status": "active|acquired|merged|defunct|bankrupt|renamed|unknown",
  "summary": "1-3 sentence plain-English explanation",
  "as_of": "year or date the status is accurate as of, or empty string",
  "successor": "acquirer / new name if acquired|merged|renamed, else null",
  "confidence": 0.0,
  "citations": [
    {"title": "...", "url": "https://...", "snippet": "...", "published": "..."}
  ]
}
"""


class Provider(Protocol):
    name: str

    def research(self, company: Company) -> StatusReport: ...


# --------------------------------------------------------------------------- #
# Pure response parsing (no network) — the only non-trivial logic in providers
# --------------------------------------------------------------------------- #

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> dict[str, Any]:
    """Pull the first JSON object out of a model response.

    LLMs love to wrap JSON in prose or ```json fences. We strip a fenced block
    if present, else fall back to the first ``{...}`` span. Raises ``ValueError``
    on anything we cannot parse — callers treat that as "unknown".
    """
    if not text or not text.strip():
        raise ValueError("empty model response")
    s = text.strip()
    # strip code fences
    if "```" in s:
        # take the content of the first fenced block
        parts = s.split("```")
        for chunk in parts[1:]:
            chunk = chunk.strip()
            if chunk.lower().startswith("json"):
                chunk = chunk[4:].strip()
            if chunk.startswith("{"):
                s = chunk
                break
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        m = _JSON_BLOCK_RE.search(s)
        if not m:
            raise ValueError("no JSON object found in model response")
        return json.loads(m.group(0))


def parse_model_payload(payload: dict[str, Any], company: Company) -> StatusReport:
    """Turn a parsed model JSON object into an (unverified) StatusReport.

    Defensive throughout: missing fields default sanely, the status is coerced
    onto the known enum, citations with no URL are skipped (the verifier would
    drop them anyway, but skipping here keeps the cache clean), and confidence
    is clamped to [0,1].
    """
    raw_status = payload.get("status")
    status = Status.coerce(raw_status)

    citations: list[Citation] = []
    for c in payload.get("citations") or []:
        if not isinstance(c, dict):
            continue
        url = (c.get("url") or "").strip()
        if not url:
            continue
        try:
            citations.append(Citation.from_dict(c))
        except ValueError:
            continue

    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(confidence, 1.0))

    successor = payload.get("successor")
    if isinstance(successor, str) and not successor.strip():
        successor = None

    return StatusReport(
        company=company,
        status=status,
        summary=(payload.get("summary") or "").strip(),
        citations=citations,
        confidence=confidence,
        as_of=(payload.get("as_of") or "").strip(),
        successor=successor,
        raw_status=str(raw_status) if raw_status is not None else None,
    )


# --------------------------------------------------------------------------- #
# Mock provider — deterministic, offline
# --------------------------------------------------------------------------- #


class MockProvider:
    """Returns canned results from an in-memory fixture keyed by company name.

    Unknown companies yield a well-formed UNKNOWN report (mirroring how the real
    model is instructed to behave when it finds nothing), so the pipeline is
    exercised on both the happy and the empty path.
    """

    name = "mock"

    def __init__(self, fixture: dict[str, dict[str, Any]] | None = None) -> None:
        self.fixture = fixture or {}

    def _key(self, name: str) -> str:
        return name.strip().lower()

    def research(self, company: Company) -> StatusReport:
        payload = self.fixture.get(self._key(company.name))
        if payload is None:
            # also try aliases
            for alias in company.aliases:
                payload = self.fixture.get(self._key(alias))
                if payload is not None:
                    break
        if payload is None:
            return StatusReport(
                company=company,
                status=Status.UNKNOWN,
                summary="No information found for this company.",
                citations=[],
                confidence=0.0,
                raw_status="unknown",
            )
        return parse_model_payload(payload, company)

    @classmethod
    def from_json_file(cls, path: str) -> "MockProvider":
        with open(path, "r", encoding="utf-8") as fh:
            return cls(json.load(fh))


# --------------------------------------------------------------------------- #
# Real provider — Anthropic Messages API, stubbed behind an env var
# --------------------------------------------------------------------------- #


class AnthropicProvider:
    """Calls a real internet-capable LLM to research a company.

    The network/SDK is touched only inside :meth:`_call_model`. Construction
    fails loudly if no API key is configured, so callers can fall back to the
    mock provider deliberately rather than accidentally hitting the network.
    """

    name = "anthropic"

    #: env var holding the API key — absence means "no real provider available"
    API_KEY_ENV = "DCT_LLM_API_KEY"
    DEFAULT_MODEL = "claude-3-5-sonnet-latest"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get(self.API_KEY_ENV)
        if not self.api_key:
            raise RuntimeError(
                f"{self.API_KEY_ENV} is not set; cannot use the live LLM provider. "
                f"Use the mock/demo provider or set the key."
            )
        self.model = model or os.environ.get("DCT_LLM_MODEL", self.DEFAULT_MODEL)
        self._client = None  # lazily created in _call_model

    @classmethod
    def available(cls) -> bool:
        return bool(os.environ.get(cls.API_KEY_ENV))

    def _client_or_create(self):  # pragma: no cover - thin SDK wiring
        if self._client is None:
            try:
                import anthropic
            except ImportError as e:
                raise RuntimeError(
                    "The 'anthropic' package is required for the live provider. "
                    "Install with: pip install 'defunct-company-tracker[llm]'"
                ) from e
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def _build_user_prompt(self, company: Company) -> str:
        bits = [f"Company name: {company.name}"]
        if company.aliases:
            bits.append("Also known as: " + ", ".join(company.aliases))
        if company.domain:
            bits.append(f"Website/domain hint: {company.domain}")
        if company.founded:
            bits.append(f"Founded around: {company.founded}")
        if company.notes:
            bits.append(f"Notes: {company.notes}")
        return "\n".join(bits)

    def _call_model(self, company: Company) -> str:  # pragma: no cover - network
        client = self._client_or_create()
        msg = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": self._build_user_prompt(company)}],
        )
        # concatenate text blocks
        parts = []
        for block in msg.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts)

    def research(self, company: Company) -> StatusReport:
        try:
            raw = self._call_model(company)
            payload = extract_json(raw)
            return parse_model_payload(payload, company)
        except Exception as e:  # pragma: no cover - network/parse failure path
            # never crash the run; degrade to UNKNOWN with a flag-able summary
            return StatusReport(
                company=company,
                status=Status.UNKNOWN,
                summary=f"Provider error: {e}",
                citations=[],
                confidence=0.0,
                raw_status=None,
            )


def default_provider(
    fixture: dict[str, dict[str, Any]] | None = None,
) -> Provider:
    """Pick a provider automatically.

    Live LLM if a key is configured, otherwise the offline mock. This is what
    lets ``dct build`` Just Work with no credentials (producing UNKNOWN reports
    for everything, which are honestly marked unpublishable) while upgrading to
    real research the moment a key is present.
    """
    if AnthropicProvider.available():
        return AnthropicProvider()
    return MockProvider(fixture)
