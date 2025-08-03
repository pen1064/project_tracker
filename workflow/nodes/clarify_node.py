import logging

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def clarify_node(state: AgentState, runtime: Runtime[AgentContext]) -> AgentState:
    """Ask the user for missing fields, using a clarification agent/tool if available."""
    logger.info("Clarify node: Asking for missing fields.")
    missing: list[str] = state.tool_input.get("missing_fields", [])
    question: str = state.tool_input.get("original_question", "")

    clarification_agent = runtime.context.mcp_tools["gemini_clarify"]
    if clarification_agent:
        result = await clarification_agent(
            missing_fields=missing,
            original_question=question,
        )
        clarification: str = result["clarification"]
        logger.info(f"Clarification Agent Result: {clarification}")
    else:
        clarification = f"Please provide the following missing fields to proceed with: {', '.join(missing)}."

    state.final_answer = clarification
    state.previous_node: str = 'clarify'
    return state
