from fastapi.testclient import TestClient

from backend.database_api.main import app

# Initialize the TestClient with the FastAPI app
client = TestClient(app)


class TestProjectsFastAPI:
    @classmethod
    def setup_class(cls):
        """
        Setup method to create a new project before running tests.
        This project will be used for CRUD operations in the tests below.
        """
        payload = {
            "name": "UnitTest Project",
            "description": "Project for CRUD testing",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
            "status": "to do",
        }
        # Create a new project via POST request
        response = client.post("/projects/", json=payload)
        # Assert the creation was successful
        assert response.status_code == 200
        # Store the created project data and ID for use in tests
        cls.project = response.json()
        cls.project_id = cls.project["id"]

    def test_read_project(self):
        """
        Test retrieving a single project by ID.
        Verifies that the returned project matches the created one.
        """
        response = client.get(f"/projects/{self.project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.project_id
        assert data["name"] == "UnitTest Project"

    def test_read_project_does_not_exist(self):
        """
        Test retrieving a project by an ID that does not exist.
        Verifies that a 404 status code and proper error message is returned.
        """
        non_existent_id = self.project_id + 9999  # Use a high number to avoid collision
        response = client.get(f"/projects/{non_existent_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Project not found"

    def test_update_project_end_date(self):
        """
        Test updating the project's end_date field.
        Sends a PATCH request to update, then a GET request to verify the end_date is updated.
        Note: The API adds a time suffix "T00:00:00" by default for date fields.
        """
        update_payload = {"end_date": "2025-09-01"}
        response = client.patch(f"/projects/{self.project_id}", json=update_payload)
        assert response.status_code == 200

        response_post_patch_end_date = client.get(f"/projects/{self.project_id}")
        response_post_patch_end_date = response_post_patch_end_date.json()
        assert response_post_patch_end_date["end_date"] == "2025-09-01T00:00:00"

    def test_update_project_status(self):
        """
        Test updating the project's status field.
        Sends a PATCH request to update, then a GET request to verify the status is updated.
        """
        update_payload = {"status": "complete"}
        response = client.patch(f"/projects/{self.project_id}", json=update_payload)
        assert response.status_code == 200

        response_post_patch_status = client.get(f"/projects/{self.project_id}")
        response_post_patch_status = response_post_patch_status.json()
        assert response_post_patch_status["status"] == "complete"

    def test_list_projects(self):
        """
        Test listing all projects.
        Verifies that the created project is present in the returned list.
        """
        response = client.get("/projects")
        assert response.status_code == 200
        data = response.json()
        # Check if the created project ID is in the list of projects
        assert any(p["id"] == self.project_id for p in data)

    def test_delete_project(self):
        """
        Test deleting the created project.
        Verifies the project is removed and cannot be retrieved afterwards.
        """
        response = client.delete(f"/projects/{self.project_id}")
        assert response.status_code == 200
        # Verify the project no longer exists by attempting to GET it
        response_check = client.get(f"/projects/{self.project_id}")
        assert response_check.status_code == 404
