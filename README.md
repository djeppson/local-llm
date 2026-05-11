# Local LLM Stack

A self-hosted local LLM stack powered by **Podman**, combining [Open WebUI](https://docs.openwebui.com/) with [SearXNG](https://docs.searxng.org/) as a privacy-respecting search backend, all orchestrated via `podman-compose`.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Your Browser                    │
└────────────────────┬────────────────────────────┘
                     │ :3000
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Open WebUI (:3000)                      │
│  - Chat UI for local LLMs                               │
│  - Connected to Ollama + llama.cpp for inference        │
│  - Connected to SearXNG for web search                  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────┐
│   Ollama     │ │ llama.cpp    │ │   SearXNG     │
│  (:11434)    │ │  (:10000)    │ │  (:8411)      │
│  CPU-based   │ │  GPU-based   │ │  Search       │
│  Inference   │ │  Inference   │ │  Engine       │
└──────────────┘ └──────────────┘ └───────┬───────┘
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
| llama.cpp    | http://localhost:10000/v1        | OpenAI-compatible API    |
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

Models are stored in: ~/.cache/huggingface/hub/
```

## Containers

| Container       | Image                                      | Purpose                      |
|-----------------|--------------------------------------------|-----------------------------|
| `searxng-core`  | `docker.io/searxng/searxng`                | SearXNG search engine       |
| `searxng-valkey`| `docker.io/valkey/valkey:9-alpine`         | Redis-compatible cache      |
| `open-webui`    | `ghcr.io/open-webui/open-webui`            | Web UI for local LLMs        |

## Managing llama.cpp Models

### Switch to Qwen3.5 27B Model

llama.cpp runs as a **systemd user service** and loads the model path specified directly in the service file (not via environment variables). Models are cached in the standard Hugging Face cache directory: `~/.cache/huggingface/hub/`.

#### Steps to Download and Activate Qwen3.5 27B:

1. **Download the Model**

   Download a GGUF-quantized version of Qwen3.5 27B from Hugging Face:

   ```bash
   # Install Hugging Face CLI if not already installed
   pip install huggingface-hub

   # Download model (uses standard HF cache at ~/.cache/huggingface/hub/)
   huggingface-cli download lmstudio-community/Qwen3.6-27B-GGUF --include "*Q4_K_M*"
   ```

   > **Note:** The Q4_K_M quantization is recommended for 27B models. Adjust based on your VRAM. The download is cached in `~/.cache/huggingface/hub/`.

2. **Find the Downloaded Model Path**

   After downloading, note the full path to the GGUF file:

   ```bash
   # Find your downloaded model
   find ~/.cache/huggingface/hub -name "*Qwen3.6*27B*.gguf" -type l
   ```

   Example output might be:
   ```
   ~/.cache/huggingface/hub/models--lmstudio-community--Qwen3.6-27B-GGUF/snapshots/[hash]/Qwen3.6-27B-Q4_K_M.gguf
   ```

3. **Update the Systemd Service File**

   Edit the llama-server systemd service to point to the new model:

   ```bash
   # Edit the service file
   systemctl --user edit llama-server
   ```

   Replace the `--model` path in the `ExecStart` line with your downloaded model path:

   ```ini
   [Service]
   ExecStart=%h/.local/bin/llama-server \
     --model %h/.cache/huggingface/hub/models--lmstudio-community--Qwen3.6-27B-GGUF/snapshots/[hash]/Qwen3.6-27B-Q4_K_M.gguf \
     --port 10000 \
     --n-gpu-layers 999 \
     --ctx-size 4096 \
     --host 0.0.0.0
   ```

   > **Tip:** Use `%h` for home directory expansion in systemd unit files.

4. **Restart the llama.cpp Service**

   ```bash
   # Reload systemd to pick up changes
   systemctl --user daemon-reload

   # Restart the service
   systemctl --user restart llama-server
   ```

5. **Verify the Model is Loaded**

   ```bash
   # Check service status
   systemctl --user status llama-server

   # View service logs
   journalctl --user -u llama-server -n 50

   # Follow logs in real-time (Ctrl+C to exit)
   journalctl --user -u llama-server -f

   # Test the API
   curl http://localhost:10000/v1/models
   ```

6. **Verify in Open WebUI**

   The llama.cpp connection should already be configured in Open WebUI (via `podman-compose.yml`). If not:
   - Go to Admin Settings → Connections → OpenAI
   - Add URL: `http://localhost:10000/v1`
   - Leave API Key empty
   - Test the connection
   - The Qwen model should appear in the model dropdown

### Cache Directory

Models are automatically cached in the standard Hugging Face directory:
```
~/.cache/huggingface/hub/
```

To see all cached models:
```bash
ls -lh ~/.cache/huggingface/hub/models--*/
```

### Other Model Operations

**Check Current Model Configuration**
```bash
systemctl --user cat llama-server | grep -A 10 "ExecStart"
```

**List Available Models via API**
```bash
curl http://localhost:10000/v1/models
```

**Check GPU Usage**
```bash
# View ROCm device in logs
journalctl --user -u llama-server -f | grep -i "device\|gpu\|rocm"
```

## Updating

### Update Podman Stack Images
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
- [llama.cpp GitHub](https://github.com/ggml-org/llama.cpp)
- [Qwen Model Hub](https://huggingface.co/Qwen)
- [Hugging Face CLI Documentation](https://huggingface.co/docs/hub/security-tokens)
