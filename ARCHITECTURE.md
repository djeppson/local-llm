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

**Why host networking?** Open WebUI needs to reach both Ollama (running on the host, not in a container) and SearXNG (in the Podman pod). Host networking simplifies connectivity without complex port mapping.

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
- Only accessible within the Podman pod (no external port exposure)

### 4. Ollama (Host)

**Role:** Local LLM inference engine.

Ollama runs directly on the host (not in a container) and provides:
- Local LLM model management and inference
- REST API on port `11434`
- GPU acceleration when available

**Why host instead of container?** Ollama requires direct GPU access and NVIDIA driver integration. Running it natively on the host avoids container GPU passthrough complexity.

## Networking

```
┌─────────────────────────────────────────────────────┐
│                    Host Machine                      │
│                                                      │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │   Ollama     │◄───│  Podman Pod: local-llm   │   │
│  │  :11434      │    │                          │   │
│  └──────────────┘    │  ┌──────────┐  ┌───────┐ │   │
│                      │  │ SearXNG  │  │Valkey │ │   │
│                      │  │ :8411    │  │ :6379 │ │   │
│                      │  └──────────┘  └───────┘ │   │
│                      └──────────────────────────┘   │
│                      ▲                              │
│  ┌───────────────────┴──────────────────────────┐   │
│  │  Open WebUI (host network)                   │   │
│  │  :3000                                       │   │
│  │  ┌─────────────┐  ┌──────────────────────┐   │   │
│  │  │ Talks to    │  │ Talks to             │   │   │
│  │  │ Ollama      │  │ SearXNG              │   │   │
│  │  │ :11434      │  │ :8411                │   │   │
│  │  └─────────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Network Design Decisions

1. **Podman Pod (`local-llm`):** SearXNG and Valkey share a pod, giving them shared networking (localhost connectivity) without exposing ports externally.

2. **Host Network (Open WebUI):** Open WebUI uses `network_mode: host` to reach both the host's Ollama and the pod's SearXNG without complex routing.

3. **No External Exposure:** Valkey has no published ports — it's only accessible within the pod. SearXNG's port is published for direct access but primarily consumed by Open WebUI.

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
