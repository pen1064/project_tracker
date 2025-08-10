import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database_api.db.connection import database
from backend.database_api.db.repositories.project_repository import ProjectRepository
from backend.database_api.enum.status import ProjectStatus
from backend.database_api.schemas.project import Project, ProjectCreate, ProjectUpdate
from backend.database_api.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: Session = Depends(database.get_db)) -> ProjectService:
    repo = ProjectRepository(db)
    return ProjectService(repo)


@router.post("/", response_model=Project)
def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    """
        Endpoint to create a new Project.
    """
    logging.info(f"Creating project with data: {project}")
    try:
        new_project = service.create(project=project)
        return new_project
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Database constraint error while creating project",
                "db_error": str(getattr(e.orig, "diag", None)) or str(e.orig) or str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unexpected error while creating project",
                "error": str(e)
            }
        )

@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    """
        Endpoint to retrieve a project by its ID
    """
    logging.info(f"Reading project with id={project_id}")
    project_obj = service.get(project_id=project_id)
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_obj


@router.get("/", response_model=list[Project])
def get_projects(
    name: Optional[str] = None,
    status: Optional[ProjectStatus] = None,
    service: ProjectService = Depends(get_project_service),
):
    """
        Endpoint to list projects filtered by optional query parameters.
    """
    logging.info("List all Projects")
    return service.list(name=name, status=status)


@router.patch("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    """
        Endpoint to update an existing project partially.
    """
    logging.info(f"Updating project id={project_id} with data: {project_update}")
    updated = service.update(project_id=project_id, project_update=project_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", response_model=Project)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    """
       Endpoint to delete a project by its ID.
    """
    logging.info(f"Deleting project id={project_id}")
    deleted = service.delete(project_id=project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted
