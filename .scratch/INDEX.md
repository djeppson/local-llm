# Handoff Index

- **active** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: lock the agent's AWS surface down to a scoped allowlisted `ai`-only permission set; Q2 (A vs B identity) is the next grill.
- **active** — [handoff-access-hygiene.md](handoff-access-hygiene.md) — restore `djeppson` SSO profile + logins; root hygiene on `ai`.
- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection.
- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test.
- **active** — [handoff-llama-cpp-rocm.md](handoff-llama-cpp-rocm.md) — llama.cpp ROCm integration; plan + unit exist, unit disabled/inactive; next: bring plan up to spec (grill) then execute.
- **active** — [handoff-hf-token-hygiene.md](handoff-hf-token-hygiene.md) — inline HF token in vllm.md; rotated + scrubbed on move; verify Open WebUI key + no other locations before digest.
- **active** — [handoff-hf-cache-cleanup.md](handoff-hf-cache-cleanup.md) — 143 GB HF cache, 21 model dirs, several Qwen3.6-27B near-dups; audit against loaded/queued models, trim, re-baseline.
