# Shared LLM Workstation — Retained Research

Distilled 2026-11-21 from `.scratch/handoff-shared-llm-workstation.md` (research complete 2026-11-19, calibrated 2026-11-20). The full handoff remains in place as reference until digestion; this is the durable subset worth keeping.

**Decision context:** shared workstation for two users, primary workload is frequent coding with OpenCode subagents serving local LLMs (27B-class at 4-bit), requiring parallelism (target 3 concurrent subagents @ 37k context). Mac Studio tiers compared against cloud branches. 7900 XTX (24 GB) baseline is not a candidate — caps at 1 subagent at 37k.

---

## 1. The core insight: memory bandwidth, not capacity, gates LLM generation

**For autoregressive generation, each output token requires reading the entire model from DRAM.** Generation is memory-bandwidth-bound, not compute-bound.

Per-token cost on a 27B model at 4-bit, 37k context: **~23.5 GB read** (18 GB model + 5.5 GB KV) vs **~54 GFLOP of compute**:

| | Compute time | Memory read | Bottleneck |
|:---|:---:|:---:|:---:|
| M5 Max (~70 TOPS, 614 GB/s) | ~0.8 ms | ~38 ms | **Memory** (~45×) |
| M5 Ultra (~140 TOPS, 1,200 GB/s) | ~0.4 ms | ~20 ms | **Memory** (~50×) |

On both tiers the math finishes before the read does — extra compute is wasted for generation.

### The bandwidth ceiling

```
tok/s ≈ bandwidth ÷ (model_bytes + KV_cache_bytes)
```

27B 4-bit @ 37k: ~23.5 GB/token
- M5 Max (614 GB/s): ~26 tok/s ceiling
- M5 Ultra (1,200 GB/s): ~51 tok/s ceiling

Direction is clear: **X% more bandwidth ≈ X% more throughput for a 27B-class model.** Real-world numbers land at ~70% of the raw ceiling (overheads, scheduling) — see §3.

### Where FLOPS *do* matter (the bound shifts)

| Workload | Bound by |
|:---|:---:|
| 27B generation (4-bit) | Memory |
| 27B **prefill** (long contexts) | Compute |
| 7B/14B generation | Mixed |
| Fine-tuning / training | Compute (and total memory first) |

### Longevity nuance (the moat shifts, not disappears)

Over a 3-year horizon the bottleneck does **not** fully migrate to compute (65–70% confidence), but the moat's **composition** shifts from bandwidth toward **capacity**:

