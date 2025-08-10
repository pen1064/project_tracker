import json
import logging
from typing import Any, Optional, Callable, Awaitable

from langgraph.runtime import Runtime
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

logger = logging.getLogger(__name__)


async def clarify_node(state: AgentState, runtime: Runtime[AgentContext]) -> AgentState:
    """
    Clarify node that:
      - If in *duplicate-confirm* flow, ONLY displays the prompt and ends the turn.
        (No yes/no handling here — plan_node will handle that on the next turn.)
      - Otherwise, uses 'gemini_clarify' to ask for general missing fields.
    """
    logger.info("Clarify node: Asking for any missing fields.")

    ti: dict[str, Any] = state.tool_input or {}
    missing_fields_raw = ti.get("missing_fields") or []
    if not isinstance(missing_fields_raw, list):
        try:
            missing_fields: list[str] = list(missing_fields_raw)
        except Exception:
            missing_fields = []
    else:
        missing_fields = missing_fields_raw

    # ---------- DUPLICATE-CONFIRM DISPLAY-ONLY ----------
    if "confirm_duplicate" in missing_fields:
        logger.info("Clarify node: Asking for confirming duplicate.")
        prompt = ti.get("clarify_prompt") or "Found a possible duplicate. Create anyway? (yes/no)"
        if not isinstance(getattr(state, "slots", None), dict):
            state.slots = {}
        state.slots["awaiting_confirm_duplicate"] = True

        state.final_answer = prompt
        state.used_tool_name = "final_answer"
        state.previous_node = "clarify"
        return state

    # ---------- DEFAULT: GENERAL CLARIFICATION VIA MCP TOOL ----------
    original_question: str = ti.get("original_question", state.question or "")
    try:
        logger.info("Clarify node: Asking users to provide missing fields.")
        clarifier: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["gemini_clarify"]
        if clarifier is None:
            # Fallback message if tool not available
            msg = (
                "Please provide the following missing fields to proceed: "
                + (", ".join(missing_fields) if missing_fields else "(none detected)")
            )
            state.final_answer = msg
            state.used_tool_name = "final_answer"
            state.previous_node = "clarify"
            return state

        response: CallToolResult = await clarifier(
            missing_fields=missing_fields,
            original_question=original_question,
        )

        txt: str = response.content[0].text
        data: dict[str, Any] = json.loads(txt)
        logger.info("----------CLARIFY-------------")
        logger.info(data)
        if data.get("isError"):
            raise RuntimeError(data.get("error", "Unknown clarifier error"))
        clarification: Optional[str] = data.get("clarification")
        if not clarification:
            clarification = (
                "Please provide the following missing fields to proceed: "
                + (", ".join(missing_fields) if missing_fields else "(none detected)")
            )

        state.final_answer = clarification
        state.used_tool_name = "final_answer"
        state.previous_node = "clarify"
        return state

    except Exception as e:
        logger.exception("Error during clarify_node", exc_info=e)
        state.tool_result = f"ERROR: Clarification failed due to {e}"
        state.final_answer = (
            "I could not run the clarifier. "
            "Please provide: " + (", ".join(missing_fields) if missing_fields else "(details)")
        )
        state.used_tool_name = "final_answer"
        state.previous_node = "clarify"
        return state
