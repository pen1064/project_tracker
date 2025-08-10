import json
import logging
from typing import Any, Callable, Awaitable

import traceback
from langgraph.runtime import Runtime
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def create_task_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Execute create_task MCP tool."""
    logger.info("Create task node.")
    try:
        tool_func: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["create_task"]
        params: dict[str, Any] = state.tool_input or {}
        logger.debug(f"create_task params: {params}")
        response: CallToolResult = await tool_func(**params)
        text: str = response.content[0].text
        result: dict[str, Any] = json.loads(text)
        if result["isError"] is True:
            raise RuntimeError(f'Create tasks returned an error: {result.get("error")}')
        state.tool_result = json.dumps(result, separators=(",", ":"))
        logger.info(f"result from create_task: {state.tool_result}")
    except Exception as e:
        logger.exception("Cannot create task", exc_info=e)
        tb_str = traceback.format_exc()
        state.tool_result = f"ERROR: Fail to create task because of {e}\n{tb_str}"

    state.previous_node: str = 'create_task'
    return state
