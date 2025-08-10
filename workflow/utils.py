import logging

import json
from typing import Any, Awaitable
from workflow.agent_state import AgentState

MAX_HISTORY: int = 4

logger = logging.getLogger(__name__)


def trim_question_history(state: AgentState) -> None:
    """
    Trim question history to a maximum number of entries
    and update state.question with the joined history.
    """
    logger.info('Trim question history')
    history: list[str] = state.slots.get("question_history", [])

    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        state.slots["question_history"] = history
    state.question = " ".join(history)


def json_parse(response: Any) -> Any:
    """
    Attempt to parse a JSON string.
    If the input is already a dict/list, return it unchanged.
    If parsing fails, return the original input.
    """
    if isinstance(response, (dict, list)):
        return response
    if isinstance(response, str):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response
    return response


async def with_error(state, node_name: str, coro: Awaitable):
    """
    Run a node's logic safely. If an exception occurs, mark the state as errored
    and short-circuit to final_answer by setting used_tool_name.
    """
    try:
        return await coro
    except Exception as e:
        logger.exception("%s node failed", node_name)
        try:
            state.error = {
                "code": "NODE_ERROR",
                "message": str(e),
                "node": node_name,
            }
        except Exception:
            pass
        state.used_tool_name = "final_answer"
        state.final_answer = state.final_answer or (
            "Sorry — something went wrong while processing your request."
        )
        return state