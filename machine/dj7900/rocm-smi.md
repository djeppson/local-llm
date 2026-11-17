# ROCm state — dj7900

Point-in-time captures of the GPU/ROCm stack state on `endeavor-7900`. This is a snapshot layer (like `telemetry/`), not runbook prose: re-capture instead of editing old entries.

## How to capture

```sh
rocm-smi
```

(The leading `Exception caught: map::at` line has been a cosmetic rocm-smi quirk; the table below it is the data.)

Newest capture first.

## Capture — 2026-11-17

```
==================================================== Concise Info ====================================================
Device  Node  IDs              Temp    Power    Partitions          SCLK  MCLK     Fan     Perf  PwrCap  VRAM%  GPU%
              (DID,     GUID)  (Edge)  (Avg)    (Mem, Compute, ID)
======================================================================================================================
0       1     0x744c,   4672   55.0°C  7.0W     N/A, N/A, 0         0Mhz  96Mhz    28.63%  auto  291.0W  87%    0%
1       2     0x164e,   60157  45.0°C  21.221W  N/A, N/A, 0         N/A   2400Mhz  0%      auto  N/A     4%     0%
```

Note: device 0 (RX 7900 XTX) showing 87% VRAM is expected in this window — Ollama's bundled `llama-server` had `bonsai-2:27b` resident (see [`telemetry/baseline-2026-11-17.md`](../../telemetry/baseline-2026-11-17.md)).
