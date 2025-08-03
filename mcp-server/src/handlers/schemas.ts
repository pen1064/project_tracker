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

export const GeminiPlannerInput = z.object({
  question: z.string(),
});
export type GeminiPlannerArgs = z.infer<typeof GeminiPlannerInput>;

export const GeminiAnswerInput = z.object({
  question: z.string(),
  tool_result: z.string(),
  previous_node: z.string(),
});
export type GeminiAnswerArgs = z.infer<typeof GeminiAnswerInput>;

export const GeminiClarifyInput = z.object({
  missing_fields: z.array(z.string()),
  original_question: z.string(),
});
export type GeminiClarifyArgs = z.infer<typeof GeminiClarifyInput>;

export const GeminiDuplicateAnalyzerInput = z.object({
  new_item: z.string(),
  existing_items: z.string(),
  item_type: z.string(),
});
export type GeminiDuplicateAnalyzerArgs = z.infer<typeof GeminiDuplicateAnalyzerInput>;