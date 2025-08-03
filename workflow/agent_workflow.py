import logging
from typing import Any, Union

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph

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
from workflow.utils import trim_question_history

logger = logging.getLogger(__name__)


class AgentWorkflow:
    def __init__(self) -> None:
        self.graph: StateGraph = self._build_graph()
        self.checkpointer: InMemorySaver = InMemorySaver()
        self.compiled: Any = self.graph.compile(checkpointer=self.checkpointer)
        self.context: Union[AgentContext, None] = None

    @staticmethod
    def _route_after_plan(state: AgentState) -> str:
        """Route based on tool chosen by plan_node."""
        if state.used_tool_name == "gemini_clarify":
            return "clarify_node"
        elif state.used_tool_name == "query_projects":
            return "query_projects"
        elif state.used_tool_name == "query_tasks":
            return "query_tasks"
        elif state.intent == "create_project":
            return "check_project_exists"
        elif state.intent == "create_task":
            return "check_task_exists"
        else:
            return "final_answer"

    @staticmethod
    def _route_after_analyze(state: AgentState) -> str:
        """
        Route after analyze_after_check_node.
        If analyze_after_check sets duplicate_confirmation, we pause there.
        """
        if state.used_tool_name == "final_answer":
            return "final_answer"
        elif state.intent == "create_project":
            return "create_project"
        elif state.intent == "create_task":
            return "create_task"

    def _build_graph(self) -> StateGraph:
        graph: StateGraph = StateGraph(
            state_schema=AgentState, context_schema=AgentContext
        )

        # Nodes
        graph.add_node("preprocess", preprocess_node)
        graph.add_node("plan", plan_node)
        graph.add_node("clarify_node", clarify_node)
        graph.add_node("query_tasks", query_tasks_node)
        graph.add_node("query_projects", query_projects_node)
        graph.add_node("check_project_exists", check_project_exists_node)
        graph.add_node("check_task_exists", check_task_exists_node)
        graph.add_node("analyze_after_check", analyze_after_check_node)
        graph.add_node("create_project", create_project_node)
        graph.add_node("create_task", create_task_node)
        graph.add_node("final_answer", answer_node)

        # Entry
        graph.set_entry_point("preprocess")

        # Flow
        graph.add_edge("preprocess", "plan")
        graph.add_conditional_edges("plan", self._route_after_plan)

        # Normal query flows -> final_answer
        graph.add_edge("query_projects", "final_answer")
        graph.add_edge("query_tasks", "final_answer")

        # Existence check flows
        graph.add_edge("check_project_exists", "analyze_after_check")
        graph.add_edge("check_task_exists", "analyze_after_check")

        # Analyze node can route to duplicate_confirmation, create, or final
        graph.add_conditional_edges("analyze_after_check", self._route_after_analyze)

        # Create → final_answer
        graph.add_edge("create_project", "final_answer")
        graph.add_edge("create_task", "final_answer")

        # End
        graph.add_edge("final_answer", END)

        return graph

    async def setup(self) -> None:
        session, mcp_tools = await setup_mcp()
        self.context = AgentContext(mcp_tools=mcp_tools)
        logger.info("MCP tools ready")

    async def chat_repl(self, user_id: str ="user"):
        """
            A simple command-line chat REPL to interact with the agent for particular user session/thread.
            Workflow:
            - Takes initial user input.
            - Initializes AgentState with the input.
            - Runs the compiled state graph asynchronously.
            - Prints the agent's reply.
            - Accepts further user messages until user quits.
        """
        config: dict[str, str] = {"thread_id": user_id}
        first_msg: str = input("You: ").strip()
        state: AgentState = AgentState(
            question=first_msg,
            user_id=user_id,
            thread_id=user_id,
            slots={"question_history": [first_msg]},
            messages=[{"role": "user", "content": first_msg}],
        )
        while True:
            result: Any = await self.compiled.ainvoke(
                input=state.model_dump(),
                config=config,
                context=self.context,
            )
            # Update state from the returned result
            state = AgentState(**result) if isinstance(result, dict) else result

            print("Agent:", state.final_answer)

            # Accept next user input
            msg: str = input("You: ").strip()
            if msg.lower() in ("exit", "quit"):
                break

            # Append message to slot when user provides additional information, combining only user's question and
            # clarification can help LLM agent to fully understand the complete questions without being overwhelmed or
            # get confused by extra system messages.
            if state.used_tool_name == "gemini_clarify":
                state.slots.setdefault("question_history", []).append(msg)
            else:
                state.slots["question_history"] = [msg]

            # Trim question history to manageable length
            trim_question_history(state)

            # Append message to conversation log
            state.messages.append({"role": "user", "content": msg})

            # Clear final_answer so it won't persist incorrectly
            state.final_answer = ""
