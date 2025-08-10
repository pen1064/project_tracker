import { z } from "zod";


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