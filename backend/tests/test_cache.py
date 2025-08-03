import time
import pytest
from backend.database_api.core.cache import Cache


@pytest.fixture
def cache():
    # Fixture to provide a Cache instance with max size 10 and TTL of 1 second for each test
    return Cache(maxsize=10, ttl=1)


class TestCache:
    def test_set_and_get(self, cache):
        """
        Test basic set and get operations:
        - Initially, getting a key returns None
        - After setting a key-value pair, get returns the correct value
        """
        key = "key1"
        value = "value1"

        # Initially None
        assert cache.get(key) is None

        # Set and get
        cache.set(key, value)
        assert cache.get(key) == value

    def test_delete(self, cache):
        """
        Test deletion of a key:
        - Set a key-value pair
        - Delete the key
        - Getting the deleted key should return None
        """
        key = "key2"
        cache.set(key, "v2")
        cache.delete(key)
        assert cache.get(key) is None

    def test_clear(self, cache):
        """
        Test clearing the entire cache:
        - Set multiple key-value pairs
        - Clear the cache
        - All keys should be removed (get returns None)
        """
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.get("k1") is None
        assert cache.get("k2") is None

    def test_ttl_expiry(self, cache):
        """
        Test time-to-live (TTL) expiry:
        - Set a key with TTL = 1 second
        - Immediately after setting, the key should be retrievable
        - After sleeping beyond TTL, the key should expire and return None
        """
        key = "expiring"
        cache.set(key, "v")
        assert cache.get(key) == "v"

        # Wait for TTL to expire
        time.sleep(1.2)
        assert cache.get(key) is None
