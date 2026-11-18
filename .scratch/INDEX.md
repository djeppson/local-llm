# Handoff Index

- **active** — [handoff-aws-sso-refresh.md](handoff-aws-sso-refresh.md) — scripted ssh-tunnel SSO refresh (local-presence gate); script drafted, first run pending; **paused 2026-11-16** — trust-seam question (does presence gate *use*, not just *mint*?). Moved from notes 2026-11-17.
- **active** — [handoff-flexible-hierarchy.md](handoff-flexible-hierarchy.md) — flexible instruction hierarchy + extract core mechanical pieces into code/tools/skills; **A-pilot (lane fix) committed 2026-11-17**, B-pilot (candidate: quality-gate) + open decisions #2–#5 pending. Moved from notes 2026-11-17.
- **active** — [handoff-promote-skill.md](handoff-promote-skill.md) — `promote` OpenCode skill workstream: brief settled, skill authored + scrubbed of credential references; see handoff-promote-rerun for the pending sec-review rerun. Moved from notes 2026-11-17.
- **active** — [handoff-promote-rerun.md](handoff-promote-rerun.md) — promote-skill scrub complete, Security Review section pending rewrite to `IN PROGRESS (0/4)`; **sec-review rerun required** before digestion. Moved from notes 2026-11-17.
- **active** — [handoff-agent-security-posture.md](handoff-agent-security-posture.md) — independent track: lock the agent's AWS surface down to a scoped allowlisted `ai`-only permission set; Q2 (A vs B identity) is the next grill.
- **active** — [handoff-access-hygiene.md](handoff-access-hygiene.md) — restore `djeppson` SSO profile + logins; root hygiene on `ai`.
- **active** — [handoff-model-gate-guardrails.md](handoff-model-gate-guardrails.md) — GLM-5 access gate; Access Analyzer; spend-guard SCP; $10 budget + anomaly detection.
- **active** — [handoff-invoke-path.md](handoff-invoke-path.md) — TPM cap; invocation logging (3 days); `bedrock-invoke` permission set; OpenCode hookup + smoke test.
- **active** — [handoff-llama-cpp-rocm.md](handoff-llama-cpp-rocm.md) — llama.cpp ROCm integration; plan + unit exist, unit disabled/inactive; next: bring plan up to spec (grill) then execute.
- **active** — [handoff-hf-token-hygiene.md](handoff-hf-token-hygiene.md) — inline HF token in vllm.md; rotated + scrubbed on move; verify Open WebUI key + no other locations before digest.
- **active** — [handoff-hf-cache-cleanup.md](handoff-hf-cache-cleanup.md) — 143 GB HF cache, 21 model dirs, several Qwen3.6-27B near-dups; audit against loaded/queued models, trim, re-baseline.
- **active** — [handoff-kb-reorg.md](handoff-kb-reorg.md) — digest loose `docs/*` notes into KB (dj7900 host notes, new `security/` `network/` `development/` axes, rpi host); decisions locked, **c1+c2 committed; c3 (network) moved + README, gate pending user review/commit**; per-gate user commits.
