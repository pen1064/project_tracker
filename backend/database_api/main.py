import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.database_api.core.config import settings
from backend.database_api.db.connection import database
from backend.database_api.routers import projects, tasks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def create_app() -> FastAPI:
    """
        Factory function to create and configure the FastAPI app instance.
    """
    # Initialize DB
    database.init_db()

    app: FastAPI = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
    )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)},
        )
    """
    Returning the exception message as part of the JSON response can be
    helpful for language models (LLMs) or clients to understand what went wrong.
    """

    # Include routers
    app.include_router(projects.router)
    app.include_router(tasks.router)

    return app


app: FastAPI = create_app()
