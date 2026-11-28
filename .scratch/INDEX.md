# Handoff Index

- **pending-digestion** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: scope the agent's AWS surface. **Build complete 2026-11-28:** Posture baseline = AWS MCP **abandoned**; `ai-agent` on **long-lived, tightly-constrained static creds** + `agent-ai` policy + `ReadOnlyAccess`; highly-privileged creds **behind SSO (~1h blast radius)**; flimsy SSO-convention scoping dropped; test-matrix / tighten steps **superseded**; local hygiene **SKIPPED** (user; deferred); **AGENTS.md update landed** (user-approved). Remaining: user commit + requested digestion (sec-review exit gate default, waivable). **Triaged 2026-11-21: Keep** (head of AWS chain).

- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection. **Triaged 2026-11-21: Keep** (middle of AWS chain; [M] to verify prereqs + GATE step).

- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test. **Triaged 2026-11-21: Keep** (tail of AWS chain; [S] for first step).
