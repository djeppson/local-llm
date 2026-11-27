# dj7900 — primary LLM host

EndeavourOS (Arch-based) workstation and the host for the local LLM stack. Hostname: `endeavor-7900`.

## Hardware (summary)

- **CPU:** AMD Ryzen 9 7900 12-Core (24 threads)
- **GPU:** AMD Radeon RX 7900 XTX 24GB (gfx1100 / Navi 31, ROCm)
- **RAM:** 32GB DDR5 6000MHz
- **Storage:** 2× Samsung 990/980 PRO 2TB NVMe + 1× Samsung 840 EVO 250GB (USB)
- **Board:** Gigabyte B650 AORUS ELITE AX

Full inventory (motherboard, boot, peripherals, USB) lives in [`system-summary.md`](./system-summary.md).

## Live diagnostics

> Note (2026-11-26): Ollama runs as a **system** unit (`/etc/systemd/system/ollama.service`, official binary) bound to `127.0.0.1:11434` with KV-cache/flash-attention tuning in a drop-in — see [`docs/ollama.md`](../../docs/ollama.md). Prior notes described a stale layout (a `0.0.0.0` bind with firewalld, later a user unit with `HSA_OVERRIDE_GFX_VERSION`); both are retired.

## Setup & how-tos

- [`setup.md`](./setup.md) — initial hardware install, dev env, integrations
- [`customization.md`](./customization.md) — boot, WoL, OpenRGB/CoolerControl/CoreCtrl
- [`terminal.md`](./terminal.md) — cargo apps, starship, terminal notes
- [`audio.md`](./audio.md) — audio streaming (listener/receiver, Sonos)
- [`nginx.md`](./nginx.md) — local nginx proxy for cargo-lambda
- [`containers.md`](./containers.md) — Podman + startup
- [`kbd67mkiirgbv3.layout.json`](./kbd67mkiirgbv3.layout.json) — kbd67 physical keyboard layout

## Related

- Stack setup and day-2 operations: [`docs/`](../../docs/)
- Point-in-time stack baseline: [`telemetry/`](../../telemetry/)
