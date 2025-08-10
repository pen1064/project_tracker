import json
import logging
from typing import Any, Callable, Awaitable

import traceback
from langgraph.runtime import Runtime
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def query_projects_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Execute query_projects MCP tool."""
    logger.info("Query projects node.")
    try:
        tool_func: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["query_projects"]
        params: dict[str, Any] = state.tool_input or {}
        logger.info(f"query_projects params: {params}")
        response: CallToolResult = await tool_func(**params)
        text: str = response.content[0].text
        result: dict[str, Any] = json.loads(text)
        logger.debug(f'Result for query_projects_node: {result}')
        if result["isError"] is True:
            raise RuntimeError(f'Query projects returned an error: {result.get("error")}')
        state.tool_result = json.dumps(result["projects"], separators=(",", ":"))
        logger.info(f"result from query_projects {state.tool_result}")
    except Exception as e:
        logger.exception("Cannot query projects", exc_info=e)
        tb_str = traceback.format_exc()
        state.tool_result = f"ERROR: Fail to query projects because of {e}\n{tb_str}"

    state.previous_node: str = 'query_projects'
    return state
