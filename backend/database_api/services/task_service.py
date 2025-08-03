from typing import Optional

from backend.database_api.core.cache import global_cache
from backend.database_api.db.models import Task
from backend.database_api.db.repositories.task_repository import TaskRepository
from backend.database_api.enum.status import TaskStatus
from backend.database_api.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """
    Service layer class responsible for logic related to Tasks.
    It uses TaskRepository for database interactions and global_cache for caching.
    """
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def create(self, task: TaskCreate) -> Task:
        db_task = self.repo.create({**task.model_dump()})
        return db_task

    def get(self, task_id: int) -> Optional[Task]:
        key = f"task:{task_id}"

        def _fetch():
            return self.repo.get(task_id)

        return self._cached(key, _fetch)

    def update(self, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        db_task = self.repo.get(task_id)
        if not db_task:
            return None
        db_task = self.repo.update(db_task, task_update.model_dump(exclude_unset=True))
        global_cache.delete(f"task:{task_id}")
        return db_task

    def delete(self, task_id: int) -> Optional[Task]:
        db_task = self.repo.get(task_id)
        if not db_task:
            return None
        self.repo.delete(db_task)
        global_cache.delete(f"task:{task_id}")
        return db_task

    def list(
        self,
        project_id: Optional[int] = None,
        project_name: Optional[str] = None,
        assigned_to: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        title: Optional[str] = None,
    ) -> list[Task]:
        return self.repo.list(
            project_id=project_id,
            project_name=project_name,
            assigned_to=assigned_to,
            status=status,
            title=title,
        )

    def _cached(self, key: str, fetch_fn) -> Optional[Task]:
        cached = global_cache.get(key)
        if cached is not None:
            return cached
        value = fetch_fn()
        global_cache.set(key, value)
        return value
