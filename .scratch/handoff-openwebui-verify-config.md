# Handoff: verify Open WebUI configuration

Placeholder task — deliberately left shallow on purpose (user wants adequate context kept, no deep DB spelunking for now).

## Goal

Verify the live Open WebUI configuration still matches the context snapshot in [`docs/openwebui.md`](../docs/openwebui.md) (snapshot read from `webui.db` on 2026-11-11): signup disabled, single admin account, Ollama connected at `http://localhost:11434`, RAG web search via SearXNG at `http://localhost:8411`, external OpenAI-compatible (HuggingFace router) enabled, image pin `v0.9.4`.

## Constraints

- `webui.db` contains a secret (the HF API key in the `config` row). If/when verifying, read only the specific keys you need — never dump the whole row, never paste config JSON into chat or into repo files.
- The version pin's source of truth is [`podman-compose.yml`](../podman-compose.yml); don't bump it as part of this task unless asked.

## Suggested skills

- `sec-review` — at digestion (default exit gate, waivable by user): this task touches secret-adjacent surface.

## Status

Pending. No work done yet; the context above plus the existing day-2 commands in `docs/openwebui.md` is all that's needed to start.
