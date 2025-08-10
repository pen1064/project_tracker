import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database_api.db.connection import database
from backend.database_api.db.repositories.task_repository import TaskRepository
from backend.database_api.enum.status import TaskStatus
from backend.database_api.schemas.task import Task, TaskCreate, TaskUpdate
from backend.database_api.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(database.get_db)) -> TaskService:
    repo = TaskRepository(db)
    return TaskService(repo)


@router.post("/", response_model=Task)
def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    """
        Endpoint to create a new task.
    """
    logging.info(f"Creating task with data: {task}")
    try:
        return service.create(task=task)
    except IntegrityError as e:
        logging.exception("Integrity error while creating task")
        # Try to extract the DB detail safely
        raw = getattr(e, "orig", e)
        diag = getattr(raw, "diag", None)
        db_error = str(diag) if diag else str(raw)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Database constraint error while creating task, project does not exist",
                "db_error": db_error,
            },
        )
    except Exception as e:
        logging.exception("Unexpected error while creating task")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unexpected error while creating task",
                "error": str(e),
            },
        )


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """
        Endpoint to retrieve a task by its ID.
    """
    task_obj = service.get(task_id=task_id)
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj


@router.get("/", response_model=list[Task])
def list_tasks(
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    title: Optional[str] = None,
    service: TaskService = Depends(get_task_service),
):
    """
        Endpoint to list tasks with optional filters.
    """
    logging.info(
        f"GET: Tasks assigned to {assigned_to} with status {status} for project_id {project_id}/ "
        f"project_name {project_name}"
    )
    return service.list(
        project_id=project_id,
        project_name=project_name,
        assigned_to=assigned_to,
        status=status,
        title=title,
    )


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """
       Endpoint to partially update a task.
    """
    updated = service.update(task_id=task_id, task_update=task_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", response_model=Task)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """
        Endpoint to delete a task by ID.
    """
    deleted = service.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted
