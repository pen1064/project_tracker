from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from backend.database_api.enum.status import ProjectStatus
from backend.database_api.schemas.task import Task

# --- Input Schemas ---


class ProjectCreate(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: ProjectStatus


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ProjectStatus] = None


# --- Output Schema ---


class Project(BaseModel):
    id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: ProjectStatus
    created_time: datetime
    last_modified: datetime
    tasks: list[Task] = []
    model_config = ConfigDict(from_attributes=True)
