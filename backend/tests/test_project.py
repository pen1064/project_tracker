from fastapi.testclient import TestClient

from backend.database_api.main import app

client = TestClient(app)


class TestProjectsFastAPI:
    @classmethod
    def setup_class(cls):
        # Create a project to use in tests
        payload = {
            "name": "UnitTest Project",
            "description": "Project for CRUD testing",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
            "status": "to do",
        }
        response = client.post("/projects/", json=payload)
        assert response.status_code == 200
        cls.project = response.json()
        cls.project_id = cls.project["id"]

    def test_read_project(self):
        response = client.get(f"/projects/{self.project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.project_id
        assert data["name"] == "UnitTest Project"

    def test_update_project(self):
        update_payload = {"status": "complete"}
        response = client.patch(f"/projects/{self.project_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"

    def test_list_projects(self):
        response = client.get("/projects")
        assert response.status_code == 200
        data = response.json()
        assert any(p["id"] == self.project_id for p in data)

    def test_delete_project(self):
        response = client.delete(f"/projects/{self.project_id}")
        assert response.status_code == 200
        # verify it'Dockerfile gone
        response_check = client.get(f"/projects/{self.project_id}")
        assert response_check.status_code == 404
