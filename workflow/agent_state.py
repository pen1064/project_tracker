from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Conversation state for an agent."""

    question: str = ""
    slots: dict[str, Any] = Field(default_factory=dict)
    messages: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    previous_node: Optional[str] = None
    tool_input: Optional[dict] = None
    tool_result: Optional[str] = None
    final_answer: Optional[str] = None
    intent: Optional[str] = None
    used_tool_name: Optional[str] = None
    user_id: str = None
    thread_id: str = None
