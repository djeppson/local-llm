# Handoff: Invoke Path (quotas, logging, identity, OpenCode)

**Date:** 2026-11-07 **Status:** IN PROGRESS — fast path (2026-11-28): inline POC policy **APPLIED** on `ai-agent` (user-confirmed); direct `zai.glm-5` `InvokeModel` **VERIFIED** (returned a valid completion, 12 tokens). Builds 1 (TPM cap) + 2 (invocation logging) SKIPPED by user decision. **Only remaining: OpenCode hookup → end-to-end smoke** (see the OpenAI-shape risk in "Verified"). **Prereq:** handoff-model-gate-guardrails applied — `zai.glm-5` active on `ai`/us-west-2 (satisfied 2026-11-28: GATE pre-passed)

**Context:** Last leg of the series: make day-to-day model use scoped, burned-capped, short-logged, and working from local OpenCode. Identity is a `bedrock-invoke` SSO permission set (1h sessions) — invoke-only, region-scoped, model-scoped; local tooling uses SSO short-lived credentials only, no static secrets.

## Triage (2026-11-21)

**Decision: Keep.** Tail of the AWS security chain — the "last mile" that actually wires GLM-5 into daily OpenCode use. All decisions locked, policy drafted, six-step build order PENDING.

**Next step + LOE:** Lower `zai.glm-5` TPM quota to 10,000 on `ai` via Service Quotas (step 1 of build order) — first unblocked action. **[S = \<1hr]** — single console/CLI quota change; the rest is build-out.

**Dependencies:** Depends on `model-gate-guardrails` (kept) being applied first — `zai.glm-5` must be active on `ai`/us-west-2. Upstream chain (`agent-security-posture` → `model-gate-guardrails`) both kept.

## Decided (current)

- Prompts land in a CloudWatch log group (not S3) with **3-day retention** and the AWS-managed key — short-fuse audit, no standing prompt archive.
- `zai.glm-5` TPM quota lowered to **10,000** — caps worst-case burn at ~$1.9/hr at GLM-5 output pricing.
- OpenCode uses the native `amazon-bedrock` provider, model `zai.glm-5`, region `us-west-2`. **POC identity (2026-11-28, user decision):** profile `ai-agent` (long-lived static credentials + inline invoke policy, `security/bedrock-invoke-poc.json`) — no `aws sso login` needed. The `bedrock-invoke` SSO permission-set path below is superseded for the POC; the user's end state is a standalone/reusable IAM policy in the shape of the policy below.
- **Region pinning is mandatory (2026-11-28):** the `ai-agent` profile is an **empty section** in `~/.aws/config` (no region, no endpoint — creds live only in `~/.aws/credentials`). Whatever calls it (OpenCode provider settings, boto3, CLI) must pin `us-west-2` explicitly; do not rely on a default region.

