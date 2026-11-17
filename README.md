# Local LLM Stack

This repo is the working surface for the local IT landscape — the LLM stack is its largest tenant, but host hardware inventory, agent tooling, and ancillary services live here too. Naming is deferred until usage patterns settle; for now it stays `local-llm`.

## Project Overview

These services provide a complete self-hosted local AI productivity solution

- **Ollama** as a local inference provider for LLM hosting
- **Open WebUI** provides chat interface and collaboration
- **SearXNG** as privacy-respecting search backend
- **OpenCode** for AI coding assistance
- **Nginx** and **AWS Route 53** for access by other systems on the local network

## Directory map

- [`machine/`](./machine/) — per-host hardware inventory + live diagnostics ([`dj7900/`](./machine/dj7900/), [\`jeppmini/](./machine/jeppmini/))
- [`docs/`](./docs/) — stack setup guides + experiment notes ([`ollama.md`](./docs/ollama.md), [`openwebui.md`](./docs/openwebui.md), [`vllm.md`](./docs/vllm.md), [`prompts/`](./docs/prompts/))
- [`telemetry/`](./telemetry/) — point-in-time stack baselines
- [`core-config/`](./core-config/) — SearXNG config
- [`opencode/`](./opencode/) — OpenCode agent config
- [`.scratch/`](./.scratch/) — agent handoffs (disposable; see `INDEX.md`)

## Tech Stack

- **Arch Linux** host OS
- **Systemd** for service management
  - Uses standard systemd command format `systemctl [--user] <command> <service_name>`
  - For user service management the `--user` flag is required
  - Symbolic links to service configurations provided in this repo `*.service`
- **Podman** and **Podman Compose** (not Docker) for container management
  - Check status: `podman-compose ps`
  - View logs: `podman-compose logs`
  - Note: Service status may not always reflect the latest file configurations

## Service Management

- User Service: `local-llm`
  - Open WebUI: http://localhost:8080
  - SearXNG: http://localhost:8411
- User Service: `ollama` with GPU acceleration via ROCm
  - Binds to loopback only (`OLLAMA_HOST=127.0.0.1:11434` in `~/.config/systemd/user/ollama.service`) — not directly reachable over the network
  - Ollama API: http://localhost:11434
  - OpenAI-compatible API: http://localhost:11434/v1
  - Available models can be fetched from these endpoints:
    - Ollama tags endpoint: http://localhost:11434/api/tags
    - OpenAI models endpoint: http://localhost:11434/v1/models
- System Service: `nginx-local`
  - Open WebUI: https://dj7900-local.darrenjeppson.com/
  - SearXNG: http://dj7900-local.darrenjeppson.com:8411

> ⚠️ As of 2026-11-17 the TLS cert for `dj7900-local.darrenjeppson.com` is **expired** (since 2026-08-02). See [`telemetry/baseline-2026-11-17.md`](./telemetry/baseline-2026-11-17.md).

## Testing/Verification

- Test configuration by checking that services/containers are up and healthy
- Fetch service endpoints to confirm availability and expected responses
- Note: Endpoints are static and should remain consistent unless configuration changes
- Test endpoints in any order - clearly identify which ones fail to quickly diagnose service issues

## Resources

- [SearXNG Documentation](https://docs.searxng.org/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Podman Compose Documentation](https://podman-desktop.io/docs/podman-compose)
- [Ollama Documentation](https://ollama.com/)
- [Qwen Model Hub](https://huggingface.co/Qwen)
