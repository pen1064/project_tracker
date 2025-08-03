import pytest

from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from backend.database_api.main import app

# Initialize TestClient for testing FastAPI endpoints
client = TestClient(app)


class TestTasksFastAPI:
    @classmethod
    def setup_class(cls):
        """
        Setup method that runs once before all tests in this class.
        It creates a project and a task linked to that project,
        which will be used in the subsequent tests.
        """
        # Create a project to associate tasks with
        payload = {
            "name": "UnitTest Task Project",
            "description": "Project for task testing",
            "start_date": "2025-08-04",
            "end_date": "2025-08-15",
            "status": "in progress",
        }
        response = client.post("/projects/", json=payload)
        # Ensure project creation succeeded
        assert response.status_code == 200
        cls.project = response.json()
        cls.project_id = cls.project["id"]

        # Create a task linked to the newly created project
        task_payload = {
            "title": "Test Task",
            "assigned_to": "Penelope",
            "status": "in progress",
            "due_date": "2025-08-10",
            "project_id": cls.project_id,
        }
        response = client.post("/tasks", json=task_payload)
        # Ensure task creation succeeded
        assert response.status_code == 200
        cls.task = response.json()
        cls.task_id = cls.task["id"]

    def test_create_task_for_invalid_project_raises(self):
        """
        Test creating a task with a non-existent project_id.
        This should raise an IntegrityError due to foreign key constraint violation.
        """
        task_payload = {
            "title": "Test Task",
            "assigned_to": "Penelope",
            "status": "in progress",
            "due_date": "2025-08-10",
            "project_id": 999999999,
        }
        # Expect an IntegrityError to be raised by the database layer
        with pytest.raises(IntegrityError):
            client.post("/tasks", json=task_payload)

    def test_read_task(self):
        """
        Test retrieving the task by its ID.
        Verifies the task exists and the assigned_to field matches (case-insensitive).
        """
        response = client.get(f"/tasks/{self.task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.task_id
        # API might lowercase names, so compare lowercase
        assert data["assigned_to"].lower() == "penelope"

    def test_read_task_does_not_exist(self):
        """
        Test retrieving a task with a non-existent ID.
        Verifies the API returns 404 with proper error detail.
        """
        response = client.get(f"/tasks/{self.task_id + 9999}") # Use a high number to avoid collision
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Task not found"

    def test_update_task(self):
        """
        Test updating the task's status field.
        Sends a PATCH request to update, then a GET request to verify the status is updated.
        """
        update_payload = {"status": "complete"}
        response = client.patch(f"/tasks/{self.task_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()

        response_post_patch = client.get(f"/tasks/{self.task_id}")
        data_post_patch = response_post_patch.json()
        assert data_post_patch["status"] == "complete"

    def test_list_tasks(self):
        """
        Test listing tasks filtered by the project ID.
        Verifies that the task created in setup appears in the list.
        """
        response = client.get(f"/tasks?project_id={self.project_id}")
        assert response.status_code == 200
        data = response.json()
        assert any(t["id"] == self.task_id for t in data)

    def test_delete_task(self):
        """
        Test deleting the task by its ID.
        Verifies the task is deleted and cannot be retrieved afterwards.
        """
        response = client.delete(f"/tasks/{self.task_id}")
        assert response.status_code == 200
        # Verify deletion by attempting to fetch the task
        response = client.get(f"/tasks/{self.task_id}")
        assert response.status_code == 404

    @classmethod
    def teardown_class(cls):
        """
        Cleanup method run after all tests in this class complete.
        Deletes the project created in setup to keep test environment clean.
        """
        client.delete(f"/projects/{cls.project_id}")
