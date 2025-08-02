import logging
from typing import Any, Optional

from cachetools import TTLCache


class Cache:
    def __init__(self, maxsize: int = 100, ttl: int = 30):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def set(self, key: str, value: Any) -> None:
        """Set a value to cache"""
        logging.debug(f"CACHE SET: {key}")
        self._cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache"""
        logging.debug(f"CACHE GET: {key}")
        return self._cache.get(key)

    def clear(self) -> None:
        """Clear all cached values"""
        logging.debug("CLEAR CACHE")
        self._cache.clear()

    def delete(self, key: str) -> None:
        if key in self._cache:
            logging.debug(f"CACHE DELETE: {key}")
            del self._cache[key]


global_cache = Cache(maxsize=200, ttl=30)
