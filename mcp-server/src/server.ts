import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { statelessHandler } from "express-mcp-handler";
import { registerTools } from "./handlers/tools.js";

const app = express();
app.use(express.json());

app.post("/mcp", statelessHandler(() => {
  const s = new McpServer({ name: "task-service", version: "1.0.0" });
  registerTools(s);
  return s;
}, {
  onError: err => console.error("MCP stateless error:", err)
}));

const port = parseInt(process.env.PORT || "4000", 10);
app.listen(port, () => {
  console.log(`MCP server listening on port ${port}`);
});
