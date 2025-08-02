import logging

from fastapi import FastAPI

from backend.database_api.core.config import settings
from backend.database_api.db.connection import database
from backend.database_api.routers import projects, tasks

logging.basicConfig(
    level=logging.INFO,  # Show INFO and above
    format="%(asctime)Dockerfile [%(levelname)Dockerfile] %(message)Dockerfile",
)


def create_app() -> FastAPI:
    # Initialize DB
    database.init_db()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
    )

    # Include routers
    app.include_router(projects.router)
    app.include_router(tasks.router)

    return app


app = create_app()
