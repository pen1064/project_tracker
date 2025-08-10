import { FastMCP } from "fastmcp";
import * as Schemas from "./schemas.js";
import { geminiPlanner, geminiAnswer, geminiClarify, geminiDuplicateAnalyzer } from "../utils/gemini.js";

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
  // Gemini tools
  server.addTool({
    name: "gemini_planner", description: "Gemini Planner", parameters: Schemas.GeminiPlannerInput,
    execute: async (args: any) => {
      try {
        const plan = await geminiPlanner(args.question);
        return wrapStructured({ isError: false as const, plan });
      } catch (e: any) {
        return wrapStructured({ isError: true as const, error: e.message });
      }
    },
  });

  server.addTool({
    name: "gemini_answer", description: "Gemini Answer", parameters: Schemas.GeminiAnswerInput,
    execute: async (args: any) => {
      try {
        const answer = await geminiAnswer(args.question, args.tool_result, args.previous_node);
        return wrapStructured({ isError: false as const, answer });
      } catch (e: any) {
        return wrapStructured({ isError: true as const, error: e.message });
      }
    },
  });

  server.addTool({
    name: "gemini_clarify", description: "Gemini Clarify", parameters: Schemas.GeminiClarifyInput,
    execute: async (args: any) => {
      try {
        const clarification = await geminiClarify(args.missing_fields, args.original_question);
        return wrapStructured({ isError: false as const, clarification });
      } catch (e: any) {
        return wrapStructured({ isError: true as const, error: e.message });
      }
    },
  });

  server.addTool({
    name: "gemini_duplicate_analyzer", description: "Gemini Duplicate Analyzer", parameters: Schemas.GeminiDuplicateAnalyzerInput,
    execute: async (args: any) => {
      try {
        const result = await geminiDuplicateAnalyzer(args.new_item, args.existing_items, args.item_type);
        return wrapStructured({ isError: false as const, result });
      } catch (e: any) {
        console.log("new");
        console.log(e);
        return wrapStructured({ isError: true as const, error: e?.response?.data?.detail });
      }
    },
  });
}
