import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from workflow.workflow_class import UserMessage
from workflow.agent_workflow import AgentWorkflow, AgentState

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

agent: AgentWorkflow = AgentWorkflow()


@asynccontextmanager
async def lifespan(app: Any) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan: ensure agent is set up before serving and log shutdown.
    """
    logger.info(">>> Lifespan starting, calling agent.setup()")
    await agent.setup()
    logger.info("Agent setup complete.")
    try:
        yield
    finally:
        logger.info("Application shutting down.")


def _reset_transients_for_new_turn(state: AgentState) -> None:
    """
    Clear per-turn/transient routing fields so each request starts clean.
    """
    state.used_tool_name = None
    state.intent = None
    state.final_answer = ""
    state.tool_result = ""
    state.previous_node = ""
    # Clear cached planner result if present
    state.slots = state.slots or {}
    state.slots.pop("planner_result", None)


async def _rehydrate_state(payload: UserMessage) -> AgentState:
    """
    Build or rehydrate AgentState from the incoming payload.
    """
    user_id: str = (
        payload.user_id
        or (payload.state.get("user_id") if payload.state else None)
        or "anon"
    )
    thread_id: str = str(user_id)
    user_msg: str = payload.message

    if payload.state:
        state: AgentState = AgentState(**payload.state)
        state.user_id = state.user_id or thread_id
        state.thread_id = state.thread_id or thread_id
    else:
        state = AgentState(
            question=user_msg,
            user_id=thread_id,
            thread_id=thread_id,
            slots={},
            messages=[],
        )

    # Append latest user message & set question to ONLY this message
    state.messages = (state.messages or []) + [{"role": "user", "content": user_msg}]
    state.question = user_msg

    # Reset per-turn transients so this turn doesn't short-circuit
    _reset_transients_for_new_turn(state)

    return state


async def process_chat(payload: UserMessage) -> dict[str, Any]:
    """
    Non-streaming path: run the graph to completion and return the final answer + state.
    """
    # Ensure agent is ready (hot-reload / worker restart safety)
    if agent.context is None:
        logger.warning("agent.context is None, running setup again.")
        await agent.setup()

    state = await _rehydrate_state(payload)

    # Invoke the graph (non-streaming)
    result: Any = await agent.compiled.ainvoke(
        input=state.model_dump(),
        config={"configurable": {"thread_id": state.thread_id}},
        context=agent.context,
    )

    # Allow both dict and AgentState returns
    state = AgentState(**result) if isinstance(result, dict) else result
    return {"answer": state.final_answer, "state": state.model_dump()}
