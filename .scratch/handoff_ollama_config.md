# Handoff: Ollama/OpenCode Model Configuration Research

## Context
The user wants to configure `ollama` models in `opencode.json` with high confidence in how to control:
1. **Overall context window size** (OpenCode-side vs. Ollama-side)
2. **Reasoning level** (`reasoningEffort` vs `capabilities.reasoning` vs `variants`)

## Findings

### 1. Context Window Control
- **OpenCode-side (`limit.context`):** This is the primary lever for OpenCode's internal managing (compaction, buffer sizing). Set this to override the discovered value from Ollama.
- **Ollama-side (`num_ctx`):** OpenCode doesn't natively pass `num_ctx` through a dedicated setting. To control the actual allocation at the Ollama engine, use the `body` field to inject it into the request:
  ```jsonc
  "body": { "options": { "num_ctx": 131072 } }
  ```
- **Precedence:** `limit.context` controls OpenCode's *perception* of the window, while `body.options.num_ctx` controls the *actual* engine allocation.

### 2. Reasoning Control
- **The "OpenAI-compatible" bridge:** Most local providers (including Ollama) use the `@opencode/ai/providers/openai-compatible` package.
- **Control via `settings`:** The package expects camelCase `reasoningEffort` (e.g., `"medium"`). The user's current snake_case `reasoning_effort` might be ignored.
- **Control via `capabilities`:** To make reasoning levels selectable as variants (e.g. `#low`, `#high`), define them in `capabilities.reasoning`:
  ```jsonc
  "capabilities": {
    "reasoning": { "supported": true, "effort": ["low", "medium", "high"] }
  }
  ```
- **Control via `variants`:** Manual naming of variants (e.g., a `#deep` variant) is possible by overriding `settings` or `body` per variant.

### 3. Schema & Code Verification
- **OpenCode Version:** 2.4.1 (running in Bun).
- **Ollama Version:** 0.40.13.
- **Ollama Verification:** `qwen3.8:27b` has a native context length of `262144`, but this is not always correctly surface-reported in the `details` object, making `limit.context` essential for reliability.

## Goal for Next Agent
Review the user's `opencode.json` and provide a finalized, tested-ready configuration block for their `ollama/qwen3.8:27b` model, implementing both the `limit` and `capabilities` patterns discovered.

## Suggested Skills
- `opencode` (to verify schema)
- `write` (to apply the final config)
