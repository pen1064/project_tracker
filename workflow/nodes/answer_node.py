import logging
import json
from typing import Any, Callable, Awaitable
from langgraph.runtime import Runtime
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState
from workflow.guardrail import filter_llm_output, sanitize_input
from workflow.utils import json_parse

logger = logging.getLogger(__name__)

async def answer_node(state: AgentState, runtime: Runtime[AgentContext]) -> AgentState:
    """Generate final answer using gemini_answer MCP tool with guardrails."""
    logger.info("Answer question node.")

    if getattr(state, "error", None) and not state.final_answer:
        msg = state.error.get("message") if isinstance(state.error, dict) else None
        state.final_answer = f"{msg}" if msg else "An error occurred."
        return state

    try:
        answer_func: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["gemini_answer"]
        response: CallToolResult = await answer_func(
            question=sanitize_input(state.question),
            tool_result=state.tool_result,
            previous_node=state.previous_node,
        )
        logger.info('----------ANSWER---------')
        logger.info(response)

        text: str = response.content[0].text
        result: dict[str, Any] = json.loads(text)

        if result.get("isError"):
            raise RuntimeError(result.get("error"))

        state.final_answer = filter_llm_output(result.get("answer", "")) or "I don't have an answer."
        logger.debug("Final answer: %s", state.final_answer)

    except Exception as e:
        logger.exception("Answer node error")

        payload = e.args[0] if e.args else str(e)
        parsed = json_parse(payload)

        code = None
        if isinstance(parsed, dict):
            code = parsed.get("error", {}).get("code") or parsed.get("code")

        if code == 429:
            state.final_answer = (
                "The system is currently at capacity (rate limit). "
                "Please try again in about a minute."
            )
        else:
            state.final_answer = f"Sorry, I couldn't generate a response due to an internal error {e}."

    state.previous_node = "answer"
    return state
