import { GoogleGenAI } from "@google/genai";
import { getAnswerPrompt } from "./gemini_prompts/getAnswerPrompt.js";
import { getClarifyPrompt } from "./gemini_prompts/getClarifyPrompt.js";
import { getDuplicatePrompt } from "./gemini_prompts/getDuplicatePrompt.js";
import { getPlanPrompt } from "./gemini_prompts/getPlanPrompt.js";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

/**
 * Generic Gemini caller using Google GenAI SDK.
 */
async function callGemini(prompt: string, temperature = 0): Promise<string> {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-lite",
    contents: [
      {
        role: "user",
        parts: [{ text: prompt }],
      },
    ],
    config: {
      temperature: temperature,
      thinkingConfig: {
        thinkingBudget: 1024,
      }
    }
  });
  return (response.text || "").trim();
}


/**
 * Parsing Output
 */
async function parseGeminiJSON(prompt: string, temperature = 0): Promise<any> {
  const raw = await callGemini(prompt, temperature);
  // Clean up response: handle ```json ... ``` blocks or extra text
  let cleaned = raw.trim();
  // If Gemini wraps in triple backticks, remove them
  if (cleaned.startsWith("```")) {
    cleaned = cleaned.replace(/```[a-zA-Z]*\n?/g, "").replace(/```$/, "");
  }

  const jsonMatch = raw.match(/\{[\s\S]*\}/);
  const jsonText = jsonMatch ? jsonMatch[0] : raw;
  console.log("--------------------MCP jsonText-------------------------")
  console.log(jsonText);

  try {
    return JSON.parse(jsonText);
  } catch {
    throw new Error(`Gemini returned invalid JSON.\nRaw output:\n${raw}`);
  }
}

/**
 * Planner
 */
export async function geminiPlanner(question: string) {
  const today = new Date().toISOString().split("T")[0];
  const prompt = getPlanPrompt(question, today);
  return parseGeminiJSON(prompt, 0);
}

/**
 * Clarification
 */
export async function geminiClarify(missingFields: string[], originalQuestion: string) {
  const today = new Date().toISOString().split("T")[0];
  const prompt = getClarifyPrompt(missingFields, originalQuestion, today);
  return callGemini(prompt, 0);
}

/**
 * Answer
 */
export async function geminiAnswer(question: string, toolResult: string, previousNode: string) {
  const today = new Date().toISOString().split("T")[0];
  const prompt = getAnswerPrompt(question, toolResult, previousNode, today);
  return callGemini(prompt, 0);
}

/**
 * Duplicate
 */
export async function geminiDuplicateAnalyzer(
  newItem: string,
  existingItems: string,
  itemType: string,
) {
  const prompt = getDuplicatePrompt(newItem, existingItems, itemType);
  try {
    const parsed = await parseGeminiJSON(prompt, 0);
    return { ...parsed, newItem, existingItems };
  } catch {
    return {
      duplicate: true,
      reason: "Could not parse Gemini output, let user decide",
      newItem,
      existingItems,
    };
  }
}

