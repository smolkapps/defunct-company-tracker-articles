import json
import re
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
QUEUE_FOUR_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-4.json"
)
QUEUE_FIVE_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-5.json"
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


def test_fourth_batch_publishes_only_independently_supported_transitions():
    records = json.loads(QUEUE_FOUR_DATA.read_text(encoding="utf-8"))
    assert len(records) == 12

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
    assert {
        name for name, record in by_name.items() if record["status"] == "unresolved"
    } == {"Breathometer", "Copa di Vino", "Toygaroo", "Wild Earth"}

    for name in (
        "Bottle Bright",
        "Cycloramic / Car360",
        "Doorbot / Ring",
        "GrooveBook",
        "LARQ",
        "Mother Beverage / Poppi",
        "Plated",
        "Squatty Potty",
    ):
        assert by_name[name]["status"] == "acquired"
        assert by_name[name]["company"]["successor_or_acquirer"]

    # The public claim stops at the documented acquisition rather than
    # promoting weaker reports about GrooveBook and Plated later closing.
    assert by_name["GrooveBook"]["company"]["successor_or_acquirer"] == "Shutterfly, Inc."
    assert by_name["Plated"]["company"]["successor_or_acquirer"] == "Albertsons Companies"


def test_fifth_batch_corrects_identity_and_preserves_deal_boundaries():
    records = json.loads(QUEUE_FIVE_DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "Black Paper Party",
        "Blackdot",
        "Blinger",
        "Boona",
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
        assert record["status"] == "operating"

    by_name = {record["company"]["name"]: record for record in records}
    black_paper = by_name["Black Paper Party"]
    assert black_paper["episode_appearances"][0]["episode"] == 8
    assert "Black Paper Company" not in black_paper["company"]["aliases"]
    assert black_paper["episode_appearances"][0]["deal_closed"] is False
    assert by_name["Blackdot"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["Blinger"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Boona"]["company"]["legal_entities"] == ["Deburr LLC"]


def test_timeline_schema_accepts_honest_partial_dates_used_by_research():
    schema = json.loads(
        (DATA.parent / "research-record.schema.json").read_text(encoding="utf-8")
    )
    pattern = schema["$defs"]["timeline_event"]["properties"]["date"]["pattern"]
    records = []
    for path in sorted(DATA.parent.glob("research_batch*.json")):
        records.extend(json.loads(path.read_text(encoding="utf-8")))

    for record in records:
        for event in record.get("timeline", []):
            assert re.fullmatch(pattern, event["date"]), (
                record["company"]["name"],
                event["date"],
            )
