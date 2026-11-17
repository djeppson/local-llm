# Stack docs

Setup guides and experiment notes for the local LLM stack on [`machine/dj7900/`](../machine/dj7900/). Each guide is a self-contained page; the host inventory and live diagnostics live under `machine/`, point-in-time measurements live under [`telemetry/`](../telemetry/).

## How to read these docs

- **Authoritative (live truth)** — the files the stack actually reads: the `*.service` symlinks at the repo root, [`podman-compose.yml`](../podman-compose.yml), [`core-config/`](../core-config/), and Open WebUI's `webui.db`. When current state matters, read the file — the prose here is not the source.
- **Runbooks (this directory)** — what each component is, *why* it is configured that way (pins, binds, warnings), day-2 operations, and the commands that reproduce current live state.
- **Point-in-time state** — [`telemetry/`](../telemetry/): the latest baseline is the working source of truth for "what was running when." Dated numbers quoted in prose are snapshots from here, not facts of record.

Quick live port check:

```sh
ss -ltn | grep -E ':(11434|10000|39299|8080|8411|443)\b'
```

## Stack components

| Component                | Defined (authoritative)                                                           | Runbook                                                        |
| ------------------------ | --------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Ollama (ROCm, GGUF)      | `ollama.service` symlink (unit env vars)                                          | [`ollama.md`](./ollama.md)                                     |
| llama.cpp (ROCm, GGUF)   | unit lives on the host; state in telemetry/ + handoff                             | [handoff](../.scratch/handoff-llama-cpp-rocm.md) (in progress) |
| Open WebUI               | [`podman-compose.yml`](../podman-compose.yml) + `webui.db`                        | [`openwebui.md`](./openwebui.md)                               |
| SearXNG                  | [`podman-compose.yml`](../podman-compose.yml) + [`core-config/`](../core-config/) | pointer-level only (see `openwebui.md`)                        |
| nginx (TLS → Open WebUI) | `nginx-local.service` symlink + `~/projects/nginx-local/`                         | pointer-level only (see `openwebui.md`)                        |

## Experiment notes

- [`vllm.md`](./vllm.md) — vLLM trials (GPU + CPU) with benchmark numbers. Kept for the benchmark data; Ollama won for this use case. HF token is read from the environment, never inlined.

## Prompts

[`prompts/`](./prompts/) — prompt-engineering notes (context skeletons, story/dev prompt patterns). Moved from `notes/scratch/llm/`.
