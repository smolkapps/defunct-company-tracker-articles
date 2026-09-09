import json
from pathlib import Path


DATA = Path(__file__).parents[1] / "src" / "dct" / "data" / "research_batch_2026-09-09.json"
QUEUE_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-2.json"
)
QUEUE_THREE_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-3.json"
)


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


def test_followup_batch_preserves_registry_conflicts_and_deal_uncertainties():
    records = json.loads(QUEUE_DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "American Ghost Walks",
        "AnyTongs",
        "AU Baby",
        "BAM Buckwheat Milk",
    }

    for record in records:
        source_ids = {source["id"] for source in record["sources"]}
        referenced = {
            source_id
            for claim in record["claims"]
            for source_id in claim["source_ids"]
        }
        referenced.update(
            source_id
            for event in record["timeline"]
            for source_id in event["source_ids"]
        )
        assert referenced <= source_ids

    by_name = {record["company"]["name"]: record for record in records}
    assert by_name["American Ghost Walks"]["registry_records"][0]["entity_number"] == "A095847"
    assert by_name["AnyTongs"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["AU Baby"]["episode_appearances"][0]["deal_closed"] is None
    assert "BAM the Brand Inc" in by_name["BAM Buckwheat Milk"]["company"]["legal_entities"]
    assert by_name["BAM Buckwheat Milk"]["uncertainties"]


def test_third_batch_preserves_identity_and_shark_deal_boundaries():
    records = json.loads(QUEUE_THREE_DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "Bear Minimum",
        "Bee D'Vine Honey Wine",
        "Big Bee, Little Bee",
        "BitsBox",
    }

    for record in records:
        source_ids = {source["id"] for source in record["sources"]}
        referenced = {
            source_id
            for claim in record["claims"]
            for source_id in claim["source_ids"]
        }
        referenced.update(
            source_id
            for event in record.get("timeline", [])
            for source_id in event["source_ids"]
        )
        referenced.update(
            registry["source_id"]
            for registry in record.get("registry_records", [])
        )
        assert referenced <= source_ids

    by_name = {record["company"]["name"]: record for record in records}
    assert by_name["Bear Minimum"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Bee D'Vine Honey Wine"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["Big Bee, Little Bee"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["BitsBox"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["BitsBox"]["company"]["legal_entities"] == ["Codepops, Inc."]
    assert by_name["Bee D'Vine Honey Wine"]["uncertainties"]
