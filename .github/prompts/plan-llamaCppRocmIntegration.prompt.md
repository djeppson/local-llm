# llama.cpp ROCm Integration Plan

## Overview

Add a llama.cpp server container with ROCm (AMD GPU) support to the existing `podman-compose.yml`. Keep Ollama as the primary model manager, and add llama.cpp as an alternative OpenAI-compatible connection in Open WebUI. Models will be stored in `models/`.

### Critical Constraint
**Ollama is actively using the dedicated GPU.** Loading another model on the same GPU risks OOM/crash. GPU testing requires stopping Ollama first.

---

## Implementation Steps

### Phase 1: Infrastructure Setup

#### 1. Create models directory
```bash
mkdir -p /home/jeppson/projects/local-llm/models
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
      - ./models:/models:Z
    devices:
      - /dev/kfd
      - /dev/dri
    environment:
      - HSA_OVERRIDE_GFX_VERSION=11.0.0  # Adjust for your AMD GPU if needed
      - LLAMA_CPP_PORT=${LLAMA_CPP_PORT:-10000}
      - LLAMA_CPP_MODEL_PATH=${LLAMA_CPP_MODEL_PATH:-}
      - LLAMA_CPP_GPU_LAYERS=${LLAMA_CPP_GPU_LAYERS:-999}
      - LLAMA_CPP_CTX_SIZE=${LLAMA_CPP_CTX_SIZE:-4096}
    command: >
      bash -c '
        if [ -n "$$LLAMA_CPP_MODEL_PATH" ] && [ -f "/models/$$LLAMA_CPP_MODEL_PATH" ]; then
          ./build/bin/llama-server \
            --model "/models/$$LLAMA_CPP_MODEL_PATH" \
            --port $$LLAMA_CPP_PORT \
            --n-gpu-layers $$LLAMA_CPP_GPU_LAYERS \
            --ctx-size $$LLAMA_CPP_CTX_SIZE \
            --host 0.0.0.0 \
            --log-disable
        else
          echo "No model specified or file not found. Server will start without a model."
          ./build/bin/llama-server \
            --port $$LLAMA_CPP_PORT \
            --host 0.0.0.0 \
            --log-disable
        fi
      '
```

#### 3. Update `.env`
Add these variables:
```bash
# llama.cpp server configuration
LLAMA_CPP_PORT=10000
LLAMA_CPP_MODEL_PATH=  # e.g., "llama-3.2-3b-instruct.Q4_K_M.gguf"
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
- [ ] You have a small test model downloaded (e.g., `llama-3.2-3b-instruct.Q4_K_M.gguf` ~2GB)
- [ ] You know how to restart Ollama after testing

#### Step-by-Step GPU Test

```bash
# 1. STOP Ollama (this will stop the AI assistant)
systemctl --user stop ollama

# 2. Verify Ollama is stopped
systemctl --user status ollama

# 3. Download a small test model (if you don't have one)
#    Option A: Using huggingface-cli (if installed)
huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf --local-dir /home/jeppson/projects/local-llm/models/

#    Option B: Using wget (direct link)
cd /home/jeppson/projects/local-llm/models
wget https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf

# 4. Update .env with the model filename
echo 'LLAMA_CPP_MODEL_PATH=llama-2-7b.Q4_K_M.gguf' >> /home/jeppson/projects/local-llm/.env

# 5. Restart llama.cpp container with the model
podman compose restart llama-server

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
# Verify file exists in container
podman exec llama-server ls -lh /models/

# Check .env variable matches exact filename
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
└─────────────┘     └──────┬──────┘     └──────────────┘
                           │
                    ┌──────▼──────┐
                    │   SearXNG   │
                    │   (:8411)   │
                    └─────────────┘
```

---

## Notes

- **ROCm vs CUDA:** ROCm is for AMD GPUs. If you have NVIDIA, use `server-cuda` image instead
- **Model switching:** llama.cpp loads one model at a time. Change `LLAMA_CPP_MODEL_PATH` in `.env` and restart container
- **GPU contention:** Never run Ollama and llama.cpp with models loaded simultaneously on the same GPU
- **Backup:** This file is your restore point. Keep it in the repo!