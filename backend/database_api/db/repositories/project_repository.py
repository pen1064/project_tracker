from sqlalchemy.orm import Session

from backend.database_api.db.models import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: dict) -> Project:
        db_project = Project(**obj_in)
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def get(self, project_id: int) -> Project:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def update(self, db_project: Project, obj_in: dict) -> Project:
        for key, value in obj_in.items():
            setattr(db_project, key, value)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete(self, db_project: Project) -> None:
        self.db.delete(db_project)
        self.db.commit()

    def list(self, name: str = None, status: str = None) -> list[Project]:
        query = self.db.query(Project)
        if name:
            query = query.filter(Project.name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Project.status == status)
        return query.all()
