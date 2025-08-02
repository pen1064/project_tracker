from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database_api.db.connection import database


class Project(database.Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False, default=func.now())
    last_modified = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    tasks = relationship("Task", back_populates="project", cascade="all, delete")


class Task(database.Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    assigned_to = Column(String, nullable=False)
    status = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_time = Column(DateTime, nullable=False, default=func.now())
    last_modified = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    project = relationship("Project", back_populates="tasks")
