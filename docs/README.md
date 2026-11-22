# Stack docs

Setup guides and experiment notes for the local LLM stack on [`machine/dj7900/`](../machine/dj7900/). Each guide is a self-contained page; the host inventory and live diagnostics live under `machine/`, point-in-time measurements live under [`telemetry/`](../telemetry/).

## Stack components

| Component              | Port                                                  | Guide                                              |
| ---------------------- | ----------------------------------------------------- | -------------------------------------------------- |
| Ollama (ROCm, GGUF)    | `127.0.0.1:11434`                                     | [`ollama.md`](./ollama.md)                         |
| Open WebUI             | `:8080` (host net)                                    | [`openwebui.md`](./openwebui.md)                   |
| SearXNG                | `:8411`                                               | `core-config/` (config)                            |
| nginx (TLS → `:8080`)  | `:443`                                                | `nginx-local.service` symlink                      |

## Experiment notes

- [`vllm.md`](./vllm.md) — vLLM trials (GPU + CPU) with benchmark numbers. Kept for the benchmark data; Ollama won for this use case. HF token is read from the environment, never inlined.

## Prompts

[`prompts/`](./prompts/) — prompt-engineering notes (context skeletons, story/dev prompt patterns). Moved from `notes/scratch/llm/`.
