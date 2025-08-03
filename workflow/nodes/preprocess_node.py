import logging

from workflow.agent_state import AgentState
from workflow.utils import trim_question_history

logger = logging.getLogger(__name__)


async def preprocess_node(state: AgentState) -> AgentState:
    """Ensure question history exists and trim it."""
    history: list[str] = state.slots.get("question_history", [])
    if not history:
        question = state["messages"][-1].content
        state.slots.setdefault("question_history", []).append(question)
    trim_question_history(state)

    state.previous_node: str = 'preprocess'
    return state
