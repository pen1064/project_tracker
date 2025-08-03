import express from "express";
import { randomUUID } from "crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

import { registerTools } from "./handlers/tools.js";

const app = express();
app.use(express.json());

const sessionMap = new Map<string, StreamableHTTPServerTransport>();

app.post("/mcp", async (req, res) => {
  const sid = req.headers["mcp-session-id"] as string | undefined;
  const isInit = req.body?.method === "initialize";

  let transport: StreamableHTTPServerTransport;

  if (sid && sessionMap.has(sid)) {
    // Reuse existing session
    transport = sessionMap.get(sid)!;
  } else if (isInit && !sid) {
    // Create new session with persistent storage
    const newSessionId = randomUUID();
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => newSessionId,
      enableJsonResponse: true,
      onsessioninitialized: (id) => {
        sessionMap.set(id, transport);
        console.debug(`MCP session initialized: ${id}`);
      }
    });

    const server = new McpServer({ name: "task-service", version: "1.0.0" });
    registerTools(server);
    await server.connect(transport);

    // Set header before the SDK writes the response
    res.setHeader("mcp-session-id", newSessionId);
  } else {
    return res.status(400).json({
      jsonrpc: "2.0",
      error: {
        code: -32000,
        message: "Bad Request: Server not initialized"
      },
      id: req.body?.id ?? null
    });
  }

  console.log("<MCP server> Incoming request:", JSON.stringify(req.body));
  await transport.handleRequest(req, res, req.body);
});

app.listen(process.env.PORT ?? 4000, () => {
  console.log("MCP HTTP server listening on port", process.env.PORT ?? 4000);
});
