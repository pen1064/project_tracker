import json
import logging

from typing import Any, Callable, Awaitable
from langgraph.runtime import Runtime
from mcp.types import CallToolResult

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState
from workflow.utils import with_error


logger = logging.getLogger(__name__)


async def analyze_after_check_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """
    Analyze results from check_*_exists nodes.
    If duplicates are found:
      - Ask the user via a clarify turn and resume on the next request.
    If no duplicates:
      - Route directly to create_* node.
    """
    async def _impl():
        logger.info("Analyzing results after existence check.")

        raw_existing_items: str = state.tool_result
        new_item_str: str = json.dumps(state.tool_input, separators=(",", ":"))
        if state.intent in ("create_project", "create_task"):
            is_project: bool = state.intent == "create_project"
            item_type: str = "project" if is_project else "task"
            analyzer: Callable[..., Awaitable[Any]] = runtime.context.mcp_tools["gemini_duplicate_analyzer"]

            response: CallToolResult = await analyzer(
                new_item=new_item_str,
                existing_items=raw_existing_items,
                item_type=item_type,
            )

            text: str = response.content[0].text
            result: dict[str, Any] = json.loads(text)

            if result["isError"] is True:
                raise RuntimeError(result["isError"])

            decision = result["result"]
            is_duplicate = bool(decision.get("duplicate", False))

            existing_items_list: list = json.loads(raw_existing_items)

            if is_duplicate:
                lines = []
                for item in existing_items_list:
                    item_id = item["id"]
                    created = item["created_time"]
                    name_or_title = item["name"] if is_project else item["title"]
                    lines.append(f"- {name_or_title} (id={item_id}, created_time={created})")
                detail_text = "\n".join(lines) if lines else "(no details)"

                prompt: str = (
                    f"I found existing {item_type}(s) that look similar:\n"
                    f"{detail_text}\n\n"
                    f"Create this {item_type} anyway? (yes/no)"
                )

                state.used_tool_name: str = "gemini_clarify"
                state.tool_input: dict[str, Any] = {
                    "missing_fields": ["confirm_duplicate"],
                    "original_question": state.question,
                    "clarify_prompt": prompt,
                    "proposed_intent": state.intent,
                    "proposed_tool_input": state.tool_input,
                    "item_type": item_type,
                }
                state.final_answer = prompt
            else:
                state.used_tool_name = "create_project" if is_project else "create_task"

        state.previous_node = "analyze_after_check"
        return state


    return await with_error(state, "analyze_after_check", _impl())