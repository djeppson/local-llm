# Handoff: Model Gate & Guardrails (GLM-5 access, SCP, budget)

**Date:** 2026-11-07 **Status:** PENDING **Prereq:** handoff-access-hygiene applied — both SSO profiles log in cleanly

**Context:** Same project: personal remote Ollama on `ai` (741297776185, Bedrock, us-west-2). This handoff lands model access (the fail-fast gate) plus the protective controls that don't depend on it working: detective coverage and spend guardrails.

## Triage (2026-11-21)

**Decision: Keep.** Middle of the AWS security chain — GLM-5 access gate + detective coverage (GuardDuty/org trail) + $10/mo spend ceiling. Plan fully drafted, all steps PENDING; prerequisite (`agent-security-posture`) kept.

**Next step + LOE:** Verify prerequisites (clean SSO both profiles, GuardDuty detector + org trail present, no existing spend SCP/budget), then perform the console-side GATE step to request `zai.glm-5` and accept the Z.AI EULA. **[M = a few hours]** — gate is a manual console action; surrounding verification spans both accounts and several services.

**Dependencies:** Depends on `agent-security-posture` (kept) being applied first. Feeds `invoke-path` (kept) — which needs `zai.glm-5` active on `ai`/us-west-2.

## Carried forward (current state — verify where noted)

- Model: **`zai.glm-5` only**, in-region us-west-2. `zai.glm-4-7-flash` deliberately held back. GLM-5.3 rejected (cross-region-only; region decision stands).
- Region: us-west-2 only, enforced by an org region-deny SCP (pre-existing).
- Org "AI services" data opt-out is in place — keep it; it has no functional impact on Bedrock.
- Detective baseline (set up 2026-11-06, re-verify): org trail `management-events` (from mgmt, multi-region) covers `ai`; standalone GuardDuty detector `c0d0da32c6f93dd46378cc87c925bdaa` on `ai`/us-west-2.
- Cost posture: $10/mo ceiling; fixed overhead ≈ $5/mo (GuardDuty).

## Verify first

- `ai`: `zai.glm-5` is **not** yet activated (console or `list-foundation-models`); if it is, skip to build 3
- GuardDuty detector and org trail from "Carried forward" still exist
- No spend-guard SCP or cost budget exists on 741297776185 yet

## Build order

1. PENDING — **GATE** — `ai` console: Bedrock → Model access → request `zai.glm-5`, accept the Z.AI EULA; then confirm with `aws bedrock list-foundation-models --profile ai --region us-west-2`. If the console rejects it: **stop and revisit the model choice** — nothing below depends on the model, so nothing to unwind.

1. PENDING — Enable IAM Access Analyzer on `ai` (free, no findings target of this handoff)

1. PENDING — Create the spend-guard SCP and attach to 741297776185 (under `djeppson`). Approved 2026-11-06; wide-scope Deny is deliberate — nothing legitimate on this account needs provisioned capacity or Marketplace, and narrow scoping only buys holes:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "DenyProvisionedCapacity",
         "Effect": "Deny",
         "Action": [
           "bedrock:PurchaseProvisionedModelCapacity",
           "bedrock:*ProvisionedModelThroughput*"
         ],
         "Resource": "*"
       },
       {
         "Sid": "DenyMarketplace",
         "Effect": "Deny",
         "Action": "aws-marketplace:*",
         "Resource": "*"
       }
     ]
   }
   ```

1. PENDING — `ai`: $10/mo cost budget with alerts at 50% / 80% / 100% + forecast alert → SNS topic (us-west-2) → `darren.jeppson@gmail.com`; enable Cost Anomaly Detection (free)
