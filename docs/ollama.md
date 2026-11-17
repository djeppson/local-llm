# Ollama on dj7900

How Ollama is set up on the primary LLM host. Verified live 2026-11-17.

## TL;DR

- **What** — Ollama (ROCm build) serving local GGUF models
- **How it runs** — **user** systemd unit `ollama` (`~/.config/systemd/user/ollama.service`), enabled + active
- **Bind** — `127.0.0.1:11434` (loopback only; not reachable over the LAN)
- **GPU** — Radeon RX 7900 XTX (gfx1100) via ROCm, `HIP_VISIBLE_DEVICES=0`, `HSA_OVERRIDE_GFX_VERSION=11.0.0`
- **Tuning** — the unit sets KV-cache quantization, flash attention, a 64k context, and a 30-min keep-alive (exact values: the `ollama.service` symlink at repo root, or `systemctl --user cat ollama`)
- **Models** — stored in `~/.ollama/models`. Size is point-in-time state (latest snapshot in [`telemetry/`](../telemetry/), ~68 GB on 2026-11-17). Live list: `http://localhost:11434/api/tags`.
- **APIs** — Ollama `http://localhost:11434`; OpenAI-compatible `http://localhost:11434/v1`

## Service unit

Authoritative source: `~/.config/systemd/user/ollama.service`. The repo root ships an `ollama.service` **symlink** to that live file, so the in-repo file *is* the current unit — no copy is kept in this doc (a copy would drift). To read the unit exactly as systemd has it:

```sh
systemctl --user cat ollama
```

## Day-2 operations

```sh
# Status / logs
systemctl --user status ollama
journalctl --user -u ollama -f

# Restart
systemctl --user restart ollama

# Edit the unit (then daemon-reload + restart)
systemctl --user edit ollama
systemctl --user daemon-reload
systemctl --user restart ollama

# Loaded models
curl -s http://localhost:11434/api/tags | jq
```

## Install history (Arch / EndeavourOS)

```sh
yay -Syu ollama-rocm hip-runtime-amd
systemctl --user enable --now ollama
```

References:

- [Arch wiki — Ollama](https://wiki.archlinux.org/title/Ollama)
- Dual-ROCm env-var setup: <https://tkamucheka.github.io/blog/2026/02/08/ollama-dual-rocm-gpu/>

## Gotchas

- **Do not** bind to `0.0.0.0` or open firewalld ports for Ollama on this host. An earlier notes guide documented that layout (`/etc/systemd/system/...`, `0.0.0.0:11434`, firewalld `11434/tcp`) — it is **stale and reverted**. The live unit is loopback-only by design. LAN access for Open WebUI is handled by Open WebUI's host networking + nginx, not by Ollama's bind.
- **Do not attempt to disable amdgpu power management** (`runpm=0`/`dpm=0`) — it froze the system at boot on this board. See [`machine/dj7900/system-summary.md`](../machine/dj7900/system-summary.md).
- llama.cpp (`llama-server.service`) can run concurrently on the same GPU; see the [`handoff-llama-cpp-rocm.md`](../.scratch/handoff-llama-cpp-rocm.md) handoff for that integration. Note (2026-11-17): the standalone unit is written but **disabled/inactive**; the `llama-server` process on `:39299` is Ollama's bundled runner serving `bonsai-2:27b`, not the standalone server. Live check: `systemctl --user status llama-server` + `ss -ltn | grep 39299`.
