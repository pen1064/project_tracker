from fastapi.testclient import TestClient

from backend.database_api.main import app

client = TestClient(app)


class TestTasksFastAPI:
    @classmethod
    def setup_class(cls):
        # Create a project first
        payload = {
            "name": "UnitTest Task Project",
            "description": "Project for task testing",
            "start_date": "2025-08-04",
            "end_date": "2025-08-15",
            "status": "in progress",
        }
        response = client.post("/projects/", json=payload)
        assert response.status_code == 200
        cls.project = response.json()
        cls.project_id = cls.project["id"]

        # Create a task for this project
        task_payload = {
            "title": "Test Task",
            "assigned_to": "Penelope",
            "status": "in progress",
            "due_date": "2025-08-10",
            "project_id": cls.project_id,
        }
        response = client.post("/tasks", json=task_payload)
        assert response.status_code == 200
        cls.task = response.json()
        cls.task_id = cls.task["id"]

    def test_read_task(self):
        response = client.get(f"/tasks/{self.task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.task_id
        assert data["assigned_to"] == "penelope"

    def test_update_task(self):
        update_payload = {"status": "complete"}
        response = client.patch(f"/tasks/{self.task_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"

    def test_list_tasks(self):
        response = client.get(f"/tasks?project_id={self.project_id}")
        assert response.status_code == 200
        data = response.json()
        assert any(t["id"] == self.task_id for t in data)

    def test_delete_task(self):
        response = client.delete(f"/tasks/{self.task_id}")
        assert response.status_code == 200
        # verify it'Dockerfile gone
        response = client.get(f"/tasks/{self.task_id}")
        assert response.status_code == 404

    @classmethod
    def teardown_class(cls):
        # Clean up: delete project
        client.delete(f"/projects/{cls.project_id}")
