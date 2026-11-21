# Handoff — llama.cpp ROCm integration

**Status:** active — plan written, unit exists, **not yet brought up to spec**.

## Context

Goal: run llama.cpp as a standalone ROCm server on dj7900 alongside Ollama, exposed to Open WebUI as an OpenAI-compatible backend. Models managed via the standard Hugging Face cache at `~/.cache/huggingface/hub/`.

## Triage (2026-11-21)

**Decision: Keep.** Standalone ROCm llama.cpp server alongside Ollama — plan + disabled systemd unit exist; three open branches are well-identified. Only local-ROCm-server track; abandoning means staying Ollama-only for llama.cpp workloads.

**Next step + LOE:** Run the plan through `grill-me` to resolve the three open branches (bind address, VRAM/concurrency, stale Open WebUI port `:3000` → real `:8080`), then refresh the plan before execution. **[S = <1hr]** — focused grilling over three already-identified decisions, not a re-plan.

**Dependencies:** Head of the local-infra cluster. Its model (`Qwen3.6-27B-Q4_K_M.gguf`, `lmstudio-community/Qwen3.6-27B-GGUF`, 16 GB) is one of the 21 dirs in the `hf-cache-cleanup` audit — that cleanup must account for this track's model. Shares the Open WebUI surface with `hf-token-hygiene`.

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
