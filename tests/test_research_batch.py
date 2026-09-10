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
QUEUE_SIX_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-6.json"
)
QUEUE_SEVEN_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-7.json"
)
QUEUE_EIGHT_DATA = (
    Path(__file__).parents[1]
    / "src"
    / "dct"
    / "data"
    / "research_batch_2026-09-09_queue-8.json"
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


def test_sixth_batch_separates_verified_closures_from_unresolved_inferences():
    records = json.loads(QUEUE_SIX_DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "Boost Oxygen",
        "Boot Illusion",
        "BootayBag",
        "Booty Queen",
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
    assert by_name["Boost Oxygen"]["status"] == "operating"
    assert by_name["BootayBag"]["status"] == "closed"
    assert by_name["Boot Illusion"]["status"] == "unresolved"
    assert by_name["Booty Queen"]["status"] == "unresolved"
    assert by_name["Boost Oxygen"]["episode_appearances"][0]["deal_closed"] is True
    assert by_name["Boot Illusion"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["BootayBag"]["episode_appearances"][0]["deal_closed"] is True
    assert by_name["Booty Queen"]["episode_appearances"][0]["deal_closed"] is True

    bootaybag = by_name["BootayBag"]
    affiliate_claim = next(
        claim for claim in bootaybag["claims"] if claim["id"] == "BOOTAYBAG-DEV-5"
    )
    assert affiliate_claim["source_ids"] == ["BB10"]
    assert "not evidence" in affiliate_claim["text"]


def test_seventh_batch_preserves_deals_sales_and_episode_provenance_conflicts():
    records = json.loads(QUEUE_SEVEN_DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "Bot-It",
        "Bottle Breacher",
        "BottleKeeper",
        "Bounce Boot Camp",
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
    assert by_name["Bot-It"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Bottle Breacher"]["episode_appearances"][0]["deal_closed"] is True
    assert by_name["BottleKeeper"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["Bounce Boot Camp"]["episode_appearances"][0]["deal_closed"] is False

    bottlekeeper = by_name["BottleKeeper"]
    assert bottlekeeper["status"] == "acquired"
    assert bottlekeeper["company"]["successor_or_acquirer"] == (
        "Wind Point Partners / RTIC Outdoors"
    )
    assert any("numbering conflict" in claim["text"] for claim in bottlekeeper["claims"])

    bounce = by_name["Bounce Boot Camp"]
    assert bounce["status"] == "operating"
    assert bounce["registry_records"][0]["status"].startswith("original LLC standing")


def test_eighth_batch_withholds_unproved_closure_and_records_verified_pivots():
    records = json.loads(QUEUE_EIGHT_DATA.read_text(encoding="utf-8"))
    assert {record["company"]["name"] for record in records} == {
        "Bouquet Bar",
        "BoxBlayde",
        "BoxLock",
        "Brake Free Technologies",
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
    bouquet = by_name["Bouquet Bar"]
    assert bouquet["status"] == "unresolved"
    assert bouquet["episode_appearances"][0]["deal_closed"] is None
    assert "withholds a definitive closure" in bouquet["claims"][0]["text"]

    assert by_name["BoxBlayde"]["status"] == "operating"
    assert by_name["BoxBlayde"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["BoxLock"]["episode_appearances"][0]["deal_closed"] is False
    assert any("industrial access-control" in claim["text"] for claim in by_name["BoxLock"]["claims"])
    assert by_name["Brake Free Technologies"]["episode_appearances"][0]["deal_closed"] is True


def test_tenth_batch_does_not_promote_handshakes_or_uncorroborated_closures():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-09_queue-10.json").read_text(encoding="utf-8")
    )
    by_name = {record["company"]["name"]: record for record in records}
    # Reports published after airing still describe an on-air agreement, not closing.
    assert by_name["BRCĒ"]["episode_appearances"][0]["deal_closed"] is None
    assert any("neither independently establishes" in claim["text"]
               for claim in by_name["BRCĒ"]["claims"])
    # Repeated closure dates and a dead storefront are not independent corroboration.
    for name in ("brellaBox", "Brewers Cow"):
        assert by_name[name]["status"] == "unresolved"
        assert by_name[name]["uncertainties"]
    assert any("2018 follow-up heading" in claim["text"]
               for claim in by_name["Brewers Cow"]["claims"])
    for record in records:
        source_ids = {source["id"] for source in record["sources"]}
        for claim in record["claims"] + record["timeline"]:
            assert claim["source_ids"] and set(claim["source_ids"]) <= source_ids


def test_eleventh_batch_preserves_founder_attribution_and_registry_gaps():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-10_queue-11.json").read_text(encoding="utf-8")
    )
    buddy = next(record for record in records if record["company"]["name"] == "Bridal Buddy")
    # A televised agreement is not closed financing; the founder reports failure.
    assert buddy["episode_appearances"][0]["deal_closed"] is False
    claim = next(claim for claim in buddy["claims"] if claim["id"] == "BBUD-CLOSING")
    assert claim["evidence_level"] == "credible_report"
    assert claim["source_ids"] == ["BBUD-INC"]
    # A commercial website's LLC footer cannot manufacture a state registry result.
    assert buddy["registry_records"] == []
    assert any("entity number" in gap for gap in buddy["uncertainties"])
    for record in records:
        ids = {source["id"] for source in record["sources"]}
        for item in record["claims"] + record["timeline"]:
            assert item["source_ids"] and set(item["source_ids"]) <= ids


def test_twelfth_batch_preserves_closing_and_ownership_uncertainty():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-10_queue-12.json").read_text(encoding="utf-8")
    )
    by_name = {record["company"]["name"]: record for record in records}
    # A current company narrative cannot turn Bro Glo's televised agreement into
    # a documented closing, and current family-ownership copy cannot disprove one.
    assert by_name["Bro Glo"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Browndages"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Broccoli Wad"]["status"] == "unresolved"
    # Current brand placement does not establish Brush Hero's acquisition chain.
    acquisition = next(
        claim for claim in by_name["Brush Hero"]["claims"] if claim["id"] == "BRH-ACQUISITION"
    )
    assert acquisition["evidence_level"] == "unresolved"
    for record in records:
        ids = {source["id"] for source in record["sources"]}
        for item in record["claims"] + record["timeline"]:
            assert item["source_ids"] and set(item["source_ids"]) <= ids


def test_thirteenth_batch_retains_transaction_conflicts_and_withholds_brümachen():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-10_queue-13.json").read_text(encoding="utf-8")
    )
    by_name = {record["company"]["name"]: record for record in records}
    assert by_name["BRUW"]["status"] == "acquired"
    assert by_name["BRUW"]["episode_appearances"][0]["deal_closed"] is True
    assert "30%" in by_name["BRUW"]["claims"][1]["text"]
    assert by_name["Brümachen"]["status"] == "unresolved"
    assert by_name["Bubbly Blaster"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Buck Mason"]["registry_records"][0]["status"] == "active"


def test_fourteenth_batch_normalizes_bucketgolf_and_preserves_deal_uncertainty():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-09_queue-14.json").read_text(encoding="utf-8")
    )
    by_name = {record["company"]["name"]: record for record in records}
    assert by_name["Bucket Golf"]["company"]["aliases"] == ["BucketGolf"]
    assert by_name["Bucket Golf"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Buckle Me Baby Coats"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Budsies"]["registry_records"][0]["status"] == "active"
    assert by_name["Buena Papa"]["episode_appearances"][0]["deal_closed"] is None
    for record in records:
        ids = {source["id"] for source in record["sources"]}
        for item in record["claims"] + record["timeline"]:
            assert item["source_ids"] and set(item["source_ids"]) <= ids


def test_fifteenth_batch_withholds_bumbling_bee_and_preserves_entity_gaps():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-10_queue-15.json").read_text(encoding="utf-8")
    )
    by_name = {record["company"]["name"]: record for record in records}
    assert by_name["Bumbling Bee"]["status"] == "unresolved"
    assert by_name["Bug Bite Thing"]["episode_appearances"][0]["deal_closed"] is None
    assert by_name["Buggy Beds"]["registry_records"] == []
    assert by_name["Buffer Bit"]["episode_appearances"][0]["deal_closed"] is False
    for record in records:
        ids = {source["id"] for source in record["sources"]}
        for item in record["claims"] + record["timeline"]:
            assert item["source_ids"] and set(item["source_ids"]) <= ids


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


def test_seventeenth_batch_withholds_business_ghost_and_records_complete_rosters():
    records = json.loads(
        (DATA.parent / "research_batch_2026-09-10_queue-17.json").read_text(encoding="utf-8")
    )
    by_name = {record["company"]["name"]: record for record in records}
    assert set(by_name) == {"Burlap & Barrel", "Business Ghost", "Busy Baby Mat", "BusyBox"}
    assert by_name["Business Ghost"]["status"] == "unresolved"
    assert by_name["Business Ghost"]["episode_appearances"][0]["deal_closed"] is False
    assert by_name["BusyBox"]["episode_appearances"][0]["deal_closed"] is False
    for record in records:
        ids = {source["id"] for source in record["sources"]}
        for item in record["claims"] + record["timeline"]:
            assert item["source_ids"] and set(item["source_ids"]) <= ids
