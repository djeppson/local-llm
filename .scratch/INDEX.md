# Handoff Index

- **active** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: lock the agent's AWS surface down to a scoped allowlisted `ai`-only permission set; steps 1–5 done + verified live 2026-11-27 (policy provisioned, `ReadOnlyAccess` fallback attached, negative test passed, MCP pinned to `ai-agent`); next: tighten (`IamScopedVerification` ARN fix → drop fallback), then local hygiene + AGENTS.md update. **Triaged 2026-11-21: Keep** (head of AWS chain).

- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection. **Triaged 2026-11-21: Keep** (middle of AWS chain; [M] to verify prereqs + GATE step).

- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test. **Triaged 2026-11-21: Keep** (tail of AWS chain; [S] for first step).
