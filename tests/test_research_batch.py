import json
from pathlib import Path


DATA = Path(__file__).parents[1] / "src" / "dct" / "data" / "research_batch_2026-09-09.json"


def test_research_batch_keeps_claims_source_complete_and_uncertainty_explicit():
    records = json.loads(DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "ActionGlow",
        "AfreSheet",
        "1920 Convertible Jackets",
        "ALL33",
    }

    for record in records:
        source_ids = {source["id"] for source in record["sources"]}
        claim_ids = {
            source_id
            for claim in record["claims"]
            for source_id in claim["source_ids"]
        }
        timeline_ids = {
            source_id
            for event in record["timeline"]
            for source_id in event["source_ids"]
        }
        assert claim_ids <= source_ids
        assert timeline_ids <= source_ids

    by_name = {record["company"]["name"]: record for record in records}
    assert by_name["AfreSheet"]["status"] == "renamed"
    assert by_name["AfreSheet"]["company"]["successor_or_acquirer"]
    # A conflicting business/registry trail must remain unresolved rather than
    # being promoted to active or defunct by a current profile alone.
    assert by_name["ALL33"]["status"] == "unresolved"
    assert by_name["ALL33"]["uncertainties"]
