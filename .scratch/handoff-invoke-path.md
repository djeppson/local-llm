# Handoff: Invoke Path (quotas, logging, identity, OpenCode)

**Date:** 2026-11-07 **Status:** PENDING **Prereq:** handoff-model-gate-guardrails applied — `zai.glm-5` active on `ai`/us-west-2

**Context:** Last leg of the series: make day-to-day model use scoped, burned-capped, short-logged, and working from local OpenCode. Identity is a `bedrock-invoke` SSO permission set (1h sessions) — invoke-only, region-scoped, model-scoped; local tooling uses SSO short-lived credentials only, no static secrets.

## Triage (2026-11-21)

**Decision: Keep.** Tail of the AWS security chain — the "last mile" that actually wires GLM-5 into daily OpenCode use. All decisions locked, policy drafted, six-step build order PENDING.

**Next step + LOE:** Lower `zai.glm-5` TPM quota to 10,000 on `ai` via Service Quotas (step 1 of build order) — first unblocked action. **[S = \<1hr]** — single console/CLI quota change; the rest is build-out.

**Dependencies:** Depends on `model-gate-guardrails` (kept) being applied first — `zai.glm-5` must be active on `ai`/us-west-2. Upstream chain (`agent-security-posture` → `model-gate-guardrails`) both kept.

## Decided (current)

- Prompts land in a CloudWatch log group (not S3) with **3-day retention** and the AWS-managed key — short-fuse audit, no standing prompt archive.
- `zai.glm-5` TPM quota lowered to **10,000** — caps worst-case burn at ~$1.9/hr at GLM-5 output pricing.
- OpenCode uses the native `amazon-bedrock` provider, model `zai.glm-5`, `AWS_REGION=us-west-2`, profile `bedrock-invoke`; `aws sso login` before sessions.

## `bedrock-invoke` permission set policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "InvokeGLMInRegionOnly",
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
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
- Converse-style calls are covered by the `InvokeModel*` actions above.
- If GLM-5.3 (cross-region) is ever revisited: this policy needs the `inference-profile/us.zai.glm-5.3` + destination-region model ARNs, and the region-deny SCP needs a scoped carve-out — reopen the region decision before touching either.

## Build order

1. PENDING — `ai`: Service Quotas — lower `zai.glm-5` TPM to 10,000
1. PENDING — `ai` console: Bedrock invocation logging → CloudWatch (AWS-managed key); capture the log group name, then `aws logs put-retention-policy` → **3 days** (CLI)
1. PENDING — `djeppson` console: create permission set `bedrock-invoke` (1h session) with the policy above; assign to `jeppson` on `ai`
1. PENDING — Local: add a `bedrock-invoke` SSO profile to `~/.aws/config` (reuse the SSO endpoints from the existing `ai` profile); sanity-check the scope rejects admin actions (e.g. `list-foundation-models` under it should be denied)
1. PENDING — Local: configure OpenCode `amazon-bedrock` provider → model `zai.glm-5` (`AWS_REGION=us-west-2`, `AWS_PROFILE=bedrock-invoke`)
1. PENDING — Smoke test: `aws sso login`, then a real invocation from OpenCode succeeds end-to-end

## Future direction

- Flex tier (~50% off on-demand, higher latency) and prompt caching (long agent loops) as volume grows — both need permission-set additions when adopted.
- `zai.glm-4-7-flash` if a cheaper/lighter second model earns it: one console request + one ARN line.
- GLM-5.3 (cross-region) only if in-region proves a real limit — see policy note; the region decision gets reopened first.
