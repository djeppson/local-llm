# Handoff Index

- **pending-digestion (blocked)** — [handoff-flexible-hierarchy.md](handoff-flexible-hierarchy.md) — **Triaged 2026-11-21: B-track (extraction-to-code) abandoned as low-value; A-pilot prose (committed AGENTS.md Lanes) persists regardless. Sec-review exit gate ESCALATED — 1 Critical SO finding on the committed exempt-lane prose (CWE-693 · AISVS C9.2): reads as re-framing the Conflict/Ambiguity Protocol to skip it. Removal blocked pending user decision on the Lanes framing.** A-pilot committed 2026-11-17. Moved from notes 2026-11-17.

- **active** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: lock the agent's AWS surface down to a scoped allowlisted `ai`-only permission set; Q2 (A vs B identity) is the next grill. **Triaged 2026-11-21: Keep** (head of AWS chain; [S] to grill Q2).

- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection. **Triaged 2026-11-21: Keep** (middle of AWS chain; [M] to verify prereqs + GATE step).

- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test. **Triaged 2026-11-21: Keep** (tail of AWS chain; [S] for first step).

- **active** — [handoff-searxng-openwebui.md](handoff-searxng-openwebui.md) — **Spun off of Ollama consolidation (2026-11-26):** Open WebUI web search / RAG "not working as expected" (not yet diagnosed) + disposition of the LAN-exposed `0.0.0.0:8411` (no auth; recommend loopback-only). Ruled out: JSON format disabled (it's on), limiter (off). Suspects: v0.9.4 pin / endpoint binding / unpinned `latest` image. First diagnostic: `curl 'http://localhost:8411/search?q=test&format=json'`. Not urgent.
