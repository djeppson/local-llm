# Handoff: Model Gate & Guardrails (GLM-5 access, SCP, budget)

**Date:** 2026-11-07 **Status:** COMPLETE — verified 2026-11-28: GATE pre-passed; builds 2 (Access Analyzer) + 3 (spend-guard SCP) done; build 4 (budget + SNS + anomaly detection) SKIPPED by user decision 2026-11-28 (POC simplification — user monitors spend directly) **Prereq:** handoff-access-hygiene applied — both SSO profiles log in cleanly

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
- Cost posture: $10/mo ceiling no longer enforced (build 4 skipped 2026-11-28, user decision); GuardDuty ≈ $5/mo fixed overhead remains. Spend-guard SCP (build 3) still blocks provisioned capacity + Marketplace.

## Verify first (results 2026-11-28, agent channel `ai-agent`)

- ✅ `zai.glm-5`: `get-foundation-model-availability` → `authorizationStatus: AUTHORIZED`, agreement/entitlement/region all AVAILABLE. `list-foundation-model-agreement-offers` → "Agreement not supported for this model" (no EULA offer flow for GLM-5). **Per handoff rule: GATE pre-passed → skip build 1.**
- ✅ GuardDuty detector `c0d0da…` ENABLED (created 2026-11-07), all data sources on
- ✅ Org trail `management-events`: `IsOrganizationTrail: true`, multi-region, visible from `ai`
- ✅ No cost budget on `ai`/us-west-2 (`describe-budgets` empty)
- ✅ No Access Analyzer on `ai`/us-west-2 (`list-analyzers` empty) — build 2 still needed
- ✅ Spend-guard SCP: **absent** (checked account + both ancestor OUs + root via `djeppson`, read-only). Inherited SCP chain: root `deny-leave-org`, `deny-unused-svcs-regions`, `maintain-cloudtrail`, `deny-member-iam-id-center-instances`; OU adds `deny-igw-peering-globalaccelerator`; all levels carry `FullAWSAccess`.
- 🆕 Finding (2026-11-28): root `deny-unused-svcs-regions` (p-7xvg2ef6) `DenyUnusedGlobal` already denies `aws-marketplace:*` (+ marketplace-management, portal, a4b, chime, directconnect, importexport) → the approved spend-guard `DenyMarketplace` statement is **redundant**. Its `DenyProvisionedCapacity` (bedrock) is covered by **no** existing SCP → build 3 still needed. The "Carried forward" region-deny is the same policy's `DenyUnusedRegions` statement (carve-outs: us-east-1, us-west-2).

## Build order

1. SKIPPED (2026-11-28) — **GATE** — pre-passed: `zai.glm-5` already `AUTHORIZED` (see Verify first). Original step was: `ai` console: Bedrock → Model access → request `zai.glm-5`, accept the Z.AI EULA; then confirm with `aws bedrock list-foundation-models --profile ai --region us-west-2`. If the console rejected it: **stop and revisit the model choice** — nothing below depends on the model, so nothing to unwind.

   - **Caveat (from agent-security-posture, 2026-11-27):** the gate-close action the `agent-ai` set will carry is `bedrock:DeleteFoundationModelAgreement`, and it is **soft** — re-invoking the model recreates the agreement. Durable model blocking needs an IAM/SCP Deny (human-applied under `djeppson`). **Resolution (2026-11-28):** GLM-5 reports "Agreement not supported for this model" — the soft-delete semantic doesn't apply to GLM-5 at all; the open question is moot for this track.

1. DONE (2026-11-28) — Enable IAM Access Analyzer on `ai` (free, no findings target of this handoff). Applied under human `ai` profile: `ai-account-analyzer`, `arn:aws:access-analyzer:us-west-2:741297776185:analyzer/ai-account-analyzer`, verified ACTIVE via `ai-agent`. (CLI flag is `--analyzer-name`, not `--name`.)

1. DONE (2026-11-28) — Create the spend-guard SCP and attach to 741297776185 (under `djeppson`). Applied: `spend-guard` **p-9xaszm54** (`arn:aws:organizations::422622447102:policy/o-tehe9bagfd/service_control_policy/p-9xaszm54`), both statements as approved, attached to 741297776185, verified via `list-policies-for-target`. Approved 2026-11-06; wide-scope Deny is deliberate — nothing legitimate on this account needs provisioned capacity or Marketplace, and narrow scoping only buys holes:

    - **Decision (2026-11-28):** Keep both statements as approved 2026-11-06 (user choice). `DenyMarketplace` does duplicate org-root `deny-unused-svcs-regions` (`DenyUnusedGlobal`); deliberate redundancy — the bedrock spend-guard stays self-contained even if that org-root policy is later narrowed.

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

1. SKIPPED (2026-11-28, user decision) — `ai`: $10/mo cost budget with alerts at 50% / 80% / 100% + forecast alert → SNS topic (us-west-2) → `darren.jeppson@gmail.com`; enable Cost Anomaly Detection (free). Rationale: bypass rigid budgeting for the POC — user keeps a close eye on spend. Steps stand as drafted if the POC graduates.
