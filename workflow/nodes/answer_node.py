import logging

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState
from workflow.guardrail import filter_llm_output, sanitize_input

logger = logging.getLogger(__name__)


async def answer_node(state: AgentState, runtime: Runtime[AgentContext]) -> AgentState:
    """Generate final answer using gemini_answer MCP tool with guardrails."""
    logger.info("Answer question node.")
    try:
        answer_func = runtime.context.mcp_tools["gemini_answer"]
        result = await answer_func(
            question=sanitize_input(state.question),
            tool_result=state.tool_result,
            previous_node=state.previous_node,
        )
        state.final_answer = filter_llm_output(result["answer"])
        logger.debug(f"Final answer: {state.final_answer}")
    except Exception as e:
        logger.exception("Answer node error", exc_info=e)
        state.final_answer = ""
    state.previous_node: str = 'answer'
    return state
