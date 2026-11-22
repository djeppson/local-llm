# Handoff — Shared LLM Workstation (M5 Max vs M5 Ultra vs Cloud)

**Status:** active — **research complete 2026-11-19** (A/B/D-local/D-cloud/E all reported; findings + decision matrix appended). Next: grill the hinge question (subagent quality tier + privacy weight), then branch decision. Decision space narrowed 2026-11-19 — four branches grilled and locked:

1. **Budget ceiling: M5 Ultra 96 GB base (~$5,500).** 256/512 GB upgrade tiers and FP16-only models out of scope. Cloud must beat ~$5,500 amortized.
2. **Two independent branches** (hybrid framing dropped 2026-11-19):
   - **Local-only:** load-bearing question is *cloud overflow frequency* — how often does the 4th subagent (or heavy-context prefill) spill to cloud at 3 concurrent @ 37k?
   - **Cloud-only:** load-bearing question is *security/privacy/access constraints* — what constraints apply to routing subagent traffic to Bedrock/HF, and what's the steady-state monthly cost for 3 concurrent cloud subagents?
3. **Throughput target: 3 concurrent subagents @ 37k context** (middle of handoff's 2–5 "frequent" range). Both branches sized for this.
4. **Longevity: 3-year asset, reassess at year 4.** NCM/compute-migration risk tracked (§10) but does not gate the purchase — if compute migrates to cloud by year 3, the Mac has already amortized most of its bandwidth-bound value.

PC branch remains **closed**. M5 Max is the budget floor (~$3,799, verified §E); M5 Ultra is the ceiling (~$5,500).

**Working style (this workstream):** agent makes edits as checkpoints for diff review; user commits when settled. No propose-and-review delay on handoff updates.

## Triage (2026-11-21)

**Decision: Keep.** Heaviest handoff (~42 KB) and only pure-research/decision track. Research complete across all 5 branches, decision matrix calibrated, sec-review PASSed. High residual value — abandoning would leave 42 KB of finished research with no recorded conclusion.

**Next step + LOE:** Resolve the two hinge items: (1) the rate discrepancy — recorded `huggingface` provider spend implies GLM-5.2 ~2.5× the calculator's DeepInfra-list numbers (recorded ~$2/M vs calc $0.56/M), which would flip cloud-vs-Mac at the mid-tier; confirm the route (HF-hosted vs DeepInfra-via-HF) via one `opencode stats` cross-check or HF billing/settings look-up. (2) Then grill the quality-tier/privacy hinge to lock the branch. **[S = <1hr]** — both items are confirmation/decision work, not new research; the analysis is already done.

**Dependencies:** Standalone — no other handoff depends on it, and it doesn't feed any other track. The `usage-stats` skill and `scratch/token-burn-calculator.py` are the persisted artifacts.

## Context

User is evaluating a **new shared workstation** for themselves and their husband. Primary use case: **frequent coding with OpenCode subagents** serving local LLMs (Ollama, 27B class models at 4-bit), requiring **parallelism** (2–5 concurrent subagents).

- **Ruled out:** M5 Pro tier (307 GB/s bandwidth insufficient).
- **Baseline:** current RTX 7900 XTX 24 GB (see baseline note below + `docs/vllm.md`).
- **Scope:** Mac Studio M5 Max/Ultra (Max=floor, Ultra=ceiling); cloud branches (Bedrock, HF Inference) as independent options. See Resolved Branches below.

## Baseline: current 7900 XTX (stated once)

The 7900 XTX is **not a candidate** for the shared workstation. Single-stream on a 27B 4-bit model is excellent (est. ~90 tok/s; measured smaller-model data in `docs/vllm.md`), but the **hard 24 GB ceiling** caps it at **1 subagent** at 37k context — the model (~18 GB) plus a second subagent's KV cache overflows to system RAM, and every stream collapses to ~2–5 tok/s. It serves well today as a single-user machine; for a 2-user parallel-subagent workstation the comparison is Mac Studio tiers only, and that is what the sections below analyze.

## 1. Specs

| | **M5 Max (18c CPU / 40c GPU)** | **M5 Ultra (30c CPU / 64c GPU)** |
|:---|:---|:---|
| **Memory** | 64 GB unified | 96 GB unified |
| **Bandwidth** | 614 GB/s | **1,200 GB/s** |
| **Neural Engine** | 16-core | 32-core |
| **Form factors** | MacBook Pro, Mac Studio | Mac Studio |
| **Approx price** | ~$3,799 | ~$5,499 |

> M5 Max also has a lower tier: 32-core GPU @ 460 GB/s. The 40-core tier at 614 GB/s is the comparison point.
> Apple specs: [M5 Max / M5 Ultra](https://support.apple.com/en-us/128107) · [MacBook Pro M5 Max](https://support.apple.com/en-us/126318)

## 2. Why FLOPS Don't Matter for Generation

The #1 non-obvious thing about local LLM inference: **generation is memory-bandwidth-bound, not compute-bound.** For each output token the accelerator must read the **entire model from DRAM** before writing the next token.

### Per-token cost (27B model, 4-bit, 37k context)

~23.5 GB read per token (18 GB model + 5.5 GB KV) vs ~54 GFLOP of compute:

| | Compute time | Memory read | **Bottleneck** |
|:---|:---:|:---:|:---:|
| M5 Max (~70 TOPS, 614 GB/s) | ~0.8 ms | ~38 ms | **Memory** (~45×) |
| M5 Ultra (~140 TOPS, 1,200 GB/s) | ~0.4 ms | ~20 ms | **Memory** (~50×) |

On both tiers the math finishes before the read does — **extra compute is wasted for generation**.

### The bandwidth ceiling

```
tok/s ≈ bandwidth ÷ (model_bytes + KV_cache_bytes)

27B 4-bit ≈ 18 GB model + 5.5 GB KV (37k context) = 23.5 GB
  M5 Max:    614 / 23.5  ≈  26 tok/s (ceiling)
M5 Ultra:   1200 / 23.5  ≈  51 tok/s (ceiling)
```

Real-world numbers land around or slightly under the raw ceiling (overheads, scheduling), but the **direction is clear**: X% more bandwidth ≈ X% more throughput for a 27B model.

### Where FLOPS DO matter

| Workload | Bound by |
|:---|:---:|
| 27B generation (4-bit) | Memory |
| 27B **prefill** (long contexts) | Compute |
| 7B/14B generation | Mixed |
| Fine-tuning / training | Compute *(and total memory first)* |

## 3. Benchmark Data (measured, 7900 XTX)

See [`docs/vllm.md`](../docs/vllm.md) for measured tok/s on the 7900 XTX via ROCm/vLLM:

| Model | 16K/1K (16 concurrent) | 1K/1K (24 concurrent) |
|:---|:---:|:---:|
| Qwen3.5-2B | 236 tok/s | — |
| Qwen3-8B | 89 tok/s | — |
| Qwen3.5-9B | 19 tok/s | — |
| Qwen2.5-Coder-14B-AWQ | 24 tok/s | 105 tok/s |
| Qwen2.5-Coder-14B-AWQ (LM-only) | — | 27 tok/s |

The 27B figures in this doc are **estimates** extrapolated from these (14B → 27B at 4-bit ≈ 30–40% lower at equal context) and from the bandwidth ceiling above: **~90 tok/s single-stream** on the 7900 XTX with Ollama's bundled runner. Mac numbers are pure extrapolation — see open branch 7.

## 4. Token Count Estimation

How to estimate context size for a planning/reorg session:

| Component | Typical tokens |
|:---|:---:|
| System prompt + tool schema (25 tools) | ~5,500 |
| AGENTS.md + CONTEXT.md + skills list | ~1,500 |
| Conversation history (user + assistant + tool results) | varies — see below |
| All 12 active handoffs + INDEX + notes | ~6,000 |
| Codebase slice (15–25 files) | ~5,000 |
| Web search / research results | ~3,000–5,000 |

**Light session (current convo, ~5 turns):** ~15,000 tokens
**Heavy session (reorg, all handoffs + codebase + research):** ~35,000–45,000 tokens
**By message 15–20 of a long session:** ~50,000+ tokens

### KV cache per subagent (27B 4-bit)

| Context | KV cache per subagent |
|:---|:---:|
| 15k tokens | ~2–3 GB |
| 37k tokens | ~5–6 GB |
| 50k tokens | ~7–8 GB |

Total memory = **model (18 GB) + N × (KV + response buffer)**.

## 5. Timing Analysis (M5 Max vs M5 Ultra)

### 15k context (still valid — prefill is fast at low context)

| Scenario | M5 Max 64 GB | M5 Ultra 96 GB |
|---|---|---|
| Single subagent (prefill + 1.5k stream) | ~31 s | ~16 s |
| 2 subagents (1k response each) | ~55 s each | ~27 s each |
| 3 subagents (1k response each) | ~80 s each | ~40 s each |

### 37k context (SUPERSEDED — see §B corrected numbers)

The §5a/5b/5c tables below were extrapolated from 15k + bandwidth ceiling. Real measurements (§B) showed the **cold 37k prefill gate is ~25–30 s on Ultra / ~45–55 s on Max** (not the ~4–9 s extrapolated), mitigated by prefix caching (89% hits, TTFT ~180 ms). Corrected per-subagent throughput: Max ~13–16 tok/s, Ultra ~22–28 tok/s. The "feel" summary (§8) is likewise superseded — the felt cost is the prefill gate, not the stream speed.

| Scenario | M5 Max (extrapolated) | M5 Ultra (extrapolated) | §B corrected |
|---|---|---|---|
| Single @37k total | ~29 s | ~14 s | Ultra ~50 s / Max ~75 s (prefill-dominated) |
| 2-way @37k, 1k response | ~60 s each | ~30 s each | ~28–32 s each (Ultra) |
| 3-way @37k, 1k response | ~60 s each | ~30 s each | ~22–28 s each (Ultra), ~13–16 each (Max) |

## 6. Shared Workstation Factor

Two people means **one extra subagent** the user didn't budget for.

| Platform | 3 subagents (37k) | + husband's session | **Usable for user** |
|:---|:---:|:---:|:---:|
| M5 Max | 3 × 60 s | 1 more subagent → 4 total | **2** (each ~15–18 tok/s) |
| M5 Ultra | 3 × 30 s | 1 more subagent → 4 total | **3–4** (each ~32–37 tok/s) |

The M5 Ultra's 96 GB means that after reserving subagents for both users, 50+ GB is still free for context growth, higher-precision models, or a third subagent.

## 7. Precision Tradeoff

| Precision | 27B size | 64 GB M5 Max | 96 GB M5 Ultra |
|:---|:---:|:---:|:---:|
| 4-bit Q4_K_M | ~18 GB | ✓ (3–4 subagents) | ✓ (5–6 subagents) |
| 8-bit Q8_0 | ~28 GB | ✓ (2 subagents) | ✓ (3–4 subagents) |
| FP16 | ~54 GB | ✗ (overflow) | ✓ (2 subagents) |

Running 8-bit on the M5 Ultra with 3 subagents: ~28 + 3×5.5 ≈ **44.5 GB** < 96 GB — comfortable. On the M5 Max 64 GB it fits but is tight.

## 8. The "Feel" Summary (SUPERSEDED — see §B / §5 corrected)

Superseded by the cold-prefill-gate finding (§B): the felt cost of a 37k session is the ~25–30 s Ultra / ~45–55 s Max cold first turn, not the stream speed. After prefill, prefix caching makes subsequent turns near-instant (TTFT ~180 ms). and all 3 Ultra streams run at/above reading speed; the M5 Max sits at "monitoring speed" (glance, can't follow). The 15k single-subagent feel (~16 s Ultra / ~31 s Max) remains valid as written.

## 9. Cost / Throughput Analysis (pre-calibration; see Decision Matrix for calibrated numbers)

| Platform | Approx. capex | Throughput at 3 subagents / 37k |
|---|---|---|---|
| M5 Max 64 GB | ~$3,799 | 3 × 13–16 tok/s = 39–48 tok/s total |
| M5 Ultra 96 GB | ~$5,499 | 3 × 22–28 tok/s = 66–84 tok/s total |

The M5 Ultra’s ~$1,700 premium over the M5 Max buys:
- 2× the usable subagents (after 2 users)
- 2× the per-subagent speed
- The ability to run 8-bit/FP16 models
- Headroom for 50k+ context conversations
- **No overflow wall**

## 10. 5-Year Horizon: The Crystal Ball (added 2026-11-18 — historical context for branch 4 decision)

> **Branch 4 decision (2026-11-19):** 3-year asset, reassess at year 4. NCM risk tracked but does not gate. The analysis below framed the longevity question; it is preserved as the reasoning that led to the decision, not as an open question for the next agent to re-grill.

The handoff's analysis (§§2–9) is sound **for the autoregressive workloads of today**. For a 5-year asset the question is whether that analysis stays valid long enough to amortize the capex. Three classes of model-architecture trend stress the current assumptions differently:

| Trend | Bottleneck shift | Hardware it rewards | Threat to Mac thesis |
|:---|:---|:---|:---|
| **MoE** (active-params-per-token) | Bandwidth ↓, **capacity** ↑ | Big unified memory | Moderate — Mac still wins on capacity; bandwidth edge erodes |
| **Extreme quant** (1.58/2-bit) | **Capacity** ↓ (smaller models) | Smaller memory pools | High — M5 Max may become "enough," weakens Ultra case |
| **NCM** (parallel coarse-to-fine) | Bandwidth ↓↓, **compute** ↑↑ | Raw FLOPS, elastic cloud | High — Mac's bandwidth moat depreciates; cloud compute becomes more attractive |
| **KV-cache compression** (MLA/GQA) | KV memory ↓ (more concurrency) | Any (neutral) | Low — helps both branches, doesn't decide |

**The synthesis question for the decision matrix:** Is the Mac a **5-year asset** (bandwidth+capacity moat holds through the trend window) or a **3-year asset** (NCM/compute migration makes cloud more attractive by year 3–4, at which point the remaining 2 years of Mac utility may not justify the capex)? This is the longevity axis the handoff previously lacked. It does not by itself decide Local vs Cloud, but it sets the *amortization horizon* each branch's numbers must be judged against.

**Source:** Stanford Hazy Research NCM blog + paper (arXiv:2610.14162), Oct 2026.

## Research Plan

See **Next Action** for the restaged plan (two independent branches: local-only, cloud-only). The original A/B/D/E subagent framing is preserved there with branch assignments.

## Current State (verified 2026-11-17)

- **Current live stack:** Ollama serving `qwen3.6:27b` on `:39299` (bundled runner, ~87% VRAM-resident on the 7900 XTX).
- **Model present in HF cache:** `lmstudio-community/Qwen3.6-27B-GGUF` (16 GB) — 143 GB cache, 21 model dirs, several near-dups of this model (see `handoff-hf-cache-cleanup.md`).
- **Ollama user-unit hardened** (see `handoff-hf-cache-cleanup.md` for context).
- **Llama.cpp ROCm standalone unit** was trialed but disabled/inactive; the standalone llama.cpp track was abandoned 2026-11-21 and the unit removed. Ollama is the sole GGUF runner on this host.

## Resolved Branches (2026-11-19 grill)

See **Status / Decision space narrowed** at the top of this handoff for the four locked branches (budget ceiling, branch structure, throughput target, longevity).

## Remaining Open Questions

- **Hinge question (decides the branch; not answerable by research — user call):** what quality tier do the coding subagents actually need — is open mid-tier (GLM-5.x/DeepSeek class) adequate, given the current stack already runs a 27B open model locally and the primary agent runs GLM-5.2 via HF daily? And how much weight does source-code-leaving-the-machine carry for this household's repos?
- **Answered 2026-11-19 (B):** real Apple Silicon benchmarks — §2/§5 decode numbers were pessimistic single-stream, roughly right 2-way, ~20–30% optimistic 3-way on Ultra; prefill 5–6× optimistic. The §5/§8 "feel" tables are superseded: the felt cost is the cold-turn prefill gate (~25–30 s Ultra), mitigated by prefix caching. Corrected numbers in Research Findings / Decision Matrix.
- **Model choice (still open, cheap to defer):** `qwen3.6:27b` vs `qwen3.8:27b` — B's data is all Qwen3.8-27B, whose hybrid attention (16/64 layers keep KV) may make the 5.5 GB/stream KV assumption ~4× too big, favoring 3-way throughput. 7B/14B exploration subagents worth testing once hardware exists.
- **5-year crystal ball (§10) — tracked, not gating:** updated by A — moat composition shifts bandwidth→capacity over the window; mind-changers for the year-4 reassessment are listed in Research Findings §A.

## Next Action

**Research complete 2026-11-19** — decision matrix appended above. Remaining sequence:

1. **Grill the hinge question** (one grill, not a barrage): subagent quality tier + privacy weight. Open-mid-tier-adequate + privacy-light → cloud-only open route. Claude-class-at-heavy-use or privacy-heavy → M5 Ultra 96 GB local.
2. **Branch decision** recorded in this handoff. If cloud: governance unblock (TPM ≥ 300k, budget $50–200/mo, model-access grants) is the first task — see `handoff-invoke-path.md` / `handoff-model-gate-guardrails.md`. If local: engine selection (MLX-family batching server + prefix caching; **not** llama.cpp multi-stream) is the first setup task.
3. Decision recorded → handoff moves to `pending-digestion`. Sec-review at digestion: waivable if the decision is a pure purchase (no infra artifacts); warranted if the cloud branch produced AWS governance changes.

Under the narrowed frame the executed plan was:

| # | Subagent | Branch served | Question |
|---|---|---|---|
| **A** | Model/arch trends over 5 years | Both (longevity context) | MoE / extreme-quant / NCM / KV compression — which hardware property each rewards; does NCM plausibly shift the bottleneck to compute by year 3? |
| **B** | Real Apple Silicon benchmarks | Local-only | Measured M5 Ultra tok/s for 27B-class 4-bit at 1–4 concurrency (MLX, llama.cpp, Ollama). Are §2/§5 extrapolations right, optimistic, or pessimistic? |
| **D-local** | Cloud overflow cost modeling | Local-only | At 3 concurrent @ 37k, how often does the 4th subagent (or heavy prefill) spill to cloud? Per-event cost on Bedrock/HF. Annual overflow spend. |
| **D-cloud** | Cloud-only steady-state + constraints | Cloud-only | Security/privacy/access constraints on routing subagent traffic to Bedrock/HF. Steady-state monthly cost for 3 concurrent cloud subagents. |
| **E** | Mac pricing/longevity | Both | M5 Ultra 96 GB TCO over 3 years; resale value. |

Append a **decision matrix** (Mac tier × cloud-spend-equivalent × throughput at 3 subagents × 3-year longevity) to this handoff when research completes.

## Research Findings (2026-11-19, all five complete)

### D-local — Cloud overflow cost model (complete)

**Verdict: overflow spend is negligible — $20–150/yr realistic, <$500/yr even at the extreme.** With 96 GB and 3 × 37k subagents using ~35 GB, the machine fits 4–6 concurrent subagents; a spill needs a 4th+ concurrent subagent or a >70k context — genuinely rare for 2 users. **The ~$1,700 Max→Ultra capex delta cannot be justified on spill economics** (payback would take decades); it must ride on speed, 8-bit precision, and headroom. Accepting rare spills is rational.

- Per-session overflow cost (8 turns, ~352k in + 8k out): Claude Sonnet 5.5 uncached ~$0.78 / **cached ~$0.22** (cache-read $0.10/M, 95% off); Qwen3 Coder 480B ~$0.17; Claude Haiku 5.5 ~$0.04; HF/DeepInfra Qwen3.8-27B ~$0.07. Annual at moderate frequency (300 events): $12–234 depending on model choice.
- **TPM gotcha:** Bedrock reserves input + max_tokens against TPM per request; unset max_tokens defaults to model max, so one 37k prefill can reserve ~100k+ quota units. Verify the `bedrock-invoke` TPM cap ≥ ~150k or a single overflow prefill will 429. Prompt-cache reads don't count against TPM.
- **Model-fit gotcha:** Bedrock Qwen3 32B has a 32K context window — unusable for 37k overflow prompts. Like-for-like targets: Qwen3 Coder 480B (256K, $0.45/$1.80), Nova Pro (300K), Llama 4 Maverick (1M), Claude Sonnet/Haiku 5.5.
- The ~$10 budget SCP was tuned for the earlier model gate — confirm it covers new model IDs before relying on it for overflow.

### E — Mac pricing/TCO/longevity (complete)

**Price verification:** M5 Ultra 96 GB/1 TB base = **$5,499** (shipped Sept 22, 2026) — the ~$5,500 ceiling is exact. **M5 Max floor correction: 64 GB/1 TB = ~$3,799, not ~$3,300** (36 GB base is $2,499 but too small). 256 GB tier +$4,000; 512 GB +$15,500 (out of scope, as locked). Base 1 TB storage suffices for a 100–200 GB model library; skip Apple SSD upgrades (external TB5 ~$100/TB).

**3-yr TCO (Ultra):** $5,499 + AppleCare+ $185 + electricity ~$420 (9 W idle / 385 W max, ~$11.50/mo at 8 h/day duty) − resale at 40–50% (−$2,200–2,500) = **net ~$3,600–3,900 → ~$100–108/mo**. The Max floor nets **~$65–75/mo**. Mac's efficiency displaces ~$700 of electricity vs the 7900 XTX-class tower over 3 years.

**Resale:** model **40–50% at 36 mo** — 2026 DRAM-shortage premium for high-RAM Macs is temporary (Macfax expects structural 15–18%/yr decay to reassert by 2027); M2 Ultra retained 58–70% at 35 mo, M1 Ultra 41–53% at 50 mo. Sell peer-to-peer — Apple Trade In pays 35–55% of market on Studios.

**Longevity:** ~1,200 GB/s bandwidth stays competent through the 3-yr window (Ars measured ~50 tok/s on 27B-class on Ultra vs ~31 on Max — corroborates §2 extrapolations). Real risk is **capacity**, not bandwidth: 96 GB fits 27B + 70B-class models; 64 GB is tight if 100B+ quantized MoEs become the default coding model by year 3.

**Vs. cloud line ($153/mo):** Ultra ≈ 60–70% of cloud cost and ends as a ~$2,400 asset; Max ≈ half of cloud cost. **On pure TCO, local wins both branches** — cloud's remaining argument is elastic scaling and zero hardware risk, not price.

### A — Model/arch trends, 3-yr horizon (complete)

**Verdict: mid-case, the bottleneck does *not* fully migrate to compute by 2029 (65–70% confidence) — but the moat's composition shifts from bandwidth toward capacity. Underwrite the capacity, not the bandwidth.**

- **MoE (moderate threat to bandwidth moat, tailwind to capacity):** the 27B-quality class is now ~30B-total/3B-active (GLM-4.7-Flash, Nemotron 3.5 Lightning, Qwen3.6 35B-A3B, gpt-oss-120b 117B/5.1B). Only ~3B active params (~1.5–2 GB at 4-bit) are read per token — a 273 GB/s DGX Spark decodes gpt-oss-120b at 41 tok/s vs the 1.2 TB/s Mac's 34. Bandwidth stops differentiating; the full expert set must still sit in RAM, so unified capacity is what makes 100B+ MoE feasible desk-side.
- **Extreme quant (low):** post-training 2-bit still collapses (steep, non-linear quality loss); native ternary works but tops out at 2B params. 4-bit remains the practical floor.
- **NCM/parallel decoding (moderate — the real compute-shift vector):** verified real (10–31× vs diffusion baselines; Mercury 2.5 in production at 1,100+ tok/s; Google's DiffusionGemma shipped June 2026), but production diffusion LLMs are Haiku/Flash-class quality and API-locked; NCM itself is a 725M research result. A 27B-class open-weight diffusion coding model by ~2028 is what would break the moat.
- **KV compression (low/neutral):** MLA/GQA shrink KV everywhere equally — helps both branches, doesn't decide.
- **Context growth (capacity tailwind):** agent sessions stretch to 500k+ but *active* context is invariant ~8K and compaction + prompt caching cap effective growth. Local serving makes caching free.
- **The Mac's known weak flank:** compute. gpt-oss-120b decode on Mac Studio falls to ~6 tok/s at long context where prefill/attention dominate.
- **Mind-changers (any two → re-rate to 2-year asset):** open-weight NCM/diffusion coding model matching dense-27B by 2027–28; native ternary scaling past ~30B at FP16 parity; MoE active fraction <2B with no quality loss; agent-harness context caps standardizing below ~50K.

### D-cloud — Cloud-only steady-state + constraints (complete)

**Verdict (a) constraints:** no structural disqualifier. Bedrock's no-training/no-sharing posture is genuinely strong for Sonnet-class and below (avoid "Fable-class" frontier models — they carry the `aws_review` 30-day AWS-side retention mode). HF Inference Providers route to third parties (DeepInfra: no training but may log small samples; Together: opt-in training) — weaker than Bedrock, no contractual ZDR. **The real blocker is self-inflicted: our TPM cap + $10 budget + spend-guard SCP stall a 3×37k workload on day one** — a 30-minute self-change (TPM ≥ 300k sustained, budget ~$50–200/mo, model-access grants per model ID; Anthropic requires use-case approval, new quotas often Applied=0).

**Verdict (b) cost vs. $153/mo** (10-turn session ≈ 370k in + 10k out; light 120/mo, moderate 300/mo, heavy 600/mo, 2 users):

| Route | Light | Moderate | Heavy |
|:---|:---:|:---:|:---:|
| HF→DeepInfra GLM-5.3-Flash / DeepSeek V4.1 Flash | $7–15 | $18–37 | $37–74 |
| HF→DeepInfra GLM-5.2 | $27 | $68 | $136 |
| Bedrock Nova Pro / Nova 2 Lite | $18–39 | $44–98 | $89–196 |
| Bedrock Claude Sonnet 5.5 (uncached / cached) | $110 / $32 | $276 / $81 | $552 / $162 |

- **Open-weight cloud route beats the Mac at every tier ($10–140/mo)** — caveat: a quality step down from Sonnet-class for agentic coding.
- **Claude-class heavy use blows past $153/mo in every configuration**; light-to-moderate cached stays under.
- Branch conclusion so far: cloud-only wins on price *if* the workload is light-to-moderate or accepts open mid-tier models; at heavy Claude-tier use the amortized Mac is cheaper, unthrottled, and more private.

### B — Real Apple Silicon benchmarks (complete)

**Verdict: §2/§5 decode extrapolations were pessimistic single-stream, roughly right 2-way, ~20–30% optimistic 3-way on Ultra — and wildly optimistic (5–6×) on prefill.** Real efficiency fraction is ~66–84% of the bandwidth ceiling (center ~70%), not the ~50% implied. No M4 Ultra exists (Apple went M3 Ultra → M5 Ultra), so M3 Ultra (819 GB/s) is the Ultra-class calibration.

Measured anchors (27B-class 4-bit, ~16 GB): M5 Ultra MLX single **54.7** @512 ctx (73% eff.), **42.6 @32k prompt** (NetworkChuck, direct, prefill 1,526 t/s); M5 Ultra llama.cpp `-np 8`: **10.9 each** (Metal dense batching is bad); TensorFold 4-way: 28.6 each; M5 Ultra 96 GB anecdotal: 2-way 93 each / 3-way 72 each (draft-model-inflated); M5 Max oMLX single **32.1** (84% eff.); M3 Ultra llama.cpp 4-way batched: 9.0 each. Prefill, dense 27B: Ultra ~1,300–1,500 t/s @15–60k; Max ~950 t/s @4k.

**Corrected numbers for our workload** (batching stack: oMLX / Splash / vLLM-metal / TensorFold — **avoid llama.cpp for multi-stream**):

| Scenario | Handoff est. | Corrected |
|:---|:---:|:---:|
| Ultra single @37k | ~32 | **~40–46** |
| Max single @37k | ~16 | **~26–32** (~22–24 llama.cpp) |
| Ultra 2-way @37k | ~32 each | ~28–32 each (fair) |
| Ultra 3-way @37k | ~32 each | **~22–28 each** (agg ~70–80); possibly 28–35 if Qwen3.8's hybrid attention (16/64 layers keep KV) makes the 5.5 GB/stream KV assumption ~4× too big |
| Max 3-way @37k | ~16 each | ~13–16 each (agg ~40–48) (fair) |
| **Cold 37k prefill** | Ultra ~4 s / Max ~9 s | **Ultra ~25–30 s / Max ~45–55 s** |

**The prefill surprise is the felt cost:** the §5/§8 "instant" feel claims are superseded — first cold turn of a session has a ~25–30 s gate (Ultra), then prefix caching carries it (89% hits, TTFT ~180 ms observed on a 96 GB box). Caveat: no direct 3-concurrent dense-27B @37k measurement on Ultra exists — interpolated from the M3 Ultra batch shape + physics + the anecdotal 96 GB report.

## Decision Matrix (research complete 2026-11-19)

| Axis | **M5 Max 64 GB** (local) | **M5 Ultra 96 GB** (local) | **Cloud, open mid-tier** (GLM-5.x / DeepSeek via HF) | **Cloud, Claude-class** (Bedrock Sonnet 5.5) |
|:---|:---|:---|:---|:---|
| Upfront capex | $3,799 | $5,499 | $0 (+ governance unblock) | $0 (+ TPM/budget/model grants) |
| Effective 3-yr $/mo (net of resale) | ~$65–75 | ~$100–108 | $10–140, usage-based, no asset | $32 (light, cached) – $552 (heavy, uncached) |
| Throughput, 3×37k subagents | ~13–16 each (agg ~40–48) | ~22–28 each (agg ~70–80) | not the constraint — our TPM cap is | same |
| Cold 37k prefill | ~45–55 s | ~25–30 s | seconds (provider-side) | seconds |
| 3-yr longevity | 64 GB tight if 100B+ MoE coding models default by yr 3; 614 GB/s fine for MoE active reads | 96 GB fits 27B + 70B-class; capacity underwritten (A: "underwrite capacity, not bandwidth"); compute is the weak flank at long ctx | elastic — always current models | elastic |
| Privacy | source never leaves | source never leaves | source leaves to DeepInfra/Together — no training, but sampled logging, no contractual ZDR | strong no-training at Sonnet-class; avoid Fable-class (30-day AWS retention) |
| Key risk | capacity wall by yr 3; prefill latency | prefill latency; compute flank | quality step-down vs Sonnet; our own SCP/budget governance stalls day one | cost blowout at heavy use; TPM friction |

### Synthesis

1. **On price alone, open mid-tier cloud dominates**: $10–140/mo, no capex, never ages — and it's the like-for-like successor to the current `qwen3.6:27b` subagent stack (the primary agent already runs GLM-5.2 via HF in this very setup — daily experiential data exists).
2. **The Mac's case is not price.** It buys: source never leaving the machine, no throttle/outage dependence, flat marginal cost at heavy use, and a ~$2,400 residual asset at year 3.
3. **The Ultra is the only configuration that beats Claude-class cloud at heavy use** (~$100/mo net vs $162–552/mo) — i.e., the Mac is also insurance against quality-tier escalation.
4. **Max vs Ultra**: the premium nets to ~$30/mo after resale — Ultra buys 2× decode speed, the capacity the MoE trend rewards, and 8-bit headroom. The Max's remaining case is a hard budget cap at ~$3.8k.
5. **Engine choice is as load-bearing as tier** for the local branch: MLX-family batching server with prefix caching; llama.cpp multi-stream measured ~11 tok/s each.
6. **Local overflow to cloud is a non-factor** (D-local: $20–150/yr) — no hybrid machinery needed; a rare spill can ride the existing (unblocked) Bedrock path.

## Token Burn & Cost-per-Million-Tokens (household, 2026-11-19)

**Revised household burn** (re-sizes the D-cloud volume, which sized ~45–228M tok/mo). Per person: 100–200M now → 200–400M planned; husband assumed similar. **Household: 400–800M tok/mo** (200–400M now → 400–800M planned). Every figure is a **cost-per-million-tokens (CPT)** so it lines up directly with the per-M rates on HF model cards; the $/mo column = that CPT × household burn.

**CPT method.** Agent skew ~97% input / 3% output (§4 session math); ~85% of input tokens hit the prompt-prefix cache (prefix caching is load-bearing, §B). Effective CPT = weighted mix of uncached-input, cache-read, and output rates; no-cache CPT shown where it materially differs. Cache rates only where the provider publishes them. (Local rows are flat capex amortized over burn — not a per-token list price — §E.)

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

> **$/mo** shown at 600M/mo; scale linearly ×0.67 / ×1.33 for the 400/800M endpoints. List CPTs: DeepInfra/HF Inference list prices (Nov 2026), no HF markup. Sonnet/Nova CPTs re-derived from the D-cloud session math (10-turn ≈ 380k in/out; 2 users) at in $3.00 / out $15.00 / cache $0.30 per M. Local CPT = net 3-yr capex (Ultra ~$100–108/mo, Max ~$65–75/mo, §E) ÷ household burn.

### Calibration (2026-11-20) — ground truth from `opencode stats`

Factors above were assumptions; `opencode stats` (per the new `usage-stats` skill) now gives recorded usage to calibrate them. **Caveat: my usage is irregular and the history is short (75 active days lifetime, 17 in the last 30) — treat this as ballpark, not a clean signal.** Numbers below are deliberately not over-fitted.

**Method.** Pulled `--all` (lifetime), `--days 90`, `--days 30`, each `--cost --models --json`. Derived per the skill: `input fraction = input/(input+output)` (the calculator's `--input` denominator), `cached input % = cache.read/(cache.read+input)`, plus a `billable IF = input/(input+output+reasoning)` for the case where reasoning is billed at the output rate. Compared each against the calculator's old defaults (97% input / 85% cache); flagged >10pp drift as MATERIAL.

**Method & tooling (where the numbers come from — digested from `handoff-token-usage-analysis.md` 2026-11-20).** The ground-truth source is OpenCode V2's native `opencode stats` command — no API calls, no credentials, reads the local session DB. The command knowledge is packaged as a repo-local skill at `opencode/skills/usage-stats/SKILL.md` (progressive disclosure; documents flags `--days N` / `--year` / `--all` / `--models` / `--cost` / `--json`, the derived metrics above, the cache-read-cumulative caveat, the local-`cost: 0` tier question, and the calibration workflow). The skill is deliberately decoupled from any calculator path or factor value so it stays durable. The cost model itself is `scratch/token-burn-calculator.py` — a pure-Python synthetic CPT renderer whose defaults are now calibrated (`--input 0.90`, `--cache 0.85`) and whose CLOUD/LOCAL/REFERENCE blocks encode the list rates and TCO components from this handoff's §§D-cloud / E. The calculator's docstring cross-references this handoff; re-run it with `python3 scratch/token-burn-calculator.py [burn] --input F --cache F` to re-render after any rate or factor change. Note: `scratch/` (no dot) is permanent user scratch — the calculator is *not* agent-disposable; it is to be described for this handoff's use but **not** edited further and **not** kept as a maintained artifact after the research project closes.

**Factor results (calculator-shape input fraction + cache hit):**

| Window | IF (out-only) | IF (billable, reas@out) | cached input % | drift vs 97/85 |
|:---|:---:|:---:|:---:|:---|
| lifetime (75 active days) | 95.0% | 94.2% | 69.8% | IF −2pp ok · cache **−15.2pp MATERIAL** |
| 90-day (36 active days) | 88.8% | 87.2% | 84.8% | IF −8pp ok · cache −0.2pp ok |
| 30-day (17 active days) | 88.1% | 86.4% | 83.3% | IF −8.9pp ok · cache −1.7pp ok |
| HF-only lifetime (cloud-billed pop.) | 92.6% | 88.5% | 88.8% | IF −4.4pp ok · cache +3.8pp ok |
| HF-only 30-day | 92.3% | 84.4% | 88.4% | IF −4.7pp ok · cache +3.4pp ok |

**What changed in the calculator (`scratch/token-burn-calculator.py`):**

- **`--cache` 0.85 → unchanged (validated).** Recent (83–85%) and HF-specific (88%) cluster right at 85%. The lifetime 69.8% MATERIAL drift is the known historical-drag artifact (older sessions before prefix caching was load-bearing, already noted in the token-usage-analysis handoff); it is not the forward-looking factor. 85% is a defensible, slightly conservative midpoint.
- **`--input` 0.97 → 0.90 (lowered).** The 97% came from the §4 *context-composition* estimate (prompt + tools + history dominates), but the calculator needs the *billed* token mix, and recorded input share is 88–95% — 97% overstates input share and therefore **understates cost** (input is cheaper than output on every calculator model). 0.90 is a ballpark midpoint across windows; the billable figure drops to ~0.84–0.86 if reasoning is billed at the output rate (see open question 1).

**Effect of the factor change alone (rates held at DeepInfra list, 600M/mo):** GLM-5.2 effective CPT $0.22 → **$0.33** (+50%), $/mo $132 → **$199**; Qwen3-Coder-480B $0.16 → $0.22, $95 → $130; flash class ~$20 → ~$22. Mac rows unchanged (TCO-based). This **narrows but does not eliminate** the open-weight cloud price advantage; the Mac's net CPT (~$0.17/M) now sits *below* GLM-5.2-cloud ($0.33/M) but still well above flash class (~$0.04/M).

### ⚠ Rate discrepancy found (unresolved — read before trusting absolute $/mo)

Reverse-engineering recorded cost against tokens exposes a **much larger** discrepancy than the factor drift:

| Model (HF, providerID `huggingface`) | Recorded cost | Implied eff $/M | Calculator's DeepInfra-list rate |
|:---|:---:|:---:|:---:|
| GLM-5.2 (lifetime) | $10.61 | **~$1.91/M** | in $0.56 / out $1.80 / cache $0.10 |
| GLM-5.2 (30-day) | $7.34 | ~$2.01/M | " |
| GLM-5 (lifetime) | $20.55 | ~$3.24/M | (not in calc) |

Even billing reasoning at the output rate with **no** cache discount, the calculator's rates produce $4.23 lifetime vs $10.61 recorded for GLM-5.2 — **the calculator understates GLM-5.2 cost ~2.5×**, and the implied input rate to reconcile is **~$1.9–2.1/M, ~3.5× the $0.56/M list**. If the real effective rate is ~$2/M, then GLM-5.2 cloud at 600M/mo is **~$1,200/mo, not $132–199/mo** — which would flip the cloud-vs-Mac conclusion at the mid-tier (Mac ~$100/mo wins decisively).

**Why I did NOT silently "fix" the calculator's rates:** the discrepancy is almost certainly a *route* difference, not a wrong list price. The calculator models **HF → DeepInfra** at DeepInfra's list; the recorded spend is on providerID `huggingface` (HF's own Inference), which may carry an HF markup or route to a different backend. **The two are not the same thing.** Whether the calculator's DeepInfra-list numbers are valid for the workstation decision depends on a fact only the user can confirm (see open question 2). Until resolved, **trust only the relative CPT ranking among same-route models, not the absolute $/mo.**

### Open questions added by calibration (do not silently decide)

1. **Is reasoning billed at the output rate on the DeepInfra route?** The calculator's `--input` denominator is `input/(input+output)`. GLM-5.2 emits substantial reasoning (30-day: 391k reasoning vs 306k output — reasoning *exceeds* output). If reasoning is billed at the output rate, the billable input fraction is ~0.84, not 0.90, and cost is higher again. Skill caveat flags this as unconfirmed. → If yes, set `--input 0.85` and re-render.
2. **Which route is the recorded `huggingface` spend actually on — HF-hosted (markup) or DeepInfra via HF Inference Providers?** This single fact determines whether cloud GLM-5.2 is ~$132–199/mo (DeepInfra list) or ~$1,200/mo (recorded effective), and thus whether cloud beats the Mac at the mid-tier. **Decision-relevant; resolve before the branch decision.** Check: HF billing/settings page, or a one-shot `opencode stats` cross-check after explicitly selecting a DeepInfra provider variant.
3. **(carried) cache-write semantics** — only `qwen3.6-plus-free` (9 steps) ever shows nonzero `cache.write`; all other models 0. Real warming or counting artifact? Does not affect current calibration (cache.write≈0 everywhere that matters).

**Burn-rate cross-check (recorded, my cloud spend only — not household, not local):** 30-day $8.21 (~$8/mo annualized run-rate, 17 active days), 90-day $22.51 (~$7.5/mo, 36 active days). These are *my single-user, irregular* cloud spends; the household 600M/mo figure in the CPT table is a forward planning number, not an extrapolation of this history — do not treat the two as comparable.

**What this changes vs. the decision matrix:**

- **Claude-class is now the clear price outlier at this burn.** Sonnet runs ~$0.7–2.4/M → ~$430 (cached) to ~$1,450 (no-cache) per month; ×36 = ~$15k–$52k over 3 yr — past the ~$5,500 Ultra capex ceiling even at the *cached* end. A *cloud-only Sonnet tier* is out on price at 400–800M regardless of the quality hinge.
- **Open-weight HF scales with burn but stays cheapest on CPT.** Flash class ~$0.03–0.05/M (~$20–30/mo); GLM-5.2 ~$0.22–0.60/M (~$132/mo cached, up to ~$360/mo no-cache). The earlier "$10–140/mo" was sized at 45–228M; at 600M it is ~2–3× higher in absolute dollars, **same relative ranking**.
- **The Mac's effective CPT (~$0.11–0.17/M) sits mid-band in the open-weight range** — more expensive per token than flash class (3–5×) but competitive with Qwen-Coder/GLM-5.2 and far cheaper than Sonnet-class. So local's price case remains "flat, unthrottled, private, +~$2,400 residual," not "cheapest per token"; the price advantage over cloud shows up only vs. mid-tier+ open models or Sonnet-class.
- **Burn is a peak-concurrency constraint for local, not a daily-volume constraint.** 400–800M/mo is high only because context is re-sent each turn; as active compute it's a few hours of subagent bursts per user per day, well within the Ultra's ~70–80 tok/s 3-way aggregate (§B). The CPT numbers are valid because the machine can actually burn this volume without saturation.
- **Governance unblock is more load-bearing.** A $10 budget SCP and a low TPM cap would stall this burn on day one; budget ~$50–200/mo + TPM ≥ 300k (higher for the Sonnet tier) is now a hard prerequisite for any cloud branch.

## Suggested skills

- **grill-me** — branches grilled 2026-11-19; reuse if new branches open during research.
- **sec-review** — run at digestion: if the decision produces a procurement plan or infrastructure config (e.g., AWS Bedrock setup, cloud cost guardrails), the remaining artifacts warrant review. The existing AWS permission infrastructure (`handoff-invoke-path.md`, `handoff-model-gate-guardrails.md`) is relevant context for the cloud branch.

## Related handoffs & docs

- [`handoff-invoke-path.md`](./handoff-invoke-path.md) — TPM cap, bedrock-invoke permission set (cloud branch context)
- [`handoff-model-gate-guardrails.md`](./handoff-model-gate-guardrails.md) — GLM-5 access gate, spend-guard SCP (cloud cost controls)
- [`handoff-hf-cache-cleanup.md`](./handoff-hf-cache-cleanup.md) — model cache state, current Ollama setup
- [`docs/vllm.md`](../docs/vllm.md) — real 7900 XTX benchmarks (ROCm/vLLM)
- [`docs/ollama.md`](../docs/ollama.md) — Ollama setup (current runner)
- [`docs/openwebui.md`](../docs/openwebui.md) — Open WebUI

## Security Review (sec-review · 2026-11-20)
Result: PASS — all 4 areas complete, no H-class findings (2026-11-20). Advisory: none. The remaining artifacts (the `usage-stats` skill, `scratch/token-burn-calculator.py`, this handoff) carry no credential material, no network surface, no unsafe code patterns, and no trust-surface changes.
- SE: complete — no findings
- NE: complete — no findings
- CP: complete — no findings
- SO: complete — no findings

Digestion exit gate over the remaining artifacts after digesting `handoff-token-usage-analysis.md` into this handoff: the `usage-stats` skill (`opencode/skills/usage-stats/SKILL.md`), `scratch/token-burn-calculator.py`, and this handoff itself.
