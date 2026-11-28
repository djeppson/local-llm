# Handoff Index

- **active (ready for digestion)** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate (pre-passed); Access Analyzer ✅; spend-guard SCP ✅; $10 budget + anomaly detection **skipped by user 2026-11-28** (POC simplification). All builds resolved — digest when ready.

- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — **Fast path 2026-11-28:** TPM cap + invocation logging SKIPPED (user decision); inline POC policy on `ai-agent` **APPLIED** + direct `zai.glm-5` invoke **VERIFIED** (12 tokens); `bedrock-runtime:` action fix recorded; profile is region-empty (pin us-west-2). GLM-5 speaks **OpenAI chat-completions** shape — OpenCode native-bedrock may not be a drop-in (**main remaining risk**). Remaining: OpenCode hookup → e2e smoke.
