from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from backend.database_api.enum.status import TaskStatus

# --- Input Schemas ---


class TaskCreate(BaseModel):
    title: str
    assigned_to: str
    status: TaskStatus
    due_date: datetime
    project_id: int

    @field_validator("assigned_to")
    @classmethod
    def normalize_assigned_to(cls, v):
        if v is not None:
            return v.lower()
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None

    @field_validator("assigned_to")
    @classmethod
    def normalize_assigned_to(cls, v):
        if v is not None:
            return v.lower()
        return v


# --- Output Schema ---


class Task(BaseModel):
    id: int
    title: str
    assigned_to: str
    status: TaskStatus
    due_date: datetime
    created_time: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
