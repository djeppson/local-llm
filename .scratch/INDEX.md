# Handoff Index

- **active** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: lock the agent's AWS surface down to a scoped allowlisted `ai`-only permission set; Q2 (A vs B identity) is the next grill. **Triaged 2026-11-21: Keep** (head of AWS chain; [S] to grill Q2).

- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection. **Triaged 2026-11-21: Keep** (middle of AWS chain; [M] to verify prereqs + GATE step).

- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test. **Triaged 2026-11-21: Keep** (tail of AWS chain; [S] for first step).

- **active** — [handoff-searxng-openwebui.md](handoff-searxng-openwebui.md) — **Spun off of Ollama consolidation (2026-11-26):** Open WebUI web search / RAG "not working as expected" (not yet diagnosed) + disposition of the LAN-exposed `0.0.0.0:8411` (no auth; recommend loopback-only). Ruled out: JSON format disabled (it's on), limiter (off). Suspects: v0.9.4 pin / endpoint binding / unpinned `latest` image. First diagnostic: `curl 'http://localhost:8411/search?q=test&format=json'`. Not urgent.
