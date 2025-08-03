import json
import logging
from typing import Any

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def create_task_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Execute create_task MCP tool."""
    logger.info("Create task node.")
    try:
        tool_func = runtime.context.mcp_tools["create_task"]
        params: dict[str, Any] = state.tool_input or {}
        logger.debug(f"create_task params: {params}")
        result = await tool_func(**params)
        state.tool_result = json.dumps(result, separators=(",", ":"))
        logger.info(f"result from create_task: {state.tool_result}")
    except Exception as e:
        logger.exception("Cannot create task", exc_info=e)
        state.tool_result = f"ERROR: Fail to create task because of {e}"

    state.previous_node: str = 'create_task'
    return state
