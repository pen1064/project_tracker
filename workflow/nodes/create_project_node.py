import json
import logging
from typing import Any

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def create_project_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Execute create_project MCP tool."""
    logger.info("Create project node.")
    try:
        tool_func = runtime.context.mcp_tools["create_project"]
        params: dict[str, Any] = state.tool_input or {}
        logger.debug(f"create_project params: {params}")
        result = await tool_func(**params)
        state.tool_result = json.dumps(result, separators=(",", ":"))
        logger.info(f"result from create_project: {state.tool_result}")
    except Exception as e:
        logger.exception("Cannot create project", exc_info=e)
        state.tool_result = f"ERROR: Fail to create project because of error {e}"
    state.previous_node: str = 'create_project'
    return state
