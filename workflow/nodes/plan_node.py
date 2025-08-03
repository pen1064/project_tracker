import logging
from typing import Any

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState
from workflow.guardrail import sanitize_input
from workflow.utils import find_missing_fields

logger = logging.getLogger(__name__)


async def plan_node(state: AgentState, runtime: Runtime[AgentContext]) -> AgentState:
    """
    Uses the gemini_planner MCP tool to determine which tool to run and with what parameters.
    If anything fails, falls back to setting used_tool_name=None and a default tool_result.
    """
    logger.info("User intention identification and plan node.")
    try:
        user_prompt: str = sanitize_input(state.question)
        logger.info(f"Sanitized question for planner_func: {user_prompt}")

        planner_func = runtime.context.mcp_tools["gemini_planner"]
        result: dict[str, Any] = await planner_func(question=user_prompt)
        logger.debug(f"Raw planner result: {result}")
        plan = result["plan"]
        state.used_tool_name = plan["tool_name"]

        if state.used_tool_name == "final_answer":
            state.tool_result = plan["parameters"]["tool_result"]
        else:
            if state.used_tool_name != "gemini_clarify":
                state.intent = plan["tool_name"]
            state.tool_input = plan["parameters"]

    except Exception as e:
        logger.exception("Cannot parse plan response", exc_info=e)

        if state.used_tool_name == "create_project":
            required = ["name", "description", "start_date", "end_date", "status"]
            missing = find_missing_fields(required, state.tool_input)
            if missing:
                state.used_tool_name = "gemini_clarify"
                state.tool_input = {
                    "missing_fields": missing,
                    "original_question": state.question,
                }
        elif state.used_tool_name == "create_task":
            required = ["title", "assigned_to", "project_id", "due_date", "status"]
            missing = find_missing_fields(required, state.tool_input)
            if missing:
                state.used_tool_name = "gemini_clarify"
                state.tool_input = {
                    "missing_fields": missing,
                    "original_question": state.question,
                }
        elif state.used_tool_name is None:
            state.tool_input = {}
            state.tool_result = (
                "summary: Cannot determine tools, no result. User should rephrase question."
            )

    state.previous_node: str = 'plan'
    return state
