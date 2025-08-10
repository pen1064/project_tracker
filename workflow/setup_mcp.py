import os
import logging
from typing import Callable, Awaitable, Optional
from fastmcp import Client

logger = logging.getLogger(__name__)

MCP_DB_URL: Optional[str] = os.environ.get("MCP_SERVER_DB_URL")
MCP_GEMINI_URL: Optional[str] = os.environ.get("MCP_SERVER_GEMINI_URL")

ToolFn = Callable[..., Awaitable]

def _wrap_tool(client: Client, tool_name: str) -> ToolFn:
    async def _runner(**kw):
        return await client.call_tool(tool_name, kw)
    return _runner

async def setup_mcp() -> dict[str, ToolFn]:
    """
    Connect to up to two MCP servers (DB + Gemini) and return:
      - clients: {'db': Client, 'gemini': Client} for those that exist
      - mcp_tools: mapping of callable tools with BOTH
    """
    clients: dict[str, Client] = {}
    mcp_tools: dict[str, ToolFn] = {}

    if MCP_DB_URL:
        logger.info("Connecting MCP DB server: %s", MCP_DB_URL)
        db_client = Client(MCP_DB_URL)
        await db_client.__aenter__()
        clients["db"] = db_client

        db_tools = await db_client.list_tools()
        logger.info("DB tools: %s", [t.name for t in db_tools])

        for t in db_tools:
            mcp_tools[t.name] = _wrap_tool(db_client, t.name)

    else:
        logger.warning("MCP_SERVER_DB_URL not set; skipping DB MCP server.")


    if MCP_GEMINI_URL:
        logger.info("Connecting MCP Gemini server: %s", MCP_GEMINI_URL)
        gem_client = Client(MCP_GEMINI_URL)
        await gem_client.__aenter__()
        clients["gemini"] = gem_client

        gem_tools = await gem_client.list_tools()
        logger.info("Gemini tools: %s", [t.name for t in gem_tools])

        for t in gem_tools:
            mcp_tools[t.name] = _wrap_tool(gem_client, t.name)
    else:
        logger.warning("MCP_SERVER_GEMINI_URL not set; skipping Gemini MCP server.")

    return mcp_tools

async def close_mcp(clients: dict[str, Client]) -> None:
    for label, client in clients.items():
        try:
            await client.__aexit__(None, None, None)
            logger.info("Closed MCP client: %s", label)
        except Exception as e:
            logger.exception("Error closing MCP client '%s': %s", label, e)
