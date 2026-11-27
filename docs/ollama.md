# Ollama on dj7900

How Ollama is set up on the primary LLM host. Verified live 2026-11-26.

## TL;DR

- **What** — Ollama serving local GGUF models (official binary, ships its own ROCm 7.2)
- **How it runs** — **system** systemd unit `ollama` (`/etc/systemd/system/ollama.service`), enabled + active, runs as user `ollama`
- **Bind** — `127.0.0.1:11434` (loopback only; not reachable over the LAN)
- **GPU** — Radeon RX 7900 XTX (gfx1100) via ROCm, `HIP_VISIBLE_DEVICES=0`; gfx1100 is supported natively, no `HSA_OVERRIDE_GFX_VERSION` needed
- **Tuning** — `OLLAMA_KV_CACHE_TYPE=q4_0`, `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_CONTEXT_LENGTH=64000`, `OLLAMA_KEEP_ALIVE=30m` (set in the unit file)
- **Models** — stored in `/var/lib/ollama/.ollama/models` (~91 GB on 2026-11-26). Live list at `http://localhost:11434/api/tags`.
- **APIs** — Ollama `http://localhost:11434`; OpenAI-compatible `http://localhost:11434/v1`

## Service unit

`/etc/systemd/system/ollama.service` — the tuning formerly in the drop-in `ollama.service.d/00-defaults.conf` was consolidated into this file on 2026-11-26; no drop-ins remain:

```ini
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="HIP_VISIBLE_DEVICES=0"
Environment="OLLAMA_KV_CACHE_TYPE=q4_0"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_CONTEXT_LENGTH=64000"
Environment="OLLAMA_KEEP_ALIVE=30m"

[Install]
WantedBy=default.target
```

`OLLAMA_HOST` is deliberately unset: the default bind is loopback `127.0.0.1:11434`. `OLLAMA_HOME` is likewise unset — it resolves from the `ollama` user's home directory, which is `/var/lib/ollama` (see `getent passwd ollama`), so the model store lands at `/var/lib/ollama/.ollama/models`.

The repo ships an `ollama.service` symlink to the live system unit (see repo root).

## Day-2 operations

```sh
# Status / logs
systemctl status ollama
journalctl -u ollama -f

# Restart (needs root)
sudo systemctl restart ollama

# Edit the unit directly (then daemon-reload + restart)
sudo $EDITOR /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Loaded models
curl -s http://localhost:11434/api/tags | jq
```

## Install history (Arch / EndeavourOS)

- **Original (2025–2026):** AUR `ollama` + `ollama-rocm`, running as a user unit (`~/.config/systemd/user/ollama.service`, since removed).
- **2026-11-26:** consolidated to the **official binary** at `/usr/local/bin/ollama` under a **system** unit; AUR packages removed; tuning folded into the main unit file (drop-in retired); `HSA_OVERRIDE_GFX_VERSION` dropped (binary 0.40.18 / bundled ROCm 7.2 supports gfx1100 natively — verified `100% GPU` without it); leftover `~/ollama` store (incl. the only qwen3.5 27b copy — re-pull from the registry if ever needed) deleted.

References:

- [Arch wiki — Ollama](https://wiki.archlinux.org/title/Ollama)

## Gotchas

- **Do not** bind to `0.0.0.0` or open firewalld ports for Ollama on this host. An earlier notes guide documented that layout (`/etc/systemd/system/...`, `0.0.0.0:11434`, firewalld `11434/tcp`) — it is **stale and reverted**. The live unit is loopback-only by design. LAN access for Open WebUI is handled by Open WebUI's host networking + nginx, not by Ollama's bind.
- **Do not attempt to disable amdgpu power management** (`runpm=0`/`dpm=0`) — it froze the system at boot on this board. See [`machine/dj7900/system-summary.md`](../machine/dj7900/system-summary.md).
- The `llama-server` process Ollama spawns (on an ephemeral port, e.g. `:39299` at the time of observation) is the bundled runner, not a standalone server. (A standalone `llama-server.service` unit was trialed 2026-11-17 and removed 2026-11-21 when the standalone llama.cpp track was abandoned; Ollama is the sole GGUF runner on this host.)
