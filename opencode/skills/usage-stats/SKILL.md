---
name: usage-stats
description: Pull ground-truth token usage and cost data from OpenCode's local stats command for financial calculations — burn rate, per-model cost, cache efficiency, TCO calibration. Use when analyzing token usage or spend, adjusting cost-model factors, or comparing assumed vs actual usage factors.
---

# Usage Stats — ground truth for financial calculations

`opencode stats` reads the local OpenCode session database and reports *recorded* usage: tokens (input / output / reasoning / cache read / cache write), cost per model, and cache efficiency. No API calls, no credentials, no estimation. This is the ground truth that synthetic cost factors must be calibrated against.

## Quick start

```sh
opencode stats --models --cost                    # human-readable, current year
opencode stats --days 30 --cost --models --json   # machine-readable window for calculations
```

## Command reference

| Flag | Effect |
|---|---|
| `--days N` | Rolling window of the last N days (`--days 0` = today) |
| `--year YYYY` | Calendar year |
| `--all` | Lifetime |
| `--project .` or `--project <id>` | Restrict to one project |
| `--models` | Per-model table: tokens, steps, cost |
| `--cost` | Cost & tokens section (includes `cached input` %) |
| `--tools` | Tool reliability (calls, failures, P50 durations) |
| `--limit N` | Rows shown in detailed sections |
| `--json` | Single JSON aggregate; stable shape for scripting |

Flags combine freely. Windows are the only time controls — there is no monthly grouping or embedded time series.

## Metrics to derive

From the `--json` shape (`tokens` block at top level; per model under `models[]` with its own `tokens` and `cost`):

- **Input fraction** = `input / (input + output)` — compare against the cost model's assumed input fraction.
- **Cached input %** = `cache.read / (cache.read + input)` — printed directly by `--cost`. This is the *comparable* cache metric for the cost model's assumed cache-hit fraction.
- **Cost per model** = `models[].cost` — recorded USD; no rate math needed.
- **Burn rate ($/mo)** = window `cost` ÷ window days × 30 — derive from `--days 30` and cross-check with `--days 90`.

## Caveats — do not misread the data

- **`cache.read` is cumulative, not a hit rate.** Every turn re-sends the conversation prefix, so the same cached tokens are counted each turn; raw `cache.read / input` routinely exceeds 100%. Use the normalized `cached input` percentage instead.
- **Local models report `cost: 0`** (Ollama etc.). Correct — the hardware is owned. Their cost belongs in an owned-hardware TCO view, not a cloud rate table. Do not let a cost-sorted view imply local inference is free.
- **`cache.write` is almost always 0** across models (one historical qwen3.6-plus-free anomaly). Semantics unconfirmed — do not build calculations on cache-write without first verifying what the field counts.
- **Reasoning tokens are a separate counter**, not folded into output for all providers; keep them distinct when comparing to pricing that bills output-only.

## Calibration workflow

1. Pull two windows: `opencode stats --days 30 --cost --models --json` and `opencode stats --all --cost --models --json`.
2. Derive the metrics above per model. Report per-model, not just aggregate — model-switching (e.g. GLM-5.2 vs Qwen vs Ollama) hides inside aggregates.
3. Prefer the recent window for forward-looking factors; the lifetime window for the long-run TCO view.
4. Compare real factors against the cost model's assumed factors — take the assumed values from the cost model being calibrated. Flag drift > 10 percentage points as material, and note the direction (assumption over- or under-states cost).
5. Feed adjusted factors back into the cost model and re-render; state which numbers changed and why.
