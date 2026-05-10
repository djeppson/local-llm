# Local LLM Stack

A self-hosted local LLM stack powered by **Podman**, combining [Open WebUI](https://docs.openwebui.com/) with [SearXNG](https://docs.searxng.org/) as a privacy-respecting search backend, all orchestrated via `podman-compose`.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Your Browser                    │
└────────────────────┬────────────────────────────┘
                     │ :3000
                     ▼
┌─────────────────────────────────────────────────┐
│              Open WebUI (:3000)                  │
│  - Chat UI for local LLMs                       │
│  - Connected to Ollama for inference            │
│  - Connected to SearXNG for web search          │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│   Ollama      │         │   SearXNG     │
│  (:11434)     │         │  (:8411)      │
│  Local LLM    │         │  Search       │
│  Inference    │         │  Engine       │
└───────────────┘         └───────┬───────┘
                                 │
                        ┌────────▼────────┐
                        │   Valkey        │
                        │  (Redis compat) │
                        │  Cache/Backend  │
                        └─────────────────┘
```

## Quick Start

### Start the Stack
```bash
cd /home/jeppson/projects/local-llm
podman compose up -d
```

### Stop the Stack
```bash
podman compose down
```

### Check Status
```bash
podman compose ps
```

### View Logs
```bash
podman compose logs -f
```

## Auto-Start on Boot

The stack is managed by a **systemd user service** that starts automatically on boot:

```bash
# Check service status
systemctl --user status local-llm

# Start/stop/restart via systemd
systemctl --user start local-llm
systemctl --user stop local-llm
systemctl --user restart local-llm
```

> **Note:** User linger is enabled (`loginctl enable-linger`), so the service starts at boot even without an interactive login session.

## Access Points

| Service      | URL                              | Description              |
|--------------|----------------------------------|--------------------------|
| Open WebUI   | http://localhost:3000            | Main chat interface      |
| SearXNG      | http://localhost:8411            | Search engine interface  |

## Configuration

### Environment Variables

All runtime configuration is in `.env`. See `.env.example` for available options.

Key variables:
- **`SEARXNG_PORT`** — Port for SearXNG (default: `8411`)
- **`SEARXNG_HOST`** — Bind address for SearXNG (default: `0.0.0.0`)
- **`SEARXNG_VERSION`** — SearXNG image tag (default: `latest`)

### SearXNG Settings

SearXNG configuration files live in `core-config/`. Edit `settings.yml` there to customize search engines, themes, etc.

### Open WebUI

Open WebUI data is stored in Podman volumes. The backend data directory is mounted from:
```
/home/jeppson/.local/share/containers/storage/volumes/open-webui/_data
```

## Project Structure

```
local-llm/
├── podman-compose.yml      # Podman Compose stack definition
├── .env                    # Runtime environment variables
├── .env.example            # Template with documented variables
├── core-config/            # SearXNG configuration directory
│   ├── settings.yml        # SearXNG settings
│   ├── limiter.toml        # Rate limiter config
│   └── uwsgi.ini           # uWSGI configuration
├── README.md               # This file
├── ARCHITECTURE.md         # Detailed architecture documentation
└── TROUBLESHOOTING.md      # Common issues and fixes
```

## Containers

| Container       | Image                              | Purpose                    |
|-----------------|------------------------------------|----------------------------|
| `searxng-core`  | `docker.io/searxng/searxng`        | SearXNG search engine      |
| `searxng-valkey`| `docker.io/valkey/valkey:9-alpine`  | Redis-compatible cache     |
| `open-webui`    | `ghcr.io/open-webui/open-webui`     | Web UI for local LLMs      |

## Updating

### Update Images
```bash
# Pull latest images
podman compose pull

# Restart with new images
podman compose up -d
```

### Update Configuration
1. Edit `.env` or `core-config/settings.yml`
2. Restart the stack: `podman compose up -d`

## Resources

- [SearXNG Documentation](https://docs.searxng.org/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Podman Compose Documentation](https://podman-desktop.io/docs/podman-compose)
- [Ollama Documentation](https://ollama.com/)
