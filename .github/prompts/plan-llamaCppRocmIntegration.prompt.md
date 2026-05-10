# llama.cpp ROCm Integration Plan

## Overview

Add a llama.cpp server container with ROCm (AMD GPU) support to the existing `podman-compose.yml`. Keep Ollama as the primary model manager, and add llama.cpp as an alternative OpenAI-compatible connection in Open WebUI. Models will be managed via the standard Hugging Face cache at `~/.cache/huggingface/`.

### Why Hugging Face Cache?
- **Standard location** used by `huggingface-cli`, `transformers`, and other HF tools
- **Easy model management** with `huggingface-cli download` / `scan-cache` / `delete-cache`
- **Shared cache** between host tools and container
- **Follows community best practices** for troubleshooting and tool integration
- **llama.cpp `-hf` flag** loads models directly from HF cache by model ID

### Critical Constraint
**Ollama is actively using the dedicated GPU.** Loading another model on the same GPU risks OOM/crash. GPU testing requires stopping Ollama first.

---

## Implementation Steps

### Phase 1: Infrastructure Setup

#### 1. Ensure Hugging Face cache directory exists
```bash
mkdir -p ~/.cache/huggingface/hub
```

#### 2. Add llama.cpp service to `podman-compose.yml`
Add this service block:
```yaml
  llama-server:
    container_name: llama-server
    image: ghcr.io/ggml-org/llama.cpp:server-rocm
    restart: unless-stopped
    network_mode: host
    volumes:
      - ${HF_HOME:-$HOME/.cache/huggingface}:/hf:Z  # Mount HF cache
    devices:
      - /dev/kfd
      - /dev/dri
    environment:
      - HSA_OVERRIDE_GFX_VERSION=11.0.0  # Adjust for your AMD GPU if needed
      - HF_HUB_CACHE=/hf/hub  # Tell HF tools where cache is inside container
    # No command override by default — lets the entrypoint start the server
    # with no model loaded. Add a command override (below) when you want
    # to load a specific model.
```

> **Note:** The image's entrypoint runs `llama-server` directly. To load a model, override with:
> ```yaml
>    command: >
>      --model /hf/hub/models--OWNER--MODEL/snapshots/COMMIT_HASH/model.gguf
>      --port ${LLAMA_CPP_PORT:-10000}
>      --n-gpu-layers ${LLAMA_CPP_GPU_LAYERS:-999}
>      --ctx-size ${LLAMA_CPP_CTX_SIZE:-4096}
>      --host 0.0.0.0
> ```
> Or use the `-hf` flag to load by model ID directly from cache:
> ```yaml
>    command: >
>      -hf owner/model-name:filename.gguf
>      --port ${LLAMA_CPP_PORT:-10000}
>      --n-gpu-layers ${LLAMA_CPP_GPU_LAYERS:-999}
>      --ctx-size ${LLAMA_CPP_CTX_SIZE:-4096}
>      --host 0.0.0.0
> ```
> Arguments after `command:` are passed directly to the entrypoint's `llama-server` binary. Verify with:
> ```bash
> podman run --rm ghcr.io/ggml-org/llama.cpp:server-rocm --help
> ```

#### 3. Update `.env`
Add these variables:
```bash
# llama.cpp server configuration
LLAMA_CPP_PORT=10000
LLAMA_CPP_MODEL_PATH=  # e.g., "owner/model-name:filename.gguf" for -hf flag
LLAMA_CPP_GPU_LAYERS=999
LLAMA_CPP_CTX_SIZE=4096
```

#### 4. Update Open WebUI environment
Add to the `open-webui` service in `podman-compose.yml`:
```yaml
    environment:
      - OLLAMA_BASE_URL=http://localhost:11434
      - SEARXNG_API_URL=http://localhost:${SEARXNG_PORT:-8411}
      - OPENAI_API_BASE_URL=http://localhost:${LLAMA_CPP_PORT:-10000}/v1
```

---

## Verification Steps

### ✅ Safe Verification (No GPU Load - Run These First)

These steps validate infrastructure without loading models onto the GPU:

```bash
# 1. Start the llama.cpp container (no model loaded)
cd /home/jeppson/projects/local-llm
podman compose up -d llama-server

# 2. Check container is running
podman ps --filter name=llama-server

# 3. Check logs for ROCm device detection (happens at startup, before model load)
podman logs llama-server | grep -i "rocm\|gpu\|device"

# 4. Test API endpoint responds (should return empty list or 404 - no model loaded yet)
curl -s http://localhost:10000/v1/models

# 5. Test Open WebUI connection
#    - Open http://localhost:3000
#    - Go to ⚙️ Admin Settings → Connections → OpenAI
#    - Click "Add Connection"
#    - URL: http://localhost:10000/v1
#    - API Key: (leave blank)
#    - Click "Save"
#    - Connection should verify successfully (or show warning about /models endpoint)
```

If all 5 steps pass, the infrastructure is solid. You can now proceed to GPU testing.

---

### ⚠️ GPU Verification (Requires Stopping Ollama)

**WARNING:** These steps require stopping Ollama, which will also stop this AI assistant. Follow these instructions carefully.

#### Pre-Test Checklist
- [ ] Safe verification steps 1-5 completed successfully
- [ ] You have a small test model in HF cache (e.g., `llama-3.2-3b-instruct.Q4_K_M.gguf` ~2GB)
- [ ] You know how to restart Ollama after testing

#### Step-by-Step GPU Test

```bash
# 1. STOP Ollama (this will stop the AI assistant)
systemctl --user stop ollama

# 2. Verify Ollama is stopped
systemctl --user status ollama

# 3. Download a small test model to HF cache (if you don't have one)
#    This downloads to ~/.cache/huggingface/hub/ automatically
huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf

# 4. Update `podman-compose.yml` to add the model via `command:` override
#    Uncomment or add the `command:` block in the `llama-server` service:
#    command: >
#      -hf TheBloke/Llama-2-7B-GGUF:llama-2-7b.Q4_K_M.gguf
#      --port 10000
#      --n-gpu-layers 999
#      --ctx-size 4096
#      --host 0.0.0.0

# 5. Restart llama.cpp container with the model
podman compose up -d llama-server

# 6. Check logs for successful model loading on GPU
podman logs llama-server | grep -i "loading model\|gpu\|rocm"

# 7. Verify model appears in API
curl -s http://localhost:10000/v1/models | jq

# 8. Test chat completion
curl -s http://localhost:10000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-2-7b.Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "Say hello in 10 words."}],
    "max_tokens": 50
  }' | jq -r '.choices[0].message.content'

# 9. Test via Open WebUI
#    - Open http://localhost:3000
#    - Select the llama.cpp model from the dropdown
#    - Send a test message
#    - Verify response streams back

# 10. CLEAN UP: Stop llama.cpp and restart Ollama
podman compose stop llama-server
systemctl --user start ollama

# 11. Verify Ollama is back up
systemctl --user status ollama
```

#### Troubleshooting GPU Issues

**ROCm not detected:**
```bash
# Check if devices are accessible
ls -l /dev/kfd /dev/dri

# Check ROCm version compatibility
podman logs llama-server | grep -i "error\|fail\|rocm"

# Try overriding GPU version (add to .env)
HSA_OVERRIDE_GFX_VERSION=11.0.0
```

**Out of Memory (OOM):**
```bash
# Reduce GPU layers
LLAMA_CPP_GPU_LAYERS=50  # instead of 999

# Reduce context size
LLAMA_CPP_CTX_SIZE=2048  # instead of 4096
```

**Model not found:**
```bash
# Verify HF cache is mounted correctly in container
podman exec llama-server ls -lh /hf/hub/

# Check what's in your HF cache on the host
huggingface-cli scan-cache

# Verify model ID and filename are correct
huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf --local-dir-use-symlinks=False

# Check .env variable matches exact model ID:filename format
cat /home/jeppson/projects/local-llm/.env | grep LLAMA_CPP_MODEL_PATH
```

---

## Post-Test Cleanup

After GPU testing, you can:
1. Keep `LLAMA_CPP_MODEL_PATH` empty in `.env` to run without a model
2. Set it to your preferred model for persistent use
3. Use Open WebUI to switch between Ollama and llama.cpp connections as needed

---

## Architecture Changes

### Before
```
┌─────────────┐     ┌─────────────┐
│   Ollama    │◄────│ Open WebUI  │
│  (:11434)   │     │  (:3000)    │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   SearXNG   │
                    │   (:8411)   │
                    └─────────────┘
```

### After
```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Ollama    │◄────│ Open WebUI  │◄────│ llama.cpp    │
│  (:11434)   │     │  (:3000)    │     │ (:10000) ROCm│
│  (host)     │     │  (host net) │     │  (host net)  │
└─────────────┘     └──────┬──────┘     └──────────────┘
                           │
                    ┌──────▼──────┐
                    │   SearXNG   │
                    │   (:8411)   │
                    │ (compose net│
                    └─────────────┘
```

---

## Ollama CPU-Only Mode

To give llama.cpp full GPU access while keeping Ollama running:

```bash
# Set Ollama to CPU-only, then restart
export OLLAMA_NUM_GPU=0
systemctl --user restart ollama
```

With `OLLAMA_NUM_GPU=0`, Ollama stays responsive on `:11434` but does all inference on CPU. This lets Open WebUI switch between Ollama (CPU) and llama.cpp (GPU) without stopping either service. CPU inference will be slower but functional.

---

## Model Management with Hugging Face CLI

The standard HF cache makes model management straightforward:

```bash
# Install huggingface-cli (if not already installed)
pip install -U huggingface_hub

# Download a model to the HF cache
huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf

# See what's in your cache (with sizes)
huggingface-cli scan-cache

# Delete a specific revision/model from cache
huggingface-cli delete-cache

# Set HF_HOME if you want a custom location (default: ~/.cache/huggingface)
export HF_HOME=/path/to/custom/cache
```

Models in the cache can be referenced in llama.cpp using the `-hf` flag with format:
`owner/repo:filename.gguf`

---

## Notes

- **ROCm vs CUDA:** ROCm is for AMD GPUs. If you have NVIDIA, use `server-cuda` image instead
- **Model switching:** llama.cpp loads one model at a time. Change `LLAMA_CPP_MODEL_PATH` in `.env` and restart container
- **GPU contention:** Never run Ollama and llama.cpp with GPU models loaded simultaneously on the same GPU. Use `OLLAMA_NUM_GPU=0` to run Ollama on CPU while llama.cpp uses the GPU
- **Binary path:** The container image installs `llama-server` in PATH — do **not** use `./build/bin/llama-server` (that's a dev build path)
- **HF Cache:** Models are stored in `~/.cache/huggingface/hub/` and mounted into the container at `/hf`. This enables seamless integration with `huggingface-cli` and other HF tools
- **Backup:** This file is your restore point. Keep it in the repo!