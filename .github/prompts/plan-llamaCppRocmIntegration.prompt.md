# llama.cpp ROCm Integration Plan

## Overview

Install llama.cpp locally (build from source) with ROCm support for AMD GPU acceleration, configure Ollama to run CPU-only, and integrate llama.cpp as an OpenAI-compatible backend for Open WebUI. Models will be managed via the standard Hugging Face cache at `~/.cache/huggingface/hub/`.

### Why Local Installation?
- **Avoids container GPU passthrough complexity** - ROCm device mapping in containers is problematic
- **Better performance** - no container overhead, direct device access
- **Easier debugging** - direct logs, no container inspection needed
- **User preference** - experienced GPU issues with Ollama in containers

### Why Hugging Face Cache?
- **Standard location** used by `huggingface-cli`, `transformers`, and other HF tools
- **Easy model management** with `huggingface-cli download` / `scan-cache` / `delete-cache`
- **Shared cache** between host tools and llama.cpp
- **Follows community best practices** for troubleshooting and tool integration

### Test Model
**Primary:** Qwen3.6 27B (Q4_K_M quantization - ~16GB, fits in 24GB VRAM with context)
**Fallback:** Qwen3.2 3B Instruct (Q4_K_M - ~2GB) for quick validation

---

## Implementation Steps

### Phase 1: Pre-Validation & Setup

#### 1. Verify ROCm environment (upfront validation)
```bash
# Check amdgpu kernel module loaded
lsmod | grep amdgpu

# Verify ROCm installed and GPU detected
rocm-smi
rocminfo | grep -i "gfx version"  # Should show 11.0.0 for RX 7900 XTX

# Check ROCm version (important for build compatibility)
rocminfo | grep "HSA Agent"
pacman -Q rocm  # or rocm-opencl-sdk

# Check device permissions
ls -l /dev/kfd /dev/dri/card0 /dev/dri/renderD128

# Verify user groups (need video, render)
groups | grep -E "video|render"
```

**Expected output:**
- `amdgpu` module loaded
- ROCm tools show GFX version 11.0.0 (Navi 31)
- ROCm version noted (e.g., 6.2.x)
- Devices `/dev/kfd` and `/dev/dri/renderD128` exist
- User in `video` and `render` groups

#### 2. Ensure Hugging Face cache directory exists
```bash
mkdir -p ~/.cache/huggingface/hub
```

#### 3. Configure Ollama CPU-only (systemd service)

**Option A: Environment override (preferred - idiomatic)**
```bash
# Create systemd override
systemctl --user edit ollama

# Add this in the editor:
[Service]
Environment="OLLAMA_NUM_GPU=0"
```

**Option B: Modify service file directly**
```bash
# Find service file
systemctl --user status ollama | grep Loaded

# Edit it
systemctl --user edit --full ollama

# Add Environment="OLLAMA_NUM_GPU=0" under [Service]
```

**Then restart:**
```bash
systemctl --user restart ollama
systemctl --user status ollama
```

**Verify CPU-only mode:**
```bash
# Ollama should still respond on :11434
curl http://localhost:11434/api/tags

# Check Ollama logs - should not mention GPU
journalctl --user -u ollama -n 50 | grep -i gpu
```

---

### Phase 2: Build llama.cpp with ROCm

#### 4. Clone llama.cpp repository
```bash
cd ~
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
```

#### 5. Build with ROCm support
```bash
# Clean any previous builds
make clean

# Build with ROCm (takes 5-10 minutes on Ryzen 9 7900)
make -j $(nproc) llama-server GGUF_ROCM=1

# Alternative: use cmake for more control
# cmake -B build -DGGML_ROCM=1
# cmake --build build --config Release
```

**Build validation:**
```bash
# Check binary exists
ls -lh llama-server

# Check ROCm linking
./llama-server --help | grep -i rocm

# Verify binary architecture
file llama-server  # Should show x86_64
```

#### 6. Install binary to accessible location
```bash
# Option A: Install to ~/.local/bin (recommended - idiomatic)
make install GGUF_ROCM=1 INSTALL_PREFIX=$HOME/.local

# Option B: Copy manually
cp llama-server ~/.local/bin/

# Verify in PATH
~/.local/bin/llama-server --version
```

**Note:** Arch Linux may require `sudo` for system-wide install. Prefer user-local install (`~/.local/bin`).

---

### Phase 3: Configuration & Integration

