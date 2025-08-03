from fastapi.testclient import TestClient
from sqlalchemy import event

from backend.database_api.db.connection import database
from backend.database_api.main import app

client = TestClient(app)


class TestProjectCache:
    @classmethod
    def setup_class(cls):
        """
        Setup method to create a new project before running cache tests.
        This project will be used to verify caching behavior on GET and PATCH requests.
        """
        payload = {
            "name": "Cache Test Project",
            "description": "Project for cache testing",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
            "status": "to do",
        }
        response = client.post("/projects/", json=payload)
        # Store the created project and its ID for use in tests
        cls.project = response.json()
        cls.project_id = cls.project["id"]

    def test_project_cache_query_count(self):
        """
        Test to ensure caching reduces database query count.
        Listens to SQLAlchemy 'before_cursor_execute' events to count DB queries.

        Sends two GET requests:
        - The first should hit the database.
        - The second should hit the cache, resulting in no additional DB queries.
        """
        query_count = 0

        def _before_cursor_execute(
                conn, cursor, statement, parameters, context, executemany
        ):
            nonlocal query_count
            query_count += 1

        # Attach listener to count DB queries before execution
        event.listen(database.engine, "before_cursor_execute", _before_cursor_execute)

        # First request, expect query count to increase
        r1 = client.get(f"/projects/{self.project_id}")
        assert r1.status_code == 200
        count1 = query_count

        # Second request, expect no additional DB queries due to cache
        r2 = client.get(f"/projects/{self.project_id}")
        assert r2.status_code == 200
        count2 = query_count
        assert count2 == count1  # No new queries after the first request

        # Remove event listener after test to avoid side effects
        event.remove(database.engine, "before_cursor_execute", _before_cursor_execute)

    def test_update_project_invalidates_cache(self):
        """
        Test that updating a project invalidates the cache.
        After a PATCH update, subsequent GET should return fresh data.
        """
        update_payload = {"status": "complete"}
        r = client.patch(f"/projects/{self.project_id}", json=update_payload)
        assert r.status_code == 200
        assert r.json()["status"] == "complete"

        # After update, GET request should return updated status (cache invalidated)
        r_after = client.get(f"/projects/{self.project_id}")
        assert r_after.status_code == 200
        assert r_after.json()["status"] == "complete"

    @classmethod
    def teardown_class(cls):
        """
        Cleanup method to delete the project after tests complete.
        """
        client.delete(f"/projects/{cls.project_id}")
