import pytest

from backend.database_api.core.cache import global_cache


@pytest.fixture(autouse=True)
def clear_global_cache():
    global_cache.clear()