#### 7. Update `.env` file
Add these variables:
```bash
# llama.cpp server configuration
LLAMA_CPP_PORT=10000
LLAMA_CPP_MODEL_PATH=  # e.g., "owner/model-name:filename.gguf"
LLAMA_CPP_GPU_LAYERS=999
LLAMA_CPP_CTX_SIZE=4096
LLAMA_CPP_HOST=0.0.0.0
```

#### 8. Create llama.cpp systemd service (direct ExecStart - idiomatic)

**Service file:** `~/.config/systemd/user/llama-server.service`

```bash
systemctl --user edit --force llama-server
```

**Service content:**
```ini
[Unit]
Description=llama.cpp ROCm Server
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/llama-server \
  --port 10000 \
  --n-gpu-layers 999 \
  --ctx-size 4096 \
  --host 0.0.0.0
Environment=HSA_OVERRIDE_GFX_VERSION=11.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

**Note:** Direct ExecStart is preferred over wrapper script - more idiomatic, easier to troubleshoot via `systemctl cat llama-server`. Model path can be added to ExecStart when loading a model.

#### 9. Enable and start service
```bash
systemctl --user daemon-rereload
systemctl --user enable llama-server
systemctl --user start llama-server
systemctl --user status llama-server
```

#### 10. Update Open WebUI environment
Add to `podman-compose.yml` in `open-webui` service:
```yaml
    environment:
      - OLLAMA_BASE_URL=http://localhost:11434
      - SEARXNG_API_URL=http://localhost:${SEARXNG_PORT:-8411}
      - OPENAI_API_BASE_URL=http://localhost:${LLAMA_CPP_PORT:-10000}/v1
```

**Then restart Open WebUI:**
```bash
cd /home/jeppson/projects/local-llm
podman compose restart open-webui
```

---

## Verification Steps

### ✅ Phase 1: Infrastructure Validation (No GPU Load)

```bash
# 1. ROCm environment check
rocm-smi  # Should show GPU info
rocminfo | grep "GFX Version"  # Should be 11.0.0

# 2. Ollama CPU-only verification
curl http://localhost:11434/api/tags  # Should respond
journalctl --user -u ollama -n 20 | grep -i gpu  # Should NOT mention GPU

# 3. llama.cpp build verification
~/.local/bin/llama-server --version  # Should show version
~/.local/bin/llama-server --help | grep -i rocm  # Should mention ROCm

# 4. Systemd service check
systemctl --user status llama-server  # Should be active (even without model)

# 5. API endpoint responds (no model loaded yet)
curl -s http://localhost:10000/v1/models  # Should return empty list or 404
```

### ✅ Phase 2: GPU Model Loading Test (Qwen3.6 27B)

```bash
# 1. Download Qwen3.6 27B test model to HF cache
#    Q4_K_M quantization (~16GB) fits in 24GB VRAM with context
huggingface-cli download bartowski/Qwen-3.6-27B-GGUF Qwen-3.6-27B-Q4_K_M.gguf

# 2. Verify model in cache
huggingface-cli scan-cache | grep -i "Qwen-3.6"

# 3. Update llama-server service to load model
# Edit the service file:
systemctl --user edit llama-server

# Add model path to ExecStart:
[Service]
ExecStart=%h/.local/bin/llama-server \
  --model %h/.cache/huggingface/hub/models--bartowski--Qwen-3.6-27B-GGUF/snapshots/COMMIT_HASH/Qwen-3.6-27B-Q4_K_M.gguf \
  --port 10000 \
  --n-gpu-layers 999 \
  --ctx-size 4096 \
  --host 0.0.0.0

# 4. Restart llama-server
systemctl --user restart llama-server

# 5. Check logs for GPU loading
journalctl --user -u llama-server -n 50 | grep -i "rocm\|gpu\|loading"

# 6. Verify model appears in API
curl -s http://localhost:10000/v1/models | jq

# 7. Test chat completion
curl -s http://localhost:10000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen-3.6-27B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "Say hello in 10 words."}],
    "max_tokens": 50
  }' | jq -r '.choices[0].message.content'

# 8. Test via Open WebUI
#    - Open http://localhost:3000
#    - Go to ⚙️ Admin Settings → Connections → OpenAI
#    - Add connection: http://localhost:10000/v1 (no API key)
#    - Select Qwen model from dropdown
#    - Send test message
```

**Fallback: If Qwen3.6 fails, test with smaller model**
```bash
# Download Qwen3.2 3B (Q4_K_M ~2GB)
huggingface-cli download bartowski/Qwen-3.2-3B-Instruct-GGUF Qwen-3.2-3B-Instruct-Q4_K_M.gguf

