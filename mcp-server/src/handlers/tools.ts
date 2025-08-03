import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  fetchTasks,
  fetchProjects,
  createProject,
  createTask,
} from "../utils/tasks.js";
import {
  geminiPlanner,
  geminiAnswer,
  geminiClarify,
  geminiDuplicateAnalyzer,
} from "../utils/gemini.js";
import * as Schemas from "./schemas.js";

function wrapStructured<T extends object>(payload: T) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(payload, null, 2),
      },
    ],
  };
}


// Register all tools in the same style
export function registerTools(server: McpServer) {
  // query_tasks
  server.registerTool(
    "query_tasks",
    {
      title: "Query Tasks",
      description: "Fetch tasks with optional filters",
      inputSchema: Schemas.QueryTasksInput.shape,
    },
    async (args: Schemas.QueryTasksArgs) => {
      try {
        const tasks = await fetchTasks(args);
        if (!tasks || tasks.length === 0) {
          return wrapStructured({ isError: true as const, error: "No matching tasks found." });
        }
        return wrapStructured({ isError: false as const, tasks });
      } catch (err: any) {
        const backendError = err?.response?.data?.error || JSON.stringify(err?.response?.data || {});
        const combinedError = `Error creating task: ${err.message}. Backend response: ${backendError}`;
        return wrapStructured({ isError: true as const, error: combinedError });
      }
    }
  );

  // query_projects
  server.registerTool(
    "query_projects",
    {
      title: "Query Projects",
      description: "Fetch projects with optional filters",
      inputSchema: Schemas.QueryProjectsInput.shape,
    },
    async (args: Schemas.QueryProjectsArgs) => {
      try {
        const projects = await fetchProjects(args);
        if (!projects || projects.length === 0) {
          return wrapStructured({ isError: true as const, error: "No matching projects found." });
        }
        return wrapStructured({ isError: false as const, projects });
      } catch (err: any) {
        const backendError = err?.response?.data?.error || JSON.stringify(err?.response?.data || {});
        const combinedError = `Error creating task: ${err.message}. Backend response: ${backendError}`;
        return wrapStructured({ isError: true as const, error: combinedError });
      }
    }
  );

  // create_project
  server.registerTool(
    "create_project",
    {
      title: "Create Project",
      description: "Create a new project",
      inputSchema: Schemas.CreateProjectInput.shape,
    },
    async (args: Schemas.CreateProjectArgs) => {
      try {
        const project = await createProject(args);
        return wrapStructured({ isError: false as const, project });
      } catch (err: any) {
        const backendError = err?.response?.data?.error || JSON.stringify(err?.response?.data || {});
        const combinedError = `Error creating task: ${err.message}. Backend response: ${backendError}`;
        return wrapStructured({ isError: true as const, error: combinedError });
      }
    }
  );

  // create_task
  server.registerTool(
    "create_task",
    {
      title: "Create Task",
      description: "Create a new task in a project",
      inputSchema: Schemas.CreateTaskInput.shape,
    },
    async (args: Schemas.CreateTaskArgs) => {
      try {
        const task = await createTask(args);
        return wrapStructured({ isError: false as const, task });
      } catch (err: any) {
        const backendError = err?.response?.data?.error || JSON.stringify(err?.response?.data || {});
        const combinedError = `Error creating task: ${err.message}. Backend response: ${backendError}`;
        return wrapStructured({ isError: true as const, error: combinedError });
      }
    }
  );

  // gemini_planner
  server.registerTool(
    "gemini_planner",
    {
      title: "Gemini Planner",
      description: "Plan which tool to use based on a natural language question",
      inputSchema: Schemas.GeminiPlannerInput.shape,
    },
    async (args: Schemas.GeminiPlannerArgs) => {
      try {
        const plan = await geminiPlanner(args.question);
        return wrapStructured({ isError: false as const, plan });
      } catch (err: any) {
        return wrapStructured({ isError: true as const, error: `Error planning: ${err.message}` });
      }
    }
  );

  // gemini_answer
  server.registerTool(
    "gemini_answer",
    {
      title: "Gemini Answer",
      description: "Answer a question using a tool_result",
      inputSchema: Schemas.GeminiAnswerInput.shape,
    },
    async (args: Schemas.GeminiAnswerArgs) => {
      try {
        const answer = await geminiAnswer(args.question, args.tool_result, args.previous_node);
        return wrapStructured({ isError: false as const, answer });
      } catch (err: any) {
        return wrapStructured({ isError: true as const, error: `Error answering: ${err.message}` });
      }
    }
  );

  // gemini_clarify
  server.registerTool(
    "gemini_clarify",
    {
      title: "Gemini Clarify",
      description: "Ask clarifying questions when fields are missing",
      inputSchema: Schemas.GeminiClarifyInput.shape,
    },
    async (args: Schemas.GeminiClarifyArgs) => {
      try {
        const clarification = await geminiClarify(args.missing_fields, args.original_question);
        return wrapStructured({ isError: false as const, clarification });
      } catch (err: any) {
        return wrapStructured({ isError: true as const, error: `Error clarifying: ${err.message}` });
      }
    }
  );

  // gemini_duplicate_analyzer
  server.registerTool(
    "gemini_duplicate_analyzer",
    {
      title: "Gemini Duplicate Analyzer",
      description: "Check if a new item is a duplicate",
      inputSchema: Schemas.GeminiDuplicateAnalyzerInput.shape,
    },
    async (args: Schemas.GeminiDuplicateAnalyzerArgs) => {
      try {
        const result = await geminiDuplicateAnalyzer(args.new_item, args.existing_items, args.item_type);
        return wrapStructured({ isError: false as const, result });
      } catch (err: any) {
        return wrapStructured({ isError: true as const, error: `Error analyzing duplicates: ${err.message}` });
      }
    }
  );
}
