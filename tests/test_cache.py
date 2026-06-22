from datetime import datetime, timedelta, timezone

from dct.cache import ReportCache, cache_key
from dct.models import Citation, Company, Status, StatusReport


def _report(name="Pets.com"):
    return StatusReport(
        company=Company(name=name),
        status=Status.DEFUNCT,
        summary="gone",
        citations=[Citation(title="W", url="https://en.wikipedia.org/wiki/Pets.com")],
        confidence=0.9,
        as_of="2000",
        verified=True,
        verification_score=0.8,
    )


class TestCacheKey:
    def test_provider_changes_key(self):
        c = Company(name="X")
        assert cache_key(c, "mock") != cache_key(c, "anthropic")

    def test_aliases_change_key(self):
        a = Company(name="X")
        b = Company(name="X", aliases=("Y",))
        assert cache_key(a, "mock") != cache_key(b, "mock")

    def test_alias_order_does_not_matter(self):
        a = Company(name="X", aliases=("Y", "Z"))
        b = Company(name="X", aliases=("Z", "Y"))
        assert cache_key(a, "mock") == cache_key(b, "mock")


class TestRoundTrip:
    def test_put_get_save_load(self, tmp_path):
        path = str(tmp_path / "cache.json")
        cache = ReportCache(path)
        r = _report()
        cache.put(r, "mock")
        cache.save()

        fresh = ReportCache(path)
        got = fresh.get(r.company, "mock")
        assert got is not None
        assert got.status is Status.DEFUNCT
        assert got.verified
        assert got.citations[0].url == "https://en.wikipedia.org/wiki/Pets.com"

    def test_miss_on_different_provider(self, tmp_path):
        cache = ReportCache(str(tmp_path / "c.json"))
        r = _report()
        cache.put(r, "mock")
        assert cache.get(r.company, "anthropic") is None

    def test_membership_and_len(self, tmp_path):
        cache = ReportCache(str(tmp_path / "c.json"))
        r = _report()
        cache.put(r, "mock")
        assert (r.company, "mock") in cache
        assert len(cache) == 1


class TestTTL:
    def test_stale_entry_is_a_miss(self, tmp_path):
        path = str(tmp_path / "c.json")
        cache = ReportCache(path, ttl_days=30)
        r = _report()
        old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(
            timespec="seconds"
        )
        r.retrieved_at = old
        cache.put(r, "mock")
        cache.save()

        reloaded = ReportCache(path, ttl_days=30)
        assert reloaded.get(r.company, "mock") is None  # too old

    def test_fresh_entry_hits(self, tmp_path):
        cache = ReportCache(str(tmp_path / "c.json"), ttl_days=30)
        r = _report()
        cache.put(r, "mock")
        assert cache.get(r.company, "mock") is not None

    def test_ttl_none_never_expires(self, tmp_path):
        cache = ReportCache(str(tmp_path / "c.json"), ttl_days=None)
        r = _report()
        r.retrieved_at = (datetime.now(timezone.utc) - timedelta(days=9999)).isoformat()
        cache.put(r, "mock")
        assert cache.get(r.company, "mock") is not None


class TestResilience:
    def test_corrupt_cache_file_starts_fresh(self, tmp_path):
        path = tmp_path / "c.json"
        path.write_text("{ this is not json")
        cache = ReportCache(str(path))
        assert len(cache) == 0  # did not raise

    def test_atomic_save_no_tmp_left(self, tmp_path):
        path = tmp_path / "c.json"
        cache = ReportCache(str(path))
        cache.put(_report(), "mock")
        cache.save()
        leftovers = list(tmp_path.glob("*.tmp"))
        assert leftovers == []
