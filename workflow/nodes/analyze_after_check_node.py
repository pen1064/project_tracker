import json
import logging
from typing import Any, Union

from langgraph.runtime import Runtime

from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState
from workflow.utils import prompt_user_for_duplicate

logger = logging.getLogger(__name__)


async def analyze_after_check_node(
    state: AgentState, runtime: Runtime[AgentContext]
) -> AgentState:
    """
    Analyze results from check_*_exists nodes:
    - If duplicates found, prompt user (sync) whether to continue
    - If no duplicates, proceed to create
    """
    logger.info("Analyzing results after existence check.")
    existing: str = state.tool_result
    new_item: str = json.dumps(state.tool_input, separators=(",", ":"))

    if state.intent in ("create_project", "create_task"):
        is_project: bool = state.intent == "create_project"
        item_type: str = "project" if is_project else "task"
        analyzer = runtime.context.mcp_tools["gemini_duplicate_analyzer"]

        raw_decision: Union[str, dict[str, Any]] = await analyzer(
            new_item=new_item,
            existing_items=existing,
            item_type=item_type,
        )
        decision = raw_decision["result"]
        is_duplicate = bool(decision["duplicate"])

        existing_items_list: list = json.loads(existing)

        if is_duplicate:
            is_proceed: bool = prompt_user_for_duplicate(
                existing_items_list,
                state.tool_input,
                "project" if is_project else "task",
            )

            if is_proceed:
                state.used_tool_name: str = (
                    "create_project" if is_project else "create_task"
                )
            else:
                state.used_tool_name = "final_answer"
                details_lines: list[str] = []
                for item in existing_items_list:
                    item_id = item.get("id", "unknown")
                    created = item.get("created_time", "unknown")
                    name_or_title = (
                        item.get("name") if is_project else item.get("title")
                    )
                    details_lines.append(
                        f"- {name_or_title} (id={item_id}, created_time={created})"
                    )

                detail_text = "\n".join(details_lines)
                state.tool_result = (
                    f"Duplicate {'project' if is_project else 'task'} creation aborted. "
                    f"The following existing {'projects' if is_project else 'tasks'} were found:\n"
                    f"{detail_text}"
                )
        else:
            state.used_tool_name = "create_project" if is_project else "create_task"

    state.previous_node: str = 'analyze_after_check'
    return state