# Update service with smaller model path and restart
# Then repeat steps 5-8
```

### ✅ Phase 3: Concurrent Operation Test

```bash
# 1. Verify both services running
systemctl --user status ollama llama-server

# 2. Ollama on CPU, llama.cpp on GPU
journalctl --user -u ollama -n 20 | grep -i gpu  # Should NOT mention GPU
journalctl --user -u llama-server -n 20 | grep -i gpu  # Should mention GPU

# 3. Test both APIs simultaneously
curl http://localhost:11434/api/tags &  # Ollama
curl http://localhost:10000/v1/models &  # llama.cpp

# 4. Monitor GPU usage
rocm-smi  # Should show llama.cpp using GPU, Ollama not
```

---

## Troubleshooting

### ROCm Not Detected

```bash
# Check device permissions
ls -l /dev/kfd /dev/dri/renderD128

# Check user groups
groups  # Should include video, render

# Try overriding GPU version
# Add to systemd service:
Environment=HSA_OVERRIDE_GFX_VERSION=11.0.0

# Check ROCm installation
rocminfo  # Should show GPU info
```

### Build Fails

```bash
# Clean and rebuild
make clean
make -j $(nproc) llama-server GGUF_ROCM=1 2>&1 | tee build.log

# Check for ROCm paths
grep -i "rocm\|amdgpu" build.log

# Verify ROCm development files
ls /opt/rocm/include  # or /usr/include/rocm

# Check ROCm version compatibility
# llama.cpp should match host ROCm version
rocminfo | grep "HSA Agent"
```

### Model Not Found

```bash
# Verify HF cache structure
ls -lh ~/.cache/huggingface/hub/

# Check model ID format
huggingface-cli scan-cache

# llama.cpp expects: ~/.cache/huggingface/hub/models--OWNER--MODEL/snapshots/COMMIT/model.gguf
# Use huggingface-cli scan-cache to find exact path
```

### GPU Memory Issues (OOM)

```bash
# Reduce GPU layers
LLAMA_CPP_GPU_Layers=50  # instead of 999

# Reduce context size
LLAMA_CPP_CTX_SIZE=2048  # instead of 4096

# Check VRAM usage
rocm-smi --showmeminfo vram
```

### Qwen3.6 27B Too Large

```bash
# If 27B model OOMs, use smaller quantization or fallback model:
# Option 1: Use Q3_K_S quantization (~13GB)
huggingface-cli download bartowski/Qwen-3.6-27B-GGUF Qwen-3.6-27B-Q3_K_S.gguf

# Option 2: Use Qwen3.2 3B (~2GB)
huggingface-cli download bartowski/Qwen-3.2-3B-Instruct-GGUF Qwen-3.2-3B-Instruct-Q4_K_M.gguf
```

---

## Architecture Changes

### Before
```
┌─────────────┐     ┌─────────────┐
│   Ollama    │◄────│ Open WebUI  │
│  (:11434)   │     │  (:3000)    │
│  (host GPU) │     └──────┬──────┘
└─────────────┘            │
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
│  (CPU only) │     │  (host net) │     │  (local)     │
└─────────────┘     └──────┬──────┘     └──────────────┘
                           │
                    ┌──────▼──────┐
                    │   SearXNG   │
                    │   (:8411)   │
                    │ (compose net│
                    └─────────────┘
```

---

## Model Management

```bash
# Download model to HF cache
huggingface-cli download bartowski/Qwen-3.6-27B-GGUF Qwen-3.6-27B-Q4_K_M.gguf

# Scan cache (shows sizes)
huggingface-cli scan-cache

# Delete from cache
huggingface-cli delete-cache

# Models referenced by: owner/repo:filename.gguf
# Stored in: ~/.cache/huggingface/hub/models--owner--repo/
```

---

## Notes

- **Build time:** 5-10 minutes on Ryzen 9 7900 - documented in README
- **ROCm version matching:** llama.cpp build must match host ROCm version - verified in Phase 1
- **Direct ExecStart:** Preferred over wrapper script - idiomatic systemd pattern, easier troubleshooting
- **No service ordering:** Ollama and llama.cpp are independent - no `After=ollama.service` needed
- **Qwen3.6 27B:** Primary test model (Q4_K_M ~16GB), fallback to Qwen3.2 3B if needed
- **Ollama CPU-only:** `OLLAMA_NUM_GPU=0` prevents GPU contention, allows concurrent operation
- **HF Cache:** Models stored in `~/.cache/huggingface/hub/` - standard location
- **Local installation:** Avoids container ROCm complexity, better performance
- **Backup:** This file is your restore point. Keep it in the repo!