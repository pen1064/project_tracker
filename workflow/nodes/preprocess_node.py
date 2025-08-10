import logging
from typing import Any, Optional

from workflow.agent_state import AgentState
from workflow.utils import trim_question_history

logger = logging.getLogger(__name__)

# one-letter replies and common confirmations
YES = {"yes", "y", "ok", "sure", "confirm", "create", "proceed"}
NO = {"no", "n", "cancel", "stop", "abort"}

def _as_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return {}

async def preprocess_node(
    state: AgentState,
) -> AgentState:
    """
    Preprocess node: the only place that mutates/normalizes user input before planning.

    Responsibilities
    ----------------
    1) Normalize containers (`slots`, `tool_input`) and set `question` to the latest user text.
    2) Manage `question_history`:
       - Normal turns: keep ONLY the latest (freshest) user message; trim if needed.
       - Clarify/Confirm turns: stitch `original_question` + latest reply for context.
    3) Handle duplicate-confirm flow (yes/no):
       - YES: short-circuit planning and route to `{intent}_skip_plan_node`.
       - NO : produce a final cancel message and short-circuit.
       - Else: re-ask yes/no and short-circuit.
    4) Purge *all stale* fields that could pollute the next plan:
       - Clear `tool_input`, `tool_result`, `final_answer`, `intent`, `used_tool_name`,
         and any cached `planner_result` *except* when actively clarifying/confirming.

    Notes
    -----
    - Absolutely NO planner calls here. This node prepares clean state only.
    - Only concatenate user text when we're in clarify or confirm flows.
    """
    logger.info("Preprocess Node")
    logger.debug("state: %r", state)

    # ---------- 0) Hardening / normalization ----------
    if not isinstance(getattr(state, "slots", None), dict):
        state.slots = {}
    state.tool_input = _as_dict(getattr(state, "tool_input", {}))

    # Compute latest user message
    latest: str = ""
    if isinstance(state.messages, list) and state.messages:
        msg = state.messages[-1]
        if isinstance(msg, dict):
            latest = (msg.get("content") or "").strip()
    if not latest:
        latest = (state.question or "").strip()
    state.question = latest

    # Detect clarify payload presence (robust)
    ti: dict[str, Any] = state.tool_input or {}
    has_clarify_payload = (
        isinstance(ti, dict)
        and ("original_question" in ti)
        and ("missing_fields" in ti or "clarify_prompt" in ti)
    )

    # Detect duplicate-confirm flow flag
    in_confirm = bool(state.slots.get("awaiting_confirm_duplicate"))

    # ---------- 1) Manage question history ----------
    # Clarify or Confirm: stitch the original question + user reply so the planner
    # has a single cohesive prompt next turn.
    if state.previous_node == "clarify" or has_clarify_payload or in_confirm:
        base = (ti.get("original_question") or state.question or "").strip()
        append = latest.strip()
        combined = f"{base} {append}".strip() if append else base
        state.question = combined  # IMPORTANT: stitched
        state.slots["question_history"] = [combined]
    else:
        # Normal turn: reset history to the latest user message only (fresh turn).
        state.slots["question_history"] = [latest] if latest else []
        # If keep a cap elsewhere, this trims safely without mutating `question`.
        trim_question_history(state)

    # ---------- 2) Duplicate-confirm branching ----------
    if in_confirm:
        # pull what the previous step proposed
        original_q: str = ti.get("original_question", state.question)
        proposed_intent: str = ti.get("proposed_intent", "create_project")
        proposed_payload: dict[str, Any] = _as_dict(ti.get("proposed_tool_input", {}))
        item_type: str = ti.get("item_type", "item")
        prompt: str = ti.get("clarify_prompt") or f"Create this {item_type} anyway? (yes/no)"

        user_reply = (latest or "").strip().lower()
        logger.info("Confirm flow awaiting yes/no; user said: %s", user_reply)

        if user_reply in YES:
            # Short-circuit plan: go execute the tool, but skip re-checking existence
            state.question = original_q
            state.intent = proposed_intent
            state.tool_input = proposed_payload
            state.slots.pop("awaiting_confirm_duplicate", None)
            state.slots.pop("planner_result", None)
            state.used_tool_name = f"{proposed_intent}_skip_plan_node"
            state.final_answer = ""
            state.tool_result = ""
            state.previous_node = "preprocess"
            return state

        if user_reply in NO:
            # Short-circuit with a cancel message and CLEAN slate for next turns
            state.slots.pop("awaiting_confirm_duplicate", None)
            state.slots.pop("planner_result", None)
            state.tool_input = {}
            state.intent = None
            state.used_tool_name = "final_answer_skip_plan_node"
            state.tool_result = f"Project creation was cancelled, duplicated item(s) is/are found, user terminate request."
            state.final_answer = f"Project creation was cancelled."
            state.previous_node = "preprocess"
            return state

        # Ambiguous reply: ask again
        state.used_tool_name = "final_answer"
        state.tool_result = ""
        state.final_answer = f"Please reply 'yes' or 'no'.\n\n{prompt}"
        state.previous_node = "preprocess"
        return state

    # ---------- 3) Normal turn cleanup (no clarify/confirm) ----------
    # Not in any special flow; wipe leftovers that can bias planning.
    state.used_tool_name = None
    state.intent = None
    state.final_answer = ""
    state.tool_result = ""
    state.slots.pop("planner_result", None)

    # If NOT clarifying, drop any leftover tool_input so planner starts clean.
    if not (state.previous_node == "clarify" or has_clarify_payload):
        state.tool_input = {}

    state.previous_node = "preprocess"
    return state
