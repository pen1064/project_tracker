import logging
from typing import Any

from fastapi import FastAPI, HTTPException

from workflow.workflow_class import UserMessage
from workflow.api.chatbot import lifespan, process_chat

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(lifespan=lifespan)


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat_endpoint(payload: UserMessage) -> dict[str, Any]:
    """
    Chat endpoint.
    """
    try:
        return await process_chat(payload)
    except Exception as e:
        logger.exception("Chat endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))
