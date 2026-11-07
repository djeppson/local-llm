# Handoff: New AWS Account Hardening for Amazon Bedrock (Personal Use)

**Date:** 2026-11-04 **Status:** Decisions finalized (incl. 2026-11-06 grill corrections); implementation pending per build order **Context:** Brand-new account in an existing AWS Organization, to be used as a "personal remote Ollama" — running LLMs too large to host locally. Owner is privacy-first, security-conscious, and cost-lean. Note: original working repo was wrong; this doc preserves state.

______________________________________________________________________

## 1. Decided (decision record)

- **Workload & data:** Personal, non-regulated data; privacy-sensitive owner. No compliance obligations, but strict personal privacy bar.
- **Cost posture:** Lean — no CMKs ($1/mo each), no Secrets Manager, no Config, no Security Hub; prefer free native controls (SCPs, CloudTrail, budgets). ~$5/mo fixed-cost ceiling (GuardDuty).
- **Identity:** IAM Identity Center (SSO) from the org; passkey MFA already in use across all accounts; no IAM users, no long-lived access keys. Named SSO profiles per account.
- **Accounts:** Bedrock account = SSO profile `ai` (741297776185). Org admin = SSO profile `djeppson` (422622447102) — profile was accidentally removed and needs restoring (it's in `~/.aws/credentials` with static keys; that entry is a posture violation to revisit).
- **Region:** **us-west-2 (Oregon) only**; an SCP is already in place denying all other regions. Broadest US model catalog + data residency.
- **AI services opt-out:** Org policy opting out of all "AI Services" — **KEEP, do not lift.** Belt-and-suspenders: Bedrock never trains base models on customer data anyway; opt-out has no functional impact on Bedrock.
- **Invocation logging:** Bedrock model invocation logging → **CloudWatch log group only** (not S3), **3-day retention** on the log group, AWS-managed KMS key. Short-fuse audit trail of prompts without a persistent sensitive archive.
- **Detective controls:** Org CloudTrail trail (verified covering `ai` on 2026-11-06); **GuardDuty: standalone detector on `ai`** (created 2026-11-06, us-west-2 — the "org GuardDuty" premise did not exist; mgmt has a us-east-1 detector only); **IAM Access Analyzer: enable** (free); skip Config & Security Hub (cost).
- **Budget:** **$10/mo cost budget**, alerts at 50% / 80% / 100% + forecast alert → `darren.jeppson@gmail.com` via SNS (us-west-2); Cost Anomaly Detection on (free). Personal experiment anchor.
- **Structural spend guards:** SCP on this account (approved 2026-11-06) — two wide Deny statements: `bedrock:PurchaseProvisionedModelCapacity` + `bedrock:*ProvisionedModelThroughput*`, and `aws-marketplace:*`. Nothing legitimate on this account needs those actions; wide scope breaks nothing, narrow scope only buys holes.
- **Burn cap:** GLM-5 tokens-per-minute quota lowered to **10K TPM** (grilled 2026-11-06 — the earlier "~100K TPM ≈ $1.4/hr" claim was off by ~10×; 10K TPM caps worst-case burn at ~$1.9/hr at $3.20/M output, which matches the ~$1.4/hr intent).
- **Guardrails for Bedrock:** **Skip.** Billed per text-unit, adds latency; value targets third-party-facing apps. Revisit if a personal app is ever exposed to others.
- **Models enabled:** **Only `zai.glm-5`.** `zai.glm-4-7-flash` is a deliberate "add later" (one console request + one ARN line when/if it earns its keep). All other provider EULAs remain un-accepted. Opt-in model access = free blast-radius control.
- **Inference mode:** **In-region only.** Reject GLM-5.3 (cross-region-only, can't pin to us-west-2, would conflict with the region SCP). Never use `us.`/`global.`-prefixed inference-profile IDs. Data pinned to us-west-2; no SCP carve-outs.
- **OpenCode integration:** Native `amazon-bedrock` provider (`@ai-sdk/amazon-bedrock`), model ID `zai.glm-5`, `AWS_REGION=us-west-2`, `AWS_PROFILE=bedrock-invoke`; `aws sso login` before sessions. No static secrets; SSO short-lived credentials only.

## 2. Verified facts (do not re-research)

- **GLM model availability in us-west-2 (checked against AWS model cards, 2026-11-04):**
  - `zai.glm-4-7-flash` — In-Region ✅ — ~$0.07 / $0.41 per M tokens
  - `zai.glm-4.7` — In-Region ✅ — ~$0.60 / $2.20
  - `zai.glm-5` — In-Region ✅ — ~$1.00 / $3.20
  - `zai.glm-5.3` — ❌ cross-region inference ONLY (`us.zai.glm-5.3` / `global.zai.glm-5.3`); no in-region option. ~$1.85 / $5.81 (US profile). One source described it as for "eligible enterprise customers" — activation on a personal account unconfirmed. **Rejected for now.**
- **OpenCode provider:** `amazon-bedrock` exists in models.dev; npm `@ai-sdk/amazon-bedrock`; resolves AWS credential chain (keys / `AWS_BEARER_TOKEN_BEDROCK` / standard chain incl. SSO profiles). 203 models listed.
- **Pricing levers:** GLM models support Bedrock **Flex tier** (~50% off on-demand, higher latency — good for personal use) and **prompt caching** (good for long agent loops). Batch pricing also ~50% off but requires data at rest — not adopted.

## 3. Open items / to verify

1. **Org CloudTrail & GuardDuty** — RESOLVED 2026-11-06: org trail `management-events` (mgmt 422622447102, multi-region, KMS, home us-east-1) appears in `ai` as an org trail — covered, no duplicate trail. GuardDuty: no org detection existed; standalone detector `c0d0da32c6f93dd46378cc87c925bdaa` created on ai/us-west-2.
1. **Root user hygiene** (console, slot 2): root MFA (hardware/passkey), no root access keys, alternate contacts set.
1. **GLM-5 activation** promoted out of open items into the build order as a **gate at slot 3** (fail fast before any model-specific work).

## 4. Build order (pending)

1. Restore SSO profile `djeppson` (org admin, 422622447102) in `~/.aws/config`; `aws sso login` for `djeppson` + `ai` (user passkey)
1. DONE (2026-11-06, mostly): `djeppson` org trail verified covering `ai`; GuardDuty detector created on ai. REMAINING: root MFA / no root keys / alternate contacts — console check under `ai`
1. **GATE — `ai` console:** Bedrock → Model access → request `zai.glm-5` → accept Z.AI EULA → confirm active. Then verify with `aws bedrock list-foundation-models --profile ai --region us-west-2`. If the console rejects it: **stop and revisit model choice** — nothing model-specific is done yet, so nothing to unwind
1. Enable IAM Access Analyzer on `ai` (CLI, free)
1. Create SCP policy (approved JSON below) on the org; attach to 741297776185 (CLI under `djeppson`)
1. Create $10/mo budget on `ai` (alerts 50/80/100% + forecast → SNS → darren.jeppson@gmail.com); enable Cost Anomaly Detection
1. Bedrock invocation logging → CloudWatch (console under `ai`); capture the log group name, then `aws logs put-retention-policy` → **3 days** (CLI)
1. Service Quotas: drop GLM-5 TPM to **10,000** (CLI `service-quotas` under `ai`)
1. SSO: create `bedrock-invoke` permission set (1h session) with the §5 policy; assign to jeppson on `ai` (CLI under `djeppson`)
1. Local (agent): add `bedrock-invoke` profile to `~/.aws/config`; configure OpenCode `amazon-bedrock` provider → model `zai.glm-5`; smoke-test a real invocation; confirm the invoke-only scope rejects admin actions
1. **Later (not this session):** Flex tier + prompt caching as volume grows — note: prompt caching will require extra permission-set actions/resources when adopted

## 5. Reference: `bedrock-invoke` permission set policy

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

- `zai.glm-4-7-flash` deliberately excluded (2026-11-06): add its ARN + the model-access request only if the utility use case shows up.
- Foundation-model ARNs have an empty account segment (`::`) — that is correct for system models.
- If prompt caching is adopted later (build order 11), this policy needs prompt-cache actions + resource ARNs added — verify exact actions at that time.
- Converse API actions are covered by the InvokeModel permissions.
- If GLM-5.3 is ever revisited (cross-region), this policy would need the `inference-profile/us.zai.glm-5.3` ARN plus destination-region model ARNs, AND the region-deny SCP would need a scoped carve-out — re-open the decision then.

## 6. Posture summary

- Data: pinned to us-west-2, never used for training, opt-out policy on, prompts logged only for 3 days
- Access: SSO + passkey MFA only; daily driver is invoke-only scoped role; root dormant
- Spend: $10 budget + anomaly detection + no-provisioned-throughput SCP + TPM quota → hard ceiling near $10/mo; fixed overhead ≈ $5 (GuardDuty)
