import { z } from "zod";

export const QueryTasksInput = z.object({
  assigned_to: z.string().optional(),
  status: z.string().optional(),
  project_id: z.number().optional(),
  title: z.string().optional(),
  due_date: z.string().optional(),
});
export type QueryTasksArgs = z.infer<typeof QueryTasksInput>;

export const QueryProjectsInput = z.object({
  name: z.string().optional(),
  status: z.string().optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
});
export type QueryProjectsArgs = z.infer<typeof QueryProjectsInput>;

export const CreateProjectInput = z.object({
  name: z.string(),
  description: z.string().optional(),
  start_date: z.string(),
  end_date: z.string().optional(),
  status: z.string().optional(),
});
export type CreateProjectArgs = z.infer<typeof CreateProjectInput>;

export const CreateTaskInput = z.object({
  title: z.string(),
  assigned_to: z.string().optional(),
  status: z.string().optional(),
  due_date: z.string().optional(),
  project_id: z.number(),
});
export type CreateTaskArgs = z.infer<typeof CreateTaskInput>;