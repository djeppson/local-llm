# Handoff Index

- **active** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: lock the agent's AWS surface down to a scoped allowlisted `ai`-only permission set; steps 1–3 done (identity shape, allowlist, policy JSON at `security/agent-ai-policy.json`); next is human provisioning in Identity Center. **Triaged 2026-11-21: Keep** (head of AWS chain).

- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection. **Triaged 2026-11-21: Keep** (middle of AWS chain; [M] to verify prereqs + GATE step).

- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test. **Triaged 2026-11-21: Keep** (tail of AWS chain; [S] for first step).
