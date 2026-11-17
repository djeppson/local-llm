# Handoff — llama.cpp ROCm integration

**Status:** active — plan written, unit exists, **not yet brought up to spec**.

## Context

Goal: run llama.cpp as a standalone ROCm server on dj7900 alongside Ollama, exposed to Open WebUI as an OpenAI-compatible backend. Models managed via the standard Hugging Face cache at `~/.cache/huggingface/hub/`.

## Current state (verified 2026-11-17)

- **Plan:** [`plan-llama-cpp-rocm.md`](./plan-llama-cpp-rocm.md) — full integration plan (restore point). Copied from `notes/projects/plan-llamaCppRocmIntegration.prompt.md`.
- **Unit:** `~/.config/systemd/user/llama-server.service` exists but is **disabled + inactive**. Configured for `0.0.0.0:10000`, loading `Qwen3.6-27B-Q4_K_M.gguf` from the HF cache. Not the live process on `:39299` — that one is Ollama's bundled runner (see [`telemetry/baseline-2026-11-17.md`](../telemetry/baseline-2026-11-17.md)).
- **Model present:** `lmstudio-community/Qwen3.6-27B-GGUF` (16 GB) in HF cache.

## Next action

**Bring the plan up to spec.** The plan was written before the current live state was captured; it predates the hardened Ollama user-unit and the real port/VRAM picture. Run it through `grill-me` to resolve open branches (notably: standalone-unit vs Ollama-bundled-runner, host bind `0.0.0.0` vs loopback, VRAM budget against the 87%-resident `bonsai-2:27b`), then execute against the refreshed spec and digest this handoff.

## Open branches (to resolve in grilling)

- Bind: plan says `0.0.0.0:10000`; Ollama is loopback-only by design — should llama.cpp match?
- Concurrency: running both Ollama's runner and a standalone llama.cpp on one 24GB GPU — VRAM budget?
- The plan's "After" diagram still shows Open WebUI on `:3000` (stale; real port is `:8080`).
