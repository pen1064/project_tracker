import { FastMCP } from "fastmcp";
import * as Schemas from "./schemas.js";
import { fetchTasks, fetchProjects, createProject, createTask } from "../utils/tasks.js";

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

export function registerTools(server: FastMCP) {
  server.addTool({
    name: "query_tasks", description: "Query Tasks", parameters: Schemas.QueryTasksInput,
    execute: async (args: Schemas.QueryTasksArgs) => {
      try {
        const tasks = await fetchTasks(args);
        if (!tasks?.length) return wrapStructured({ isError: true as const, error: "No matching tasks found." });
        return wrapStructured({ isError: false as const, tasks });
      } catch (e: any) {
        return wrapStructured({ isError: true as const, error: e.message });
      }
    },
  });

  server.addTool({
    name: "query_projects", description: "Query Projects", parameters: Schemas.QueryProjectsInput,
    execute: async (args: Schemas.QueryProjectsArgs) => {
      try {
        const projects = await fetchProjects(args);
        if (!projects?.length) return wrapStructured({ isError: true as const, error: "No matching projects found." });
        return wrapStructured({ isError: false as const, projects });
      } catch (e: any) {
        return wrapStructured({ isError: true as const, error: e.message });
      }
    },
  });

  server.addTool({
    name: "create_project", description: "Create Project", parameters: Schemas.CreateProjectInput,
    execute: async (args: Schemas.CreateProjectArgs) => {
      try {
        const project = await createProject(args);
        return wrapStructured({ isError: false as const, project });
      } catch (e: any) {
        return wrapStructured({ isError: true as const, error: e.message });
      }
    },
  });

  server.addTool({
    name: "create_task", description: "Create Task", parameters: Schemas.CreateTaskInput,
    execute: async (args: Schemas.CreateTaskArgs) => {
      try {
        const task = await createTask(args);
        return wrapStructured({ isError: false as const, task });
      } catch (e: any) {

        return wrapStructured({ isError: true as const, error:  e?.response?.data?.detail || e?.response?.data || e.message || e });
      }
    },
  });
}
