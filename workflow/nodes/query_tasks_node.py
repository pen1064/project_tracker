import json
import logging
from typing import Any, Union

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def query_tasks_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Execute query_tasks MCP tool."""
    logger.info("Query tasks node.")
    try:
        tool_func = runtime.context.mcp_tools["query_tasks"]
        params: dict[str, Any] = state.tool_input or {}
        logger.info(f"query_tasks params: {params}")
        result = await tool_func(**params)
        logger.debug(f'Result for query_tasks_node: {result}')
        if result["isError"] is True:
            raise RuntimeError(f'Query tasks returned an error: {result.get("error")}')
        state.tool_result = json.dumps(result["tasks"], separators=(",", ":"))

        logger.info(f"result from query_tasks {state.tool_result}")
    except Exception as e:
        logger.exception("Cannot query tasks", exc_info=e)
        # Use safe access to error message if present
        error_message = (
            result["error"] if "result" in locals() and "error" in result else str(e)
        )
        state.tool_result = f"ERROR: Fail to query tasks because {error_message}"

    # update previous node
    state.previous_node: str = 'query_tasks'
    return state
