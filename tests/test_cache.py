import time

import pytest

from backend.database_api.core.cache import Cache


@pytest.fixture
def cache():
    return Cache(maxsize=10, ttl=1)


class TestCache:
    def test_set_and_get(self, cache):
        key = "key1"
        value = "value1"

        # Initially None
        assert cache.get(key) is None

        # Set and get
        cache.set(key, value)
        assert cache.get(key) == value

    def test_delete(self, cache):
        key = "key2"
        cache.set(key, "v2")
        cache.delete(key)
        assert cache.get(key) is None

    def test_clear(self, cache):
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.get("k1") is None
        assert cache.get("k2") is None

    def test_ttl_expiry(self, cache):
        key = "expiring"
        cache.set(key, "v")
        assert cache.get(key) == "v"

        time.sleep(1.2)
        assert cache.get(key) is None
