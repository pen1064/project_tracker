from typing import Optional

from backend.database_api.core.cache import global_cache
from backend.database_api.db.models import Project
from backend.database_api.db.repositories.project_repository import ProjectRepository
from backend.database_api.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """
    Service layer class responsible for logic related to Projects.
    It uses ProjectRepository for database interactions and global_cache for caching.
    """
    def __init__(self, repo: ProjectRepository):
        self.repo = repo

    def create(self, project: ProjectCreate) -> Project:
        db_project = self.repo.create(project.model_dump())
        return db_project

    def get(self, project_id: int) -> Optional[Project]:
        key = f"project:{project_id}"

        def _fetch():
            return self.repo.get(project_id)

        return self._cached(key, _fetch)

    def update(
        self, project_id: int, project_update: ProjectUpdate
    ) -> Optional[Project]:
        db_project = self.repo.get(project_id)
        if not db_project:
            return None
        db_project = self.repo.update(
            db_project, project_update.model_dump(exclude_unset=True)
        )
        global_cache.delete(f"project:{project_id}")
        return db_project

    def delete(self, project_id: int) -> Optional[Project]:
        db_project = self.repo.get(project_id)
        if not db_project:
            return None
        self.repo.delete(db_project)
        global_cache.delete(f"project:{project_id}")
        return db_project

    def list(
        self, name: Optional[str] = None, status: Optional[str] = None
    ) -> list[Project]:
        return self.repo.list(name=name, status=status)

    def _cached(self, key: str, fetch_fn) -> Optional[Project]:
        cached = global_cache.get(key)
        if cached is not None:
            return cached
        value = fetch_fn()
        global_cache.set(key, value)
        return value
