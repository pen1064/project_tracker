from enum import Enum


class TaskStatus(str, Enum):
    TO_DO = "to do"
    IN_PROGRESS = "in progress"
    PENDING_APPROVAL = "pending approval"
    BLOCK = "block"
    COMPLETE = "complete"


class ProjectStatus(str, Enum):
    TO_DO = "to do"
    IN_PROGRESS = "in progress"
    PENDING_APPROVAL = "pending approval"
    BLOCK = "block"
    COMPLETE = "complete"
