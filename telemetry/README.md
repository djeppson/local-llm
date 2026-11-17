# Telemetry

Point-in-time snapshots of the stack and host. One file per capture, named `baseline-YYYY-MM-DD.md`. The latest baseline is the working source of truth for "current state"; older files are kept for diffing over time.

Capture scope (baseline): service units + states, `podman compose ps`, LLM-relevant listening ports, Ollama model list (`/api/tags`), Hugging Face cache size + model count, ROCm/GPU memory state, TLS cert validity for `dj7900-local.darrenjeppson.com`.

## Baselines

- [`baseline-2026-11-17.md`](./baseline-2026-11-17.md) — first capture; surfaced an expired TLS cert (since 2026-08-02) and a disabled `llama-server.service`.
