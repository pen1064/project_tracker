import { FastMCP } from "fastmcp";
import { registerTools } from "./handlers/tools.js";

async function main() {
  const server = new FastMCP({
    name: "DB Server",
    version: "1.0.0",
  });

  registerTools(server);

  await server.start({
    transportType: "httpStream",
    httpStream: {
      port: 4000,
      stateless: true,
    },
  });

  console.log("MCP server is running on http://localhost:4000/mcp");
}

main().catch((err) => {
  console.error("Failed to start FastMCP server:", err);
  process.exit(1);
});
