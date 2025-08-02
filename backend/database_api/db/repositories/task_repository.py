from typing import Optional

from sqlalchemy.orm import Session, joinedload

from backend.database_api.db.models import Project, Task
from backend.database_api.enum.status import TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: dict) -> Task:
        db_task = Task(**obj_in)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def update(self, db_task: Task, obj_in: dict) -> Task:
        for key, value in obj_in.items():
            setattr(db_task, key, value)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete(self, db_task: Task) -> None:
        self.db.delete(db_task)
        self.db.commit()

    def list(
        self,
        project_id: Optional[int] = None,
        project_name: Optional[str] = None,
        assigned_to: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        title: Optional[str] = None,
    ) -> list[Task]:
        query = self.db.query(Task).options(joinedload(Task.project))
        if project_id is not None:
            query = query.filter(Task.project_id == project_id)
        if project_name is not None:
            query = query.join(Task.project).filter(
                Project.name.ilike(f"%{project_name}%")
            )
        if assigned_to is not None:
            query = query.filter(Task.assigned_to.ilike(f"%{assigned_to}%"))
        if status is not None:
            query = query.filter(Task.status == status)
        if title is not None:
            query = query.filter(Task.title.ilike(f"%{title}%"))
        return query.all()
