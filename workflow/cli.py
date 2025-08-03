import asyncio
import logging

from workflow.agent_workflow import AgentWorkflow


async def main():
    agent: AgentWorkflow = AgentWorkflow()
    await agent.setup()
    await agent.chat_repl(user_id="taylor_swift")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
