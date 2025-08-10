from pydantic import BaseModel
from typing import Optional, Any


class UserMessage(BaseModel):
    user_id: str
    message: str
    state: Optional[dict[str, Any]] = None
