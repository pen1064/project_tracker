import logging
import json
from typing import Any, Callable, Awaitable

import traceback
from langgraph.runtime import Runtime
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState
from workflow.guardrail import sanitize_input


logger = logging.getLogger(__name__)

async def plan_node(state: AgentState, runtime: Runtime[AgentContext]) -> AgentState:
    """
    Flow:
      1) If preprocess already routed (_skip_plan_node), short-circuit.
      2) Call gemini_planner to determine tool_name and parameters.
      3) If create_* missing fields, send to gemini_clarify (stash partial payload).
      4) Else set used_tool_name / intent / tool_input and continue.
    """

    logger.info("User intention identification and plan node.")
    logger.debug("state: %r", state)

    # ---------- 1) Short-circuit if preprocess already decided a route ----------
    utn = getattr(state, "used_tool_name", None)
    if isinstance(utn, str) and utn:
        if utn.endswith("_skip_plan_node"):
            logger.info("Plan node: short-circuit due to preprocess routing (%s).", utn)
            state.previous_node = "plan"
            return state
        if utn == "final_answer_skip_plan_node":
            logger.info("Plan node: short-circuit returning final answer.")
            state.used_tool_name = "final_answer"
            state.previous_node = "plan"
            return state

    # ---------- Normalize containers ----------
    if not isinstance(getattr(state, "slots", None), dict):
        state.slots = {}
    ti: dict[str, Any] = state.tool_input or {}
    if not isinstance(ti, dict):
        try:
            ti = dict(ti)
        except Exception:
            ti = {}

    # ---------- 2) Compute plan via planner ----------
    try:
        user_prompt: str = sanitize_input(state.question)
        logger.info("Sanitized question for planner_func: %s", user_prompt)

        planner: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["gemini_planner"]
        response: CallToolResult = await planner(question=user_prompt)

        text: str = response.content[0].text if getattr(response, "content", None) else "{}"
        result: dict[str, Any] = json.loads(text or "{}")
        logger.info('-----------PLAN NODE-----------------')
        logger.info(result)

    except Exception as e:
        logger.exception("Cannot parse plan response", exc_info=e)
        state.used_tool_name = "final_answer"
        state.tool_input = {}
        tb_str: str = traceback.format_exc()
        state.tool_result: str = (
            f"ERROR: Fail to process user's request because of {e}. Details of the error can be found here: {tb_str}"
        )
        state.previous_node = "plan"
        return state

    # ---------- 3) Interpret plan ----------
    try:
        plan = result["plan"]
        tool_name = plan["tool_name"]
        params: dict[str, Any] = plan["parameters"]
        logger.info("Planner chose tool: %s", tool_name)

        # Handle "create_* but missing fields" → gemini_clarify + stash partial payload
        if tool_name == "create_project":
            required = ["name", "description", "start_date", "end_date", "status"]
            miss = [k for k in required if not params.get(k)]
            if miss:
                state.used_tool_name = "gemini_clarify"
                state.tool_input = {
                    "missing_fields": miss,
                    "original_question": state.question,
                    "proposed_intent": "create_project",
                    "proposed_tool_input": params,  # stash partial payload
                }
                state.previous_node = "plan"
                logger.info("Planner missing fields for create_project; asking for: %s", miss)
                return state

        elif tool_name == "create_task":
            required = ["title", "assigned_to", "project_id", "due_date", "status"]
            miss = [k for k in required if not params.get(k)]
            if miss:
                state.used_tool_name = "gemini_clarify"
                state.tool_input = {
                    "missing_fields": miss,
                    "original_question": state.question,
                    "proposed_intent": "create_task",
                    "proposed_tool_input": params,  # stash partial payload
                }
                state.previous_node = "plan"
                logger.info("Planner missing fields for create_task; asking for: %s", miss)
                return state

        # ---------- 4) Standard routing ----------
        state.used_tool_name = tool_name
        if state.used_tool_name == "final_answer":
            state.tool_result = params.get("tool_result", "")
        else:
            if state.used_tool_name != "gemini_clarify":
                state.intent = tool_name
            state.tool_input = params

    except Exception as e:
        logger.exception("Error interpreting planner result", exc_info=e)
        state.tool_input = {}
        tb_str: str = traceback.format_exc()
        state.tool_result: str = (
            f"ERROR: Fail to determine tool or any missing attributes to continue process the request becasue of {e}. "
            f"Details of the error can be found here: {tb_str} \n User should rephrase question."
        )
    state.previous_node = "plan"
    return state
