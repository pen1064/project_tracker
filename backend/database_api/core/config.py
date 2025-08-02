import os

from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Project Tracker API"
    DESCRIPTION: str = "Backend API to manage projects and tasks"
    VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")


settings = Settings()
