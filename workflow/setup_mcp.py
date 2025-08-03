import json
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any, Union

import aiohttp

logger = logging.getLogger(__name__)

MCP_URL: str = os.environ.get("MCP_SERVER_URL")


class MCPHttpClient:
    def __init__(self, base_url: str = MCP_URL) -> None:
        self.base_url: str = base_url
        self.session: aiohttp.ClientSession = None
        self.session_id: Union[str, None] = None
        self._id_counter: int = 0
        logger.info(f"MCPHttpClient initialized with base_url: {self.base_url}")

    async def _ensure_session(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def initialize(self) -> dict[str, Any]:
        """
        Perform the MCP 'initialize' call and capture the mcp-session-id.
        """
        await self._ensure_session()
        self._id_counter += 1
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "python-client", "version": "1.0.0"},
            },
        }
        headers: dict[str, str] = {"Accept": "application/json,text/event-stream"}
        logger.info(f"Sending MCP initialize -> {json.dumps(payload)}")
        async with self.session.post(
            self.base_url, json=payload, headers=headers
        ) as resp:
            text: str = await resp.text()
            logger.info(f"Initialize raw response: {text}")
            data: dict[str, Any] = json.loads(text)
            self.session_id: str = resp.headers.get("mcp-session-id")
            logger.info(f"Session ID: {self.session_id}")
            return data

    async def _call(self, method: str, params: dict):
        """
        JSON-RPC call with session_id header.
        """
        if not self.session_id:
            raise RuntimeError("MCP client not initialized. Call initialize() first.")
        await self._ensure_session()

        self._id_counter += 1
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": method,
            "params": params or {},
        }
        headers: dict[str, str] = {
            "Accept": "application/json,text/event-stream",
            "mcp-session-id": self.session_id,
        }
        async with self.session.post(
            self.base_url, json=payload, headers=headers
        ) as resp:
            text: str = await resp.text()
            logger.debug(f"Raw response ({method}): {text}")
            data: dict[str, Any] = json.loads(text)
            if "error" in data:
                raise RuntimeError(data["error"])
            return data["result"]

    async def list_tools(self):
        logger.info("Listing tools...")
        result: dict[str, Any] = await self._call("tools/list", {})
        tools: list[dict[str, Any]] = result.get("tools", [])
        return {t["name"]: t for t in tools}

    async def run_tool(self, tool_name: str, **kwargs):
        """
        Run a specific tool via tools/call.
        """
        logger.debug(f"Running tool: {tool_name} with args: {kwargs}")
        params: dict[str, Any] = {"name": tool_name, "arguments": kwargs}
        result: dict[str, Any] = await self._call("tools/call", params)

        # MCP response always has content array; parse if JSON
        content_item = result["content"][0]
        text: str = content_item.get("text", "")
        try:
            return json.loads(text)
        except Exception:
            return text

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None


async def setup_mcp():
    """
    Initialize MCP and return a tuple (client, tool_runners).
    tool_runners is a dict of async functions to run tools easily.
    """
    client: MCPHttpClient = MCPHttpClient()
    await client.initialize()
    tools_info: dict[str, dict[str, Any]] = await client.list_tools()

    mcp_tools: dict[str, Callable[..., Awaitable[Any]]] = {}

    def make_runner(tool_name) -> Callable[..., Awaitable[Any]]:
        async def _runner(**kwargs):
            return await client.run_tool(tool_name, **kwargs)

        return _runner

    for tool_name in tools_info:
        mcp_tools[tool_name] = make_runner(tool_name)

    return client, mcp_tools
