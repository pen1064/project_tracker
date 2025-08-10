import os
import logging
from typing import Any, Optional

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from workflow.agent_context import AgentContext
from workflow.agent_state import AgentState

from workflow.nodes.analyze_after_check_node import analyze_after_check_node
from workflow.nodes.answer_node import answer_node
from workflow.nodes.check_proejct_exists_node import check_project_exists_node
from workflow.nodes.check_task_exist_node import check_task_exists_node
from workflow.nodes.clarify_node import clarify_node
from workflow.nodes.create_project_node import create_project_node
from workflow.nodes.create_task_node import create_task_node
from workflow.nodes.plan_node import plan_node
from workflow.nodes.preprocess_node import preprocess_node
from workflow.nodes.query_projects_node import query_projects_node
from workflow.nodes.query_tasks_node import query_tasks_node
from workflow.setup_mcp import setup_mcp

logger = logging.getLogger(__name__)

class AgentWorkflow:
    def __init__(self) -> None:
        self.graph: StateGraph = self._build_graph()

        # Build an async context manager for the saver (not opened yet)
        redis_url = os.getenv("REDIS_URL", "redis://redis_data:6379/0")
        self._checkpointer_cm = AsyncRedisSaver.from_conn_string(redis_url)
        self.checkpointer = None  # will be set in setup()
        self.compiled: Any = None
        self.context: Optional[AgentContext] = None

    def _build_graph(self) -> StateGraph:
        g = StateGraph(state_schema=AgentState, context_schema=AgentContext)
        g.add_node("preprocess", preprocess_node)
        g.add_node("plan", plan_node)
        g.add_node("clarify", clarify_node)
        g.add_node("query_tasks", query_tasks_node)
        g.add_node("query_projects", query_projects_node)
        g.add_node("check_project_exists", check_project_exists_node)
        g.add_node("check_task_exists", check_task_exists_node)
        g.add_node("analyze_after_check", analyze_after_check_node)
        g.add_node("create_project", create_project_node)
        g.add_node("create_task", create_task_node)
        g.add_node("final_answer", answer_node)

        g.set_entry_point("preprocess")
        g.add_edge("preprocess", "plan")
        g.add_conditional_edges("plan", self._route_after_plan)
        g.add_edge("query_projects", "final_answer")
        g.add_edge("query_tasks", "final_answer")
        g.add_edge("check_project_exists", "analyze_after_check")
        g.add_edge("check_task_exists", "analyze_after_check")
        g.add_conditional_edges("analyze_after_check", self._route_after_analyze)
        g.add_edge("create_project", "final_answer")
        g.add_edge("create_task", "final_answer")
        g.add_edge("final_answer", END)
        return g

    @staticmethod
    def _route_after_plan(state: AgentState) -> str:
        """
        Decide route based on planner output/intents.
        """
        if state.error:
            return "final_answer"
        elif state.used_tool_name == "gemini_clarify":
            return "clarify"
        elif state.used_tool_name == "query_projects":
            return "query_projects"
        elif state.used_tool_name == "query_tasks":
            return "query_tasks"
        elif state.used_tool_name == "create_project_skip_plan_node":
            return "create_project"
        elif state.used_tool_name == "create_task_skip_plan_node":
            return "create_task"
        elif state.used_tool_name == "final_answer_skip_plan_node":
            return "final_answer"
        elif state.intent == "create_project":
            return "check_project_exists"
        elif state.intent == "create_task":
            return "check_task_exists"
        else:
            return "final_answer"

    @staticmethod
    def _route_after_analyze(state: AgentState) -> str:
        # Go to clarify if we requested a duplicate confirmation
        if state.error:
            return "final_answer"
        elif state.used_tool_name == "gemini_clarify" or state.slots.get("awaiting_confirm_duplicate"):
            return "clarify"
        if state.used_tool_name == "final_answer":
            return "final_answer"
        elif state.intent == "create_project":
            return "create_project"
        elif state.intent == "create_task":
            return "create_task"
        return "final_answer"

    async def setup(self) -> None:
            # Open the saver (context manager) for the app lifetime
            self.checkpointer = await self._checkpointer_cm.__aenter__()
            if hasattr(self.checkpointer, "asetup"):
                await self.checkpointer.asetup()
            # Compile after the saver is ready
            self.compiled = self.graph.compile(checkpointer=self.checkpointer)

            # Wire MCP tools
            mcp_tools = await setup_mcp()
            self.context = AgentContext(mcp_tools=mcp_tools)
            logger.info("MCP tools added to context.")

    async def close(self) -> None:
        if self._checkpointer_cm is not None:
            await self._checkpointer_cm.__aexit__(None, None, None)
