# Handoff — Hugging Face cache cleanup

**Status:** active — audit needed; deletions not yet made.

## Context

`~/.cache/huggingface` is **143 GB** with **21 model dirs** (see [`telemetry/baseline-2026-11-17.md`](../telemetry/baseline-2026-11-17.md) for the size breakdown). Several are near-duplicate variants of the same base model — Qwen3.6-27B alone has six cached variants:

| Dir                                    | Size  | Note                                      |
| -------------------------------------- | ----- | ----------------------------------------- |
| `lmstudio-community--Qwen3.6-27B-GGUF` | 16 GB | the one the `llama-server` unit loads     |
| `unsloth--Qwen3.6-27B-GGUF`            | 20 KB | metadata only                             |
| `Lorbus--Qwen3.6-27B-int4-AutoRound`   | 48 KB | metadata only                             |
| `Qwen--Qwen3.6-27B`                    | 22 MB | metadata only                             |
| `Qwen--Qwen3.6-27b`                    | 22 MB | metadata only — likely a dup of the above |
| `Qwen--Qwen3.6-27B-FP8`                | 22 MB | metadata only                             |

The ~22 MB and ~20 KB dirs are mostly manifest stubs, not full weights — the real space is in the big ones. But the dups create `huggingface-cli` confusion and make `scan-cache` noisy.

## Goal

Trim the cache to the models actually in use (or queued for near-term use), recover disk, and leave a clean inventory.

## Approach (sketch)

1. **Audit** — `huggingface-cli scan-cache` and cross-reference against:
   - Ollama models actually loaded (`curl -s http://localhost:11434/api/tags`)
   - The `llama-server.service` model path
   - Anything referenced in `docs/` or `.scratch/` plans
1. **Identify safe-to-delete** — near-duplicate variants not referenced anywhere; the 20 KB / 22 MB metadata stubs of unused variants first (free wins); then the larger unreferenced weights.
1. **Delete** — `huggingface-cli delete-cache` (interactive) is the safe path since it shows sizes and prompts per-model.
1. **Re-capture** a baseline in `telemetry/` after cleanup (next dated file).

## Open questions (resolve before deleting)

- Is `ByteDance-Seed--Seed-Coder-8B-Reasoning` (31 GB — the largest entry) still wanted? Not referenced by any Ollama model or the llama.cpp unit.
- `Qwen--Qwen2.5-Coder-32B-Instruct-AWQ` (19 GB) — does anything use it? Ollama's `/api/tags` did not list a 32B model on 2026-11-17.
- Keep both `Qwen2.5-Coder-7B-Instruct` (15 GB) and its `-AWQ` (5.2 GB), or consolidate to one?

## Digestion condition

Cleanup done + a refreshed `telemetry/baseline-*.md` recording the post-cleanup cache state.
