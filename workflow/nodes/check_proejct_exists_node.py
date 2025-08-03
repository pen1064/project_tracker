import json
import logging

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def check_project_exists_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """Call query_projects MCP tool with project_name to check for duplicates."""
    logger.info("Check if project already exists.")
    try:
        tool_func = runtime.context.mcp_tools["query_projects"]
        project_name_to_query: str = state.tool_input.get("name")
        params = {"name": project_name_to_query}
        logger.debug(f"check_project_exists params: {params}")
        result = await tool_func(**params)
        if result["isError"] is True:
            raise RuntimeError(f'Query tasks returned an error: {result.get("error")}')
        state.tool_result = json.dumps(result["projects"], separators=(",", ":"))
        logger.info(f"Result from check_project_exists: {state.tool_result}")
    except Exception as e:
        logger.exception("Error during check_project_exists", exc_info=e)
        state.tool_result = "[]"
    state.previous_node: str = 'check_project_exists'
    return state