## `bedrock-invoke` permission set policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "InvokeGLM5InRegionOnly",
    "Effect": "Allow",
    "Action": [
      "bedrock-runtime:InvokeModel",
      "bedrock-runtime:InvokeModelWithResponseStream",
      "bedrock-runtime:Converse",
      "bedrock-runtime:ConverseStream",
      "bedrock-runtime:CountTokens"
    ],
    "Resource": [
      "arn:aws:bedrock:us-west-2::foundation-model/zai.glm-5"
    ]
  }]
}
```

Notes:

- `::` (empty account segment) in the foundation-model ARN is correct — that's how system models are addressed.
- Do **not** add `zai.glm-4-7-flash` (ARN line or model-access request) until the use case earns it.
- If prompt caching is adopted later: this policy needs the prompt-cache actions + resource ARNs — verify the exact actions at that time.
- **Correction (2026-11-28):** invoke actions are `bedrock-runtime:` (data plane), not `bedrock:` (management plane) — the original draft's `bedrock:InvokeModel` / `bedrock:InvokeModelWithResponseStream` do not exist as actions and would have granted nothing. Converse / ConverseStream / CountTokens are separate actions, now included so the policy works whichever API surface the client uses (InvokeModel, Converse, or Mantle).
- If GLM-5.3 (cross-region) is ever revisited: this policy needs the `inference-profile/us.zai.glm-5.3` + destination-region model ARNs, and the region-deny SCP needs a scoped carve-out — reopen the region decision before touching either.

## Verified (2026-11-28) — direct invoke works

- **Inline policy APPLIED + invoke VERIFIED.** `BedrockInvokePoc` (`security/bedrock-invoke-poc.json`) is on `ai-agent` (user-confirmed). A direct `zai.glm-5` `InvokeModel` call returned a valid completion: `finish_reason: stop`, content `"ok"`, usage 10 prompt + 2 completion = **12 tokens**. Auth + authorization through the inline policy is confirmed end-to-end at the API layer.
- **Repro (no local boto3; `uv` avoids polluting the machine):** `AWS_PROFILE=ai-agent uv run --with boto3 python /tmp/opencode/glm5_smoke.py` — boto3 client `bedrock-runtime`, region pinned `us-west-2` in the client (the profile has none).
- **GLM-5's `InvokeModel` speaks OpenAI chat-completions shape.** Tried in order: Anthropic `inputs` → `missing field 'messages'`; Converse `messages/content:[{text}]` + `inferenceConfig` → `Invalid 'content' variant`; OpenAI `messages:[{role, content:<string>}]` + `max_tokens` + `temperature` → **works**, returns OpenAI `chat.completion`. **Main remaining risk for step 5:** OpenCode's native `amazon-bedrock` provider may not be a drop-in for GLM-5 if it sends Anthropic/Converse shapes — the OpenAI-compatible (Mantle) endpoint may be the right provider. Verify at hookup.
- **Scope check invalidated (and that's fine).** `list-foundation-models` under `ai-agent` is **not** denied: a pre-existing attached policy (matches `security/agent-ai-policy.json`, `BedrockModelAccessGate` statement) already grants the management-plane actions `bedrock:ListFoundationModels` / `GetFoundationModelAvailability` / `Create+DeleteFoundationModelAgreement` (Resource `*`), plus `bedrock:Get+PutModelInvocationLoggingConfiguration` and guardrail CRUD. So (a) invoke-only scope is proven by the direct invoke working, not by a list-denial; (b) the EULA soft-gate action `DeleteFoundationModelAgreement` (guardrails build-1 caveat) is already available; (c) invocation-logging config (skipped step 2) is already permitted if re-enabled later.
- **CLI gotchas (v2.34.45):** `list-foundation-models` rejects `--max-results`; `invoke-model`'s binary response is awkward with `--outfile` (both parameter and global positions fail in this build). Use boto3 / `uv run --with boto3` for a binary invoke.

## Build order

1. SKIPPED (2026-11-28, user decision) — `ai`: Service Quotas — lower `zai.glm-5` TPM to 10,000. Rationale: bypass rigid spend control for the POC; user keeps a close eye on spend. (Spend-guard SCP from guardrails build 3 still blocks provisioned capacity + Marketplace.)
1. SKIPPED (2026-11-28, user decision) — `ai` console: Bedrock invocation logging → CloudWatch (AWS-managed key); capture the log group name, then `aws logs put-retention-policy` → **3 days** (CLI). Rationale: POC simplification; CloudTrail already records who/when/model. Steps stand as drafted if the POC graduates.
1. DONE (2026-11-28) — identity policy on `ai-agent`: `security/bedrock-invoke-poc.json` applied by the user as inline policy `BedrockInvokePoc` (the `bedrock-invoke` SSO permission-set path is superseded/unused). Direct `zai.glm-5` invoke verified through it (see "Verified" above). The policy stays the shape of the eventual standalone/reusable policy.
1. DONE (2026-11-28) — local profile: `ai-agent` already exists (static credentials, no SSO login). **Note:** it's an empty section (no region) — every caller must pin `us-west-2`. The drafted scope check (`list-foundation-models` "should be denied") is **invalidated**: a pre-existing attached policy already grants those management actions, so they're allowed; invoke-only scope is proven by the direct invoke instead.
1. PENDING — Local: OpenCode V2 config in a project-local `opencode.json` at the repo root (NOT the global `opencode/` live config): `providers.amazon-bedrock.settings = { "profile": "ai-agent", "region": "us-west-2" }` plus an explicit `zai.glm-5` model entry; user selects via `/models`, not set as default.
1. PARTIAL (2026-11-28) — smoke test: **direct `zai.glm-5` `InvokeModel` VERIFIED** (valid completion, 12 tokens — see "Verified" above, incl. the OpenAI-shape body + repro). **Remaining:** a real invocation from OpenCode succeeds end-to-end (depends on step 5; watch the OpenAI-shape risk).

## Future direction

- Flex tier (~50% off on-demand, higher latency) and prompt caching (long agent loops) as volume grows — both need permission-set additions when adopted.
- `zai.glm-4-7-flash` if a cheaper/lighter second model earns it: one console request + one ARN line.
- GLM-5.3 (cross-region) only if in-region proves a real limit — see policy note; the region decision gets reopened first.
