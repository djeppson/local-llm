# Architecture

## Overview

The Local LLM Stack is a self-hosted, privacy-first AI assistant platform that combines local LLM inference with web search capabilities. It runs entirely on your machine using Podman containers, with no external dependencies beyond image pulls.

## Components

### 1. Open WebUI

**Role:** Frontend interface and orchestration layer.

Open WebUI provides a ChatGPT-like web interface that connects to:
- **Ollama** (running on the host) for local LLM inference
- **SearXNG** for web search augmentation

**Key configuration:**
- Runs in host network mode for direct access to both Ollama (`:11434`) and SearXNG (`:8411`)
- Environment variables `OLLAMA_BASE_URL` and `SEARXNG_API_URL` point to the respective backends
- Data persists in a Podman volume mounted at `/app/backend/data`

**Why host networking?** Open WebUI needs to reach both Ollama (running on the host, not in a container) and SearXNG (published on the host via the compose network port mapping). Host networking simplifies connectivity without complex port mapping.

### 2. SearXNG

**Role:** Privacy-respecting metasearch engine.

SearXNG aggregates results from multiple search engines without tracking user queries. It serves as the web search backend for Open WebUI's "web search" feature.

**Key configuration:**
- Listens on port `8411` (configurable via `.env`)
- Configuration files stored in `core-config/` directory, mounted read-write into the container
- Cache data persisted in the `core-data` Podman volume

**Why SearXNG?** Unlike direct search engine APIs, SearXNG:
- Doesn't require API keys
- Aggregates from 70+ search engines
- Respects privacy (no tracking, no profiling)
- Runs entirely locally

### 3. Valkey

**Role:** In-memory data store (Redis-compatible).

Valkey (a Redis fork) provides caching and session storage for SearXNG. It handles:
- Result caching to reduce redundant search queries
- Rate limiting state
- Session management

**Key configuration:**
- Runs as `valkey-server` with minimal persistence (`--save 30 1`)
- Data persisted in the `valkey-data` Podman volume
- Only accessible within the compose network (no external port exposure)

### 4. Ollama (Host)

**Role:** Local LLM inference engine.

Ollama runs directly on the host (not in a container) and provides:
- Local LLM model management and inference
- REST API on port `11434`
- GPU acceleration when available

**Why host instead of container?** Ollama requires direct GPU access and NVIDIA driver integration. Running it natively on the host avoids container GPU passthrough complexity.

## Networking

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Host Machine                                   │
│                                                                      │
│  ┌───────────────┐                                                  │
│  │    Ollama     │                                                  │
│  │   :11434      │                                                  │
│  └───────────────┘                                                  │
│         ▲                                                           │
│         │                                                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Open WebUI (network_mode: host)                             │    │
│  │  :3000                                                       │    │
│  │  ┌───────────────┐  ┌───────────────────┐                    │    │
│  │  │ Talks to      │  │ Talks to          │                    │    │
│  │  │ Ollama        │  │ SearXNG           │                    │    │
│  │  │ :11434        │  │ :8411             │                    │    │
│  │  └───────────────┘  └───────────────────┘                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│         ▲                                                           │
│         │                                                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Podman Compose Network: local-llm                           │    │
│  │                                                              │    │
│  │  ┌──────────────┐  ┌──────────────┐                          │    │
│  │  │   SearXNG    │  │    Valkey    │                          │    │
│  │  │ :8411        │  │    :6379     │                          │    │
│  │  └──────────────┘  └──────────────┘                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### Network Design Decisions

1. **Compose Network (`local-llm`):** SearXNG and Valkey share the default compose network, giving them DNS-based connectivity (by service name) without exposing ports to the host beyond what's published.

2. **Host Network (Open WebUI):** Open WebUI uses `network_mode: host` to reach both the host's Ollama and the published SearXNG port without complex routing.

3. **Minimal Exposure:** Only SearXNG's port is published (`8411`, configurable via `.env`). Valkey has no published ports — it's only accessible from SearXNG via the compose network. Open WebUI listens on the host directly (port `3000`).

## Data Persistence

| Volume / Mount              | Purpose                          | Container       |
|-----------------------------|----------------------------------|-----------------|
| `core-data` (Podman volume) | SearXNG cache and runtime data   | searxng-core    |
| `valkey-data` (Podman volume)| Valkey dataset persistence      | searxng-valkey  |
| `core-config/` (bind mount) | SearXNG configuration files      | searxng-core    |
| Open WebUI volume (bind)    | Open WebUI backend data          | open-webui      |

### Backup Strategy

To back up all persistent data:
```bash
# Podman volumes
podman volume export local-llm_core-data > core-data-backup.tar
podman volume export local-llm_valkey-data > valkey-data-backup.tar

# SearXNG config
tar czf core-config-backup.tar.gz core-config/

# Open WebUI data
tar czf open-webui-data-backup.tar.gz /home/jeppson/.local/share/containers/storage/volumes/open-webui/_data
```

## Systemd Integration

The stack is managed by a systemd user service (`local-llm.service`) that:
- Starts the entire compose stack on boot
- Stops all containers cleanly on shutdown
- Uses `RemainAfterExit=yes` so systemd tracks the "started" state correctly

**Service file location:** `~/.config/systemd/user/local-llm.service`

**Why a user service?** Podman runs in rootless mode, so the service must run under the user's systemd instance, not the system instance.

## Security Considerations

1. **Rootless Containers:** All containers run without root privileges via Podman's rootless mode.
2. **SELinux Labels:** Volume mounts use `:Z` labels for proper SELinux context.
3. **Minimal Exposure:** Only necessary ports are published (SearXNG: `8411`, Open WebUI: `3000`).
4. **No Root Access:** Valkey and internal services have no external network exposure.
