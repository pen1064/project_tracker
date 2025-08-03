import logging

from workflow.agent_state import AgentState

MAX_HISTORY: int = 4

logger = logging.getLogger(__name__)


def find_missing_fields(required_fields: list[str], params: dict[str]) -> list[str]:
    """
    Return a list of required fields that are missing or empty in params.
    """
    return [key for key in required_fields if not params.get(key)]


def trim_question_history(state: AgentState) -> None:
    """
    Trim question history to a maximum number of entries
    and update state.question with the joined history.
    """
    history: list[str] = state.slots.get("question_history", [])
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        state.slots["question_history"] = history
    state.question = " ".join(history)


def prompt_user_for_duplicate(
    existing_items_list: list, new_item: dict[str, str], item_type: str
) -> bool:
    """
    Prompt the user synchronously to confirm creation despite duplicates.
    Returns True if user says yes, False otherwise.
    """
    if item_type == "project":
        existing_names_list_print_out: str = ", ".join(
            [f'{p.get("name", "")} (id: {p.get("id", "")})' for p in existing_items_list]
        )
        target_item_name: str = new_item.get("name", "")
    else:
        existing_names_list_print_out = ", ".join(
            [f'{t.get("title", "")} (id: {t.get("id", "")})' for t in existing_items_list]
        )
        target_item_name = new_item.get("title", "")

    print(f"A similar {item_type} already exists: {existing_names_list_print_out}.")

    answer = (
        input(f"Do you still want to create '{target_item_name}'? (yes/no): ")
        .strip()
        .lower()
    )

    return answer.startswith("y")
