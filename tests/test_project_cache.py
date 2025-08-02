from fastapi.testclient import TestClient
from sqlalchemy import event

from backend.database_api.db.connection import database
from backend.database_api.main import app

client = TestClient(app)


class TestProjectCache:
    @classmethod
    def setup_class(cls):
        # Create a project to test caching
        payload = {
            "name": "Cache Test Project",
            "description": "Project for cache testing",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
            "status": "to do",
        }
        response = client.post("/projects/", json=payload)
        cls.project = response.json()
        cls.project_id = cls.project["id"]

    def test_project_cache_query_count(self):
        # Instead of checking query time, check query count to the db, more accurate
        query_count = 0

        def _before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            nonlocal query_count
            query_count += 1

        event.listen(database.engine, "before_cursor_execute", _before_cursor_execute)

        # First request
        r1 = client.get(f"/projects/{self.project_id}")
        assert r1.status_code == 200
        count1 = query_count

        # Second request, should use cache instead of db
        r2 = client.get(f"/projects/{self.project_id}")
        assert r2.status_code == 200
        count2 = query_count
        assert count2 == count1  # No new queries after the first

        event.remove(database.engine, "before_cursor_execute", _before_cursor_execute)

    def test_update_project_invalidates_cache(self):
        # Update the project so that cache is invalidated
        update_payload = {"status": "complete"}
        r = client.patch(f"/projects/{self.project_id}", json=update_payload)
        assert r.status_code == 200
        assert r.json()["status"] == "complete"

        # After update, the next GET should return updated data
        r_after = client.get(f"/projects/{self.project_id}")
        assert r_after.status_code == 200
        assert r_after.json()["status"] == "complete"

    @classmethod
    def teardown_class(cls):
        # Clean up: delete project
        client.delete(f"/projects/{cls.project_id}")
