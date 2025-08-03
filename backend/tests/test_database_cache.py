from unittest.mock import MagicMock
import pytest

from backend.database_api.core.cache import global_cache
from backend.database_api.db.models import Project
from backend.database_api.services.project_service import ProjectService


@pytest.fixture
def fake_project():
    # Create a fake Project instance with predefined id and name
    project = Project()
    project.id = 42
    project.name = "Cached Project"
    return project


@pytest.fixture
def mock_repo(fake_project):
    # Create a MagicMock repository with 'get' and 'update' methods returning the fake project
    repo = MagicMock()
    repo.get.return_value = fake_project
    repo.update.return_value = fake_project
    return repo


@pytest.fixture
def service(mock_repo):
    # Provide a ProjectService instance using the mocked repository
    return ProjectService(mock_repo)


class TestDatabaseCache:
    def test_get_project_uses_cache(self, service, mock_repo, fake_project):
        """
        Test that repeated 'get' calls for the same project id hit the DB only once,
        and subsequent calls return the cached project without querying the repo again.
        """
        global_cache._cache.clear()  # Clear global cache before test

        # First call: repo.get() should be called and cache populated
        p1 = service.get(42)
        assert p1.id == 42
        assert mock_repo.get.call_count == 1

        # Second call: should come from cache, repo.get() count stays the same
        p2 = service.get(42)
        assert p2.id == 42
        assert mock_repo.get.call_count == 1  # No additional call

    def test_update_project_invalidates_cache(self, service, mock_repo, fake_project):
        """
        Test that updating a project invalidates its cache entry:
        - After update, cache for the project should be cleared
        - Subsequent get calls hit the repo again until cached
        """
        global_cache._cache.clear()
        # Cache should initially be empty for project:42
        assert global_cache.get("project:42") is None

        # First get: repo.get() called, cache populated
        service.get(42)
        assert mock_repo.get.call_count == 1

        # Update the project — this should invalidate the cache entry
        service.update(
            42, project_update=MagicMock(model_dump=lambda **_: {"name": "New"})
        )
        # Cache entry for project:42 should be removed after update
        assert global_cache.get("project:42") is None

        # After update, get is called again — repo.get() should be called again due to cache miss
        service.get(42)
        assert mock_repo.get.call_count == 3  # Because update may internally call repo.get too

        # Another get call now hits the cache again — no new repo.get() call
        service.get(42)
        assert mock_repo.get.call_count == 3
