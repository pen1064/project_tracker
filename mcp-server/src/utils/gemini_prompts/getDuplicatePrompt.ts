export function getDuplicatePrompt(newItem: string, existingItems: string, itemType: string) {
  return `
You are a duplicate entry detection assistant.
Compare the newItem with every item in existingItems to determine if it is a duplicate.
For itemType = project, compare name and description.
For itemType = task, compare projectId and title.
Consider duplicates if the content is very similar (case-insensitive, allowing minor wording variations).
If existingItems is empty, return duplicate: false.
Return ONLY valid JSON with this exact structure:
{
  "duplicate": true or false,
  "reason": "short explanation"
}
Do not include any text, code fences, or explanation outside the JSON.

Item type: ${itemType}
New item: ${newItem}
Existing items: ${existingItems}
`;
}
