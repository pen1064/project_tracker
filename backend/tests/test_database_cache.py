from unittest.mock import MagicMock

import pytest

from backend.database_api.core.cache import global_cache
from backend.database_api.db.models import Project
from backend.database_api.services.project_service import ProjectService


@pytest.fixture
def fake_project():
    project = Project()
    project.id = 42
    project.name = "Cached Project"
    return project


@pytest.fixture
def mock_repo(fake_project):
    repo = MagicMock()
    repo.get.return_value = fake_project
    repo.update.return_value = fake_project
    return repo


@pytest.fixture
def service(mock_repo):
    # Provide a ProjectService that uses the fake repository
    return ProjectService(mock_repo)


class TestDatabaseCache:
    def test_get_project_uses_cache(self, service, mock_repo, fake_project):
        global_cache._cache.clear()  # Always clear before tests!
        # First call: DB (repo) is hit, caches the project
        p1 = service.get(42)
        assert p1.id == 42
        assert mock_repo.get.call_count == 1

        # Second call: should return from cache, no new DB call
        p2 = service.get(42)
        assert p2.id == 42
        assert mock_repo.get.call_count == 1  # Not incremented

    def test_update_project_invalidates_cache(self, service, mock_repo, fake_project):
        global_cache._cache.clear()
        # Cache is empty at the start
        assert global_cache.get("project:42") is None

        # First get: cache is populated
        service.get(42)
        assert mock_repo.get.call_count == 1

        # Update invalidates cache, and cache for this project_id should be gone
        service.update(
            42, project_update=MagicMock(model_dump=lambda **_: {"name": "New"})
        )
        assert global_cache.get("project:42") is None

        # After update, call get again, hit repo again
        service.get(42)
        assert mock_repo.get.call_count == 3

        # After this, another call should use cache, so no increment
        service.get(42)
        assert mock_repo.get.call_count == 3
