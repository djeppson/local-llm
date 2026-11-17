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

- **ROCm/GPU state:** [`rocm-smi.md`](./rocm-smi.md) — point-in-time captures; re-capture with `rocm-smi`.

## Related

- Stack setup and day-2 operations: [`docs/`](../../docs/)
- Point-in-time stack baseline: [`telemetry/`](../../telemetry/)
