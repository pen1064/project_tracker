import json
import logging

from langgraph.runtime import Runtime
from typing import Any, Callable, Awaitable
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def check_task_exists_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Call query_tasks MCP tool with project_id and title to check for duplicates."""
    logger.info("Check if task already exists.")
    try:
        tool_func: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["query_tasks"]
        project_id_to_query: str = state.tool_input.get("project_id")
        task_title_to_query: str = state.tool_input.get("title")
        params = {
            "project_id": project_id_to_query,
            "title": task_title_to_query,
        }
        logger.info(f"check_task_exists params: {params}")
        response: CallToolResult = await tool_func(**params)
        text: str = response.content[0].text
        result: dict[str, Any] = json.loads(text)

        logger.debug(f'Result in check task exist node: {result}')
        if result["isError"] is True:
            raise RuntimeError(f'Query tasks returned an error: {result.get("error")}')
        state.tool_result = json.dumps(result["tasks"], separators=(",", ":"))
        logger.info(f"Result from check_task_exists: {state.tool_result}")
    except Exception as e:
        logger.exception("Error during check_task_exists", exc_info=e)
        state.tool_result = "[]"
    state.previous_node: str = 'check_task_exists'
    return state