- **MoE:** active params per token drop to ~3B (e.g. GLM-4.7-Flash, Qwen3.6 35B-A3B, gpt-oss-120b is 117B/5.1B) — only ~1.5–2 GB read per token. A 273 GB/s DGX Spark decodes gpt-oss-120b at 41 tok/s vs the 1,200 GB/s Mac's 34. **Bandwidth stops differentiating; the full expert set must still sit in RAM**, so unified *capacity* is what makes 100B+ MoE feasible desk-side.
- **Extreme quant:** post-training 2-bit still collapses; native ternary works but tops out at ~2B params. 4-bit remains the practical floor.
- **NCM/diffusion LLMs:** real (Mercury 2.5 in production at 1,100+ tok/s; Google's DiffusionGemma shipped June 2026) but API-locked and Haiku/Flash-class. A 27B-class open-weight diffusion coding model by ~2028 is what would break the moat.
- **KV compression (MLA/GQA):** shrinks KV everywhere equally — neutral, helps both branches.

**Synthesis: underwrite capacity, not bandwidth.** The Mac's known weak flank is compute (gpt-oss-120b decode falls to ~6 tok/s at long context where prefill/attention dominate). Mind-changers that would re-rate to a 2-year asset: open-weight NCM/diffusion coding model matching dense-27B by 2027–28; native ternary scaling past ~30B at FP16 parity; MoE active fraction <2B with no quality loss; agent-harness context caps standardizing below ~50K.

---

## 2. Hardware specs and costs (grounded)

### Specs

| | M5 Max (18c CPU / 40c GPU) | M5 Ultra (30c CPU / 64c GPU) |
|:---|:---|:---|
| Memory | 64 GB unified | 96 GB unified |
| Bandwidth | 614 GB/s | **1,200 GB/s** |
| Neural Engine | 16-core | 32-core |
| Form factors | MacBook Pro, Mac Studio | Mac Studio |
| Approx price | ~$3,799 | ~$5,499 |

> M5 Max also has a 32-core GPU tier @ 460 GB/s; the 40-core @ 614 GB/s is the comparison point.
> Apple specs: [M5 Max / M5 Ultra](https://support.apple.com/en-us/128107) · [MacBook Pro M5 Max](https://support.apple.com/en-us/126318)
> No M4 Ultra exists — Apple went M3 Ultra → M5 Ultra. M3 Ultra (819 GB/s) is the Ultra-class calibration anchor for benchmarks in §3.

### Pricing & TCO (verified Nov 2026)

- **M5 Ultra 96 GB / 1 TB base = $5,499** (shipped Sept 22, 2026) — the ~$5,500 ceiling is exact.
- **M5 Max 64 GB / 1 TB = ~$3,799** (36 GB base is $2,499 but too small for the workload).
- 256 GB tier +$4,000; 512 GB +$15,500 — both out of scope (budget ceiling locked at the 96 GB base).
- Base 1 TB storage suffices for a 100–200 GB model library; skip Apple SSD upgrades (external TB5 ~$100/TB).

**3-yr TCO (Ultra):** $5,499 + AppleCare+ $185 + electricity ~$420 (9 W idle / 385 W max, ~$11.50/mo at 8 h/day duty) − resale 40–50% (−$2,200–2,500) = **net ~$3,600–3,900 → ~$100–108/mo**.
**Max floor nets ~$65–75/mo.** Mac efficiency displaces ~$700 of electricity vs a 7900 XTX-class tower over 3 years.

**Resale:** 40–50% at 36 mo (M2 Ultra retained 58–70% at 35 mo; M1 Ultra 41–53% at 50 mo). Sell peer-to-peer — Apple Trade In pays 35–55% of market on Studios. The 2026 DRAM-shortage premium for high-RAM Macs is temporary; expect structural 15–18%/yr decay to reassert by 2027.

**Longevity:** 1,200 GB/s stays competent through the 3-yr window. Real risk is **capacity**, not bandwidth — 96 GB fits 27B + 70B-class models; 64 GB is tight if 100B+ quantized MoEs become the default coding model by year 3.

---

## 3. Real-world benchmarks (grounded, no subjective framing)

Measured anchors (27B-class 4-bit, ~16 GB):

| Setup | tok/s | Notes |
|:---|:---:|:---|
| M5 Ultra MLX single @512 ctx | 54.7 | 73% of bandwidth ceiling |
| M5 Ultra MLX single @32k prompt | 42.6 | prefill 1,526 t/s (NetworkChuck) |
| M5 Ultra llama.cpp `-np 8` | 10.9 each | Metal dense batching is bad |
| M5 Max oMLX single | 32.1 | 84% of ceiling |
| M3 Ultra llama.cpp 4-way batched | 9.0 each | Ultra-class calibration |

Real efficiency fraction is **~66–84% of the bandwidth ceiling (center ~70%)** — not the ~50% the original extrapolations implied.

Prefill, dense 27B: Ultra ~1,300–1,500 t/s @15–60k; Max ~950 t/s @4k.

### Corrected numbers for the target workload

Batching stack: **oMLX / Splash / vLLM-metal / TensorFold — avoid llama.cpp for multi-stream.**

| Scenario | Original est. | Corrected |
|:---|:---:|:---:|
| Ultra single @37k | ~32 | **~40–46** |
| Max single @37k | ~16 | **~26–32** (~22–24 llama.cpp) |
| Ultra 2-way @37k | ~32 each | ~28–32 each |
| Ultra 3-way @37k | ~32 each | **~22–28 each** (agg ~70–80) |
| Max 3-way @37k | ~16 each | ~13–16 each (agg ~40–48) |
| **Cold 37k prefill** | Ultra ~4 s / Max ~9 s | **Ultra ~25–30 s / Max ~45–55 s** |

Caveat: no direct 3-concurrent dense-27B @37k measurement on Ultra exists — interpolated from the M3 Ultra batch shape + physics + the anecdotal 96 GB report. Qwen3.8's hybrid attention (16/64 layers keep KV) may make the 5.5 GB/stream KV assumption ~4× too big, which would favor 3-way throughput.

---

## 4. Economic drivers — the core questions

### Decision matrix axes

| Axis | M5 Max 64 GB | M5 Ultra 96 GB | Cloud, open mid-tier (GLM-5.x / DeepSeek via HF) | Cloud, Claude-class (Bedrock Sonnet 5.5) |
|:---|:---|:---|:---|:---|
| Upfront capex | $3,799 | $5,499 | $0 (+ governance unblock) | $0 (+ TPM/budget/model grants) |
| Effective 3-yr $/mo (net of resale) | ~$65–75 | ~$100–108 | $10–140, usage-based, no asset | $32 (light, cached) – $552 (heavy, uncached) |
| Throughput, 3×37k subagents | ~13–16 each (agg ~40–48) | ~22–28 each (agg ~70–80) | not the constraint — our TPM cap is | same |
| Cold 37k prefill | ~45–55 s | ~25–30 s | seconds (provider-side) | seconds |
| 3-yr longevity | 64 GB tight if 100B+ MoE default by yr 3; 614 GB/s fine for MoE active reads | 96 GB fits 27B + 70B-class; capacity underwritten; compute is the weak flank at long ctx | elastic — always current models | elastic |
| Privacy | source never leaves | source never leaves | source leaves to DeepInfra/Together — no training, but sampled logging, no contractual ZDR | strong no-training at Sonnet-class; avoid Fable-class (30-day AWS retention) |
| Key risk | capacity wall by yr 3; prefill latency | prefill latency; compute flank | quality step-down vs Sonnet; our own SCP/budget governance stalls day one | cost blowout at heavy use; TPM friction |

### Synthesis (the six things that actually drive the decision)

1. **On price alone, open mid-tier cloud dominates**: $10–140/mo, no capex, never ages — and it's the like-for-like successor to the current `qwen3.6:27b` subagent stack (the primary agent already runs GLM-5.2 via HF daily — experiential data exists).
2. **The Mac's case is not price.** It buys: source never leaving the machine, no throttle/outage dependence, flat marginal cost at heavy use, and a ~$2,400 residual asset at year 3.
3. **The Ultra is the only configuration that beats Claude-class cloud at heavy use** (~$100/mo net vs $162–552/mo) — i.e., the Mac is also insurance against quality-tier escalation.
4. **Max vs Ultra**: the premium nets to ~$30/mo after resale — Ultra buys 2× decode speed, the capacity the MoE trend rewards, and 8-bit headroom. The Max's remaining case is a hard budget cap at ~$3.8k.
5. **Engine choice is as load-bearing as tier** for the local branch: MLX-family batching server with prefix caching; llama.cpp multi-stream measured ~11 tok/s each.
6. **Local overflow to cloud is a non-factor** ($20–150/yr realistic) — no hybrid machinery needed; a rare spill can ride the existing (unblocked) Bedrock path.

### The hinge question (decides the branch — user call, not answerable by research)

- What quality tier do the coding subagents actually need — is **open mid-tier** (GLM-5.x / DeepSeek class) adequate, given the current stack already runs a 27B open model locally and the primary agent runs GLM-5.2 via HF daily?
- How much weight does **source-code-leaving-the-machine** carry for this household's repos?

Open-mid-tier-adequate + privacy-light → cloud-only open route. Claude-class-at-heavy-use or privacy-heavy → M5 Ultra 96 GB local.

### Cost-per-million-tokens (calibrated 2026-11-20)

Household burn: **400–800M tok/mo** (per person 200–400M; husband assumed similar). Agent skew ~97% input / 3% output by context composition; **billed input share recorded at 88–95%** (97% overstates input, understates cost — input is cheaper than output). **~85% of input tokens hit the prompt-prefix cache** (prefix caching is load-bearing). Effective CPT = weighted mix of uncached-input, cache-read, and output rates.

| Route / model | List CPT (in/out) $/M | Effective CPT (cache where pub.) | $/mo @ 600M/mo |
|:---|:---:|:---:|:---:|
| DeepSeek V4.1 Flash (HF→DeepInfra) | $0.14 / $0.42 | **$0.05** (no-cache $0.15) | **$30** (no-cache $90) |
| DeepSeek V4 Flash (HF→DeepInfra) | $0.09 / $0.18 | **$0.03** (no-cache $0.09) | **$20** (no-cache $56) |
| Qwen3-Coder-480B (HF→DeepInfra) | $0.30 / $1.00 | **$0.16** (no-cache $0.32) | **$95** (no-cache $192) |
| GLM-5.2 (HF→DeepInfra) | $0.56 / $1.80 | **$0.22** (no-cache $0.60) | **$132** (no-cache $360) |
| Qwen3.8-27B (HF→DeepInfra) | $0.15 / $1.88 | **$0.20** (no-cache; cache n/a) | **$120** |
| Qwen3.6-27B — *current local model* (HF→DeepInfra) | $0.32 / $3.20 | **$0.41** (no-cache; cache n/a) | **$246** |
| Mistral Small 3.2 24B (HF→DeepInfra) | $0.075 / $0.20 | **$0.08** (no-cache) | **$48** |
| **M5 Ultra 96 GB — local** | — flat capex ~$100–108/mo | **~$0.17/M** (0.13–0.27 across burn) | flat ~$104 (not token-gated) |
| **M5 Max 64 GB — local** | — flat capex ~$65–75/mo | **~$0.11/M** (0.08–0.19 across burn) | flat ~$70 (not token-gated) |
| Bedrock Sonnet 5.5 *(ref, closed)* | $3.00 / $15.00 ($0.30 cache) | ~$0.70 (cached) / ~$2.40 (no-cache) | ~$430 / ~$1,450 |
| Bedrock Nova Pro / 2 Lite *(ref, closed)* | — | ~$0.4–0.85 | ~$234–510 |

> $/mo shown at 600M/mo; scale ×0.67 / ×1.33 for the 400/800M endpoints. List CPTs: DeepInfra/HF Inference list prices (Nov 2026), no HF markup. Sonnet/Nova re-derived from 10-turn ≈ 380k in/out session math (2 users). Local CPT = net 3-yr capex ÷ household burn.
> **HF pricing drifts frequently — treat the table as the *directional* ranking (flash class < Mac ≤ mid-tier open << Claude-class), not as precise absolute $/mo.**

---

## 5. Tracking usage with `opencode stats` — pointers for a future agent

The ground-truth source for token usage and cost is **OpenCode V2's native `opencode stats` command** — no API calls, no credentials, reads the local session DB.

### Where the knowledge lives

- **`opencode/skills/usage-stats/SKILL.md`** — repo-local skill, progressive disclosure. Documents the flags, the derived metrics, the cache-read-cumulative caveat, the local-`cost: 0` tier question, and the calibration workflow. **Deliberately decoupled from any calculator path or factor value so it stays durable** — read this first if you want to re-pull or re-calibrate.
- **`scratch/token-burn-calculator.py`** — pure-Python synthetic CPT renderer. Defaults calibrated 2026-11-20 (`--input 0.90`, `--cache 0.85`). CLOUD/LOCAL/REFERENCE blocks encode the list rates and TCO components from this doc. Re-render with:
  ```
  python3 scratch/token-burn-calculator.py [burn] --input F --cache F
  ```
  `scratch/` (no dot) is **permanent user scratch — not agent-disposable**. The calculator is described for this research's use but is **not to be edited further or maintained as an artifact** after the research closes.

### Flags worth knowing

`--days N` / `--year` / `--all` (window) · `--models` (per-model breakdown) · `--cost` (recorded spend) · `--json` (machine-readable). Combine as `opencode stats --days 30 --cost --models --json`.

### Derived metrics (per the skill)

- `input fraction = input / (input + output)` — the calculator's `--input` denominator
- `cached input % = cache.read / (cache.read + input)`
- `billable IF = input / (input + output + reasoning)` — for the case where reasoning is billed at the output rate (unconfirmed for DeepInfra)
- Compare against defaults (97% input / 85% cache); flag **>10pp drift as MATERIAL**

### Calibration workflow

Pull `--all` (lifetime), `--days 90`, `--days 30`, each with `--cost --models --json`. Compute the derived metrics for each window and compare against the calculator's defaults. Update `--input` / `--cache` only when a window shows MATERIAL drift that is **forward-looking** (not a historical-drag artifact).

### Caveats a future agent must respect

- **Usage is irregular and history is short** (75 active days lifetime, 17 in the last 30 at calibration time) — treat numbers as ballpark, not a clean signal. Do not over-fit factor values to one window.
- **Cache-read is cumulative** — look at ratios over windows, not raw cumulative numbers. The lifetime 69.8% cache hit is a known historical-drag artifact (older sessions before prefix caching was load-bearing); the forward-looking factor is the recent ~83–88%.
- **`cost: 0` rows on local providers** — confirm with the user whether that's truly free or a recording gap.
- **Don't trust absolute $/mo blindly.** HF provider pricing drifts frequently; the load-bearing output of `opencode stats` calibration is the *directional* ranking and the factor values (input share, cache hit), not precise absolute spend. If absolute dollars matter for a decision, cross-check the recorded rate against the current list price at that moment rather than treating either as fixed.
- **The skill is durable; the calculator is user-owned permanent scratch** — not agent-disposable, not maintained. Don't fold the skill's command knowledge into the calculator or vice versa; keep them decoupled so factor changes don't orphan the skill.

---

## Branches locked (2026-11-19) — for reference

1. **Budget ceiling:** M5 Ultra 96 GB base (~$5,500). 256/512 GB tiers and FP16-only models out of scope.
2. **Two independent branches** (hybrid framing dropped):
   - **Local-only** — load-bearing question: cloud overflow frequency (resolved — negligible, $20–150/yr).
   - **Cloud-only** — load-bearing question: security/privacy/access constraints + steady-state monthly cost.
3. **Throughput target:** 3 concurrent subagents @ 37k context.
4. **Longevity:** 3-year asset, reassess at year 4. NCM/compute-migration risk tracked but does not gate the purchase — if compute migrates to cloud by year 3, the Mac has already amortized most of its bandwidth-bound value.

PC branch closed. M5 Max is the budget floor (~$3,799); M5 Ultra is the ceiling (~$5,499).
