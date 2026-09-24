import { Type } from "typebox";
import { defineToolPlugin } from "openclaw/plugin-sdk/tool-plugin";

export default defineToolPlugin({
  id: "cesa-lookup",
  name: "CESA Lookup",
  description: "Consult the local, cited CESA knowledge base.",
  tools: (tool) => [
    tool({
      name: "cesa_lookup",
      description: "Answer a student's CESA question using the local evidence service. Relay its answer and source links; do not invent missing information.",
      optional: true,
      parameters: Type.Object({
        question: Type.String({ minLength: 3, maxLength: 350, description: "Student's question in Spanish." }),
      }),
      async execute({ question }, _config, context) {
        context.signal?.throwIfAborted();
        const response = await fetch("http://127.0.0.1:8765/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
          signal: context.signal,
        });
        if (!response.ok) throw new Error("Local CESA service unavailable");
        const result = await response.json() as Record<string, unknown>;
        if (typeof result.answer !== "string" || !Array.isArray(result.sources)) {
          throw new Error("Unexpected CESA service response");
        }
        // Wrap domain status: a top-level status=no_match is interpreted as a tool failure.
        return { result };
      },
    }),
  ],
});
