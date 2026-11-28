# Handoff: Agent Security Posture (lock down the agent's AWS surface)

**Date:** 2026-11-07 **Status:** IN PROGRESS — steps 1–5 done and verified live (2026-11-27); next: tighten the policy (fix `IamScopedVerification` ARNs → drop the `ReadOnlyAccess` fallback), then local hygiene + AGENTS.md update **Prereq:** none — independent track, runs alongside the bedrock hardening series

**Context:** Interim state: the agent currently operates overpermissioned — `AWSAdministratorAccess` on both `ai` and `djeppson` profiles. Goal: replace the agent's AWS surface with a scoped, allowlisted permission set on **`ai` only**, so agent actions are auditable, boundary-locked, and never self-modifying. This session landed Q1 (surface) and parked Q2 (identity shape) at "leaning A".

**Suggested skills:** docs-verify — for step 4+ provisioning checks; grilling is done for steps 1–3.

## Triage (2026-11-21)

**Decision: Keep.** Head of the AWS security chain — Q1 already landed in `AGENTS.md` as a preflight guard; one decision (Q2 identity shape) unblocks the seven-step build order. Abandoning would cascade to the downstream two.

**Next step + LOE:** Resume grill at Q2 (A vs B identity shape, settle permission-set name) → unblocks allowlist enumeration. **[S = \<1hr]** — single-decision grilling, no artifacts/infra yet.

**Dependencies:** `model-gate-guardrails` and `invoke-path` both depend on this being applied first (the "handoff-access-hygiene" prerequisite named in model-gate-guardrails is this track). Keep this and the chain stays alive.

## Decisions

- **Q2 — identity shape (AGREED 2026-11-27): A** — scoped set assigned to `jeppson`; no dedicated SSO user. Audit separation falls out of the machinery: agent actions land in the scoped role on `ai`, human-admin actions in the `AWSAdministratorAccess` role — CloudTrail separates by role, same person. B stays a future upgrade (policy is identity-agnostic; re-assignment is a 1h human step).
- **Permission-set name (AGREED 2026-11-27): `agent-ai`** — Identity Center set name; produces CloudTrail role `agent-ai-<id>`. Deliberately not `*-readonly`: the set includes scoped control writes (budgets, logging, quotas).
- **Policy JSON (AGREED 2026-11-27):** draft at [`security/agent-ai-policy.json`](../security/agent-ai-policy.json) — 12 pure-allow statements (default-deny; no Deny blocks), zero invoke actions, structurally cannot touch identity/SSO/org. Deltas settled at approval: `PutUseCaseForModelAccess` **out** (Anthropic-only one-time form, human-shaped); **no** `aws-marketplace:Subscribe` (Z.AI has no product key — docs; add scoped by `aws-marketplace:ProductId` if a product-key model becomes the gate); quota-tracking reads **in** (`GetRequestedServiceQuotaChange`, `ListRequestedServiceQuotaChangeHistory`); IAM reads include `arn:aws:iam::741297776185:policy/*` so `GetPolicy`/`GetPolicyVersion` can actually read the attached policies. **FINAL STATE 2026-11-27 (provisioned, verified):** live policy `arn:aws:iam::741297776185:policy/agent-ai` v1 is **identical to `security/agent-ai-policy.json` on disk** (9 statements). Deltas vs the earlier agreed list, per user at provisioning ("removed non-existent actions"): Service Quotas reads + `RequestServiceQuotaChange` and Budgets/`ce` statements are **absent** — note those actions do exist in AWS; re-add during tighten if the model-gate (spend guard) or invoke-path tracks need them. `ReadOnlyAccess` (v192) attached as an **interim fallback** alongside the custom policy — remove once the tightened set passes the test matrix.
- **Invoke placement (AGREED 2026-11-27):** Bedrock invoke/test actions stay on the separate `bedrock-invoke` set (invoke-path track owns it); `agent-ai` = investigation + guardrail-control only. Rationale: clean audit streams (inference vs control writes), independent kill-switches per risk class, consistency with the triaged chain.
- **Q1 — agent surface (AGREED 2026-11-07):** `ai` only. Scoped control plane: investigative reads + the specific control writes the hardening needs (budgets, invocation logging, quotas, model access, guardrail config). Zero mgmt permissions; zero on the other seven accounts. Identity Center / org / IAM-creating operations stay **human-applied** (under `djeppson`). **The agent never modifies its own boundaries** — no permission sets, SCPs, policies, or SSO.
  - Consequence: the "(under `djeppson`)" steps in the bedrock handoff series (SCP create/attach, permission-set create/assign) become human-applies / agent-verifies.
- **Model:** allowlist (scoped permission set, default-deny) rather than admin-plus-deny-lists — a deny list is only as good as what you thought to deny.
- **Process guard added to AGENTS.md today (2026-11-07):** Preflight section — mode-constraint conflicts get raised before acting, not half-executed around. (`../frob/AGENTS.md`, symlinked from this repo.)

## Open (next grilling branch)

- **Step 2 — allowlist enumeration. First sub-question: where do Bedrock invoke/test actions live — in `agent-ai`, or on the `bedrock-invoke` set (invoke-path track)?**
  - **DONE 2026-11-27:** invoke stays on `bedrock-invoke`; `agent-ai` = investigation + guardrail-control only.
  - **Read list (AGREED 2026-11-27):** STS `GetCallerIdentity`; CloudTrail (lookup events, describe trails, trail status); CloudWatch Logs (describe groups, get/filter events, retention); CloudWatch Metrics (list metrics, get stats); Bedrock reads (foundation models, model access, guardrails); Service Quotas (list/get); IAM reads **narrowed** to `agent-ai-*` + `AWSAdministratorAccess*` roles (list roles, get role/policy, attached policies); Budgets + `ce:GetCostAndUsage`; Access Analyzer findings (model-gate-dependent). Out: S3, EventBridge, Kinesis, SSO, org. Exact action names verified at JSON drafting (step 3).
  - **Control-write list (AGREED 2026-11-27):** budgets **create/update** (no delete); Bedrock **put+delete model access** (gate close = allowed direction), **put invocation-logging prefs**, **guardrail create/update** incl. versions (no delete); service-quotas **request quota change**; CloudWatch Logs **create log group, put retention**. Rule (record in policy rationale): **agent creates/updates/configures; teardown (budget/guardrail delete) is human** — `DeleteModelAccess` is the deliberate exception (gate-close, shrink-the-envelope direction).
  - **Never-list (CONFIRMED 2026-11-27, from Q1):** all IAM writes, SCPs, policies, SSO, org; by extension: S3/EventBridge writes, budget/guardrail deletes. Policy = pure allow (default-deny; no Deny blocks).
  - **Step 2 complete.** Step 3 complete (JSON drafted, approved 2026-11-27). Next: step 4 — human provisioning of the `agent-ai` set in Identity Center.

## Verified (local machine, 2026-11-07)

- `~/.aws/config`: nine account profiles, **all `AWSAdministratorAccess`**, one shared `db-work` SSO session; `fin`/`certbot` chain via `source_profile = djeppson`.
- `~/.aws/credentials`: three static key sets — one is `djeppson` (flagged posture violation in an earlier handoff); the other two have not been named yet.
- Permissions: `~/.aws/` is `755`, `config`/`credentials` are `644` (world-readable on a laptop).
- `opencode.json` already denies the agent `read` on `**/.aws/**` — but the **shell** tool reads the same files without check; the guardrail covers a tool, not the path.
- AWS MCP server (`mcp-proxy-for-aws-cli` → AWS-managed endpoint, per AGENTS.md) is configured for profiles `ai djeppson` — the agent's *remote* surface today is full admin on both accounts.
- The `djeppson` SSO profile appears **restored** in local config (previously the open item in handoff-access-hygiene) — its phases should be checked off next session.
- **2026-11-27 addendum (docs check):** SSO profile-flow role selection when a user holds multiple permission sets on `ai` (admin + `agent-ai` \[+ possibly `bedrock-invoke`\]) — **RESOLVED 2026-11-27 (docs):** AWS CLI docs (`cli-configure-sso-manual`) confirm `sso_role_name` in the profile section is the role-pinning key; a scoped profile = shared `sso_session` + `sso_account_id = 741297776185` + `sso_role_name = agent-ai-<id>` is deterministic. AssumeRole fallback (`source_profile` + `role_arn`) remains plan B (not needed). **EMPIRICALLY CONFIRMED 2026-11-27 (post-provision):** with both sets assigned to `jeppson`, `sso_role_name = agent-ai` deterministically assumes `AWSReservedSSO_agent-ai_d3ae8eca9c6db8bc` — the CLI resolves the permission-set name. Actual SSO role naming is `AWSReservedSSO_<set>_<hash>`, **not** `agent-ai-<id>` (see Findings).
- **2026-11-27 (pre-step-4, verified live under `djeppson`):** Identity Center instance `djeppson` ACTIVE, **primary region us-west-2**, `ssoins-79072264cfc8adcf`. Seven existing permission sets: AWSOrganizationsFullAccess, AWSAdministratorAccess, AWSReadOnlyAccess, AWSServiceCatalogEndUserAccess, `iam-auth-connect`, AWSServiceCatalogAdminFullAccess, AWSPowerUserAccess. On `ai` (741297776185) the **only** assignment is **AWSAdministratorAccess** → user `58418390-5051-7017-235c-5ae2f5980098` (= `jeppson`). `agent-ai` does not exist yet — no name clash; `iam-auth-connect` is the only other custom set and it is not assigned on `ai`.

## Verified live (2026-11-27, through the MCP server path)

- **Identity:** `sts:GetCallerIdentity` → account `741297776185`, role `AWSReservedSSO_agent-ai_d3ae8eca9c6db8bc` — the `agent-ai` set, correctly chosen over the co-assigned `AWSAdministratorAccess` set.
- **Attached on that role:** `arn:aws:iam::aws:policy/ReadOnlyAccess` (v192) + `arn:aws:iam::741297776185:policy/agent-ai` (v1, document identical to `security/agent-ai-policy.json`).
- **Scoped reads — ALLOW:** `cloudtrail:DescribeTrails` + `LookupEvents` (178 bedrock events in the last 24h visible), `logs:DescribeLogGroups`, `cloudwatch:ListMetrics` (276), `bedrock:ListFoundationModels` (125), `accessanalyzer:ListAnalyzers` (empty; via CLI — see Finding 4), `iam:ListRoles`/`GetRole`/`ListAttachedRolePolicies`/`GetPolicy`/`GetPolicyVersion`.
- **Fallback — ALLOW:** `ec2:DescribeInstances` (zero ec2 actions in the custom policy ⇒ `ReadOnlyAccess` is live).
- **Negative — DENIED:** `iam:CreateUser` → AccessDenied naming the scoped role. Admin surface closed.
- **Config surface:** `opencode.json` MCP server → `--profile ai-agent` only (dropped `djeppson`); `~/.aws/config` `[profile ai-agent]` = `sso_session dj-work` + account `741297776185` + `sso_role_name agent-ai`.

### Findings (drive the tighten phase)

1. **`IamScopedVerification` resource ARNs are broken for SSO roles.** Actual role ARNs include the SSO path: `arn:aws:iam::741297776185:role/aws-reserved/sso.amazonaws.com/us-west-2/AWSReservedSSO_agent-ai_d3ae8eca9c6db8bc` (admin set: `.../AWSReservedSSO_AWSAdministratorAccess_3780b855f22f7e4e`). The patterns `role/agent-ai-*` and `role/AWSAdministratorAccess-*` match nothing — IAM role ARNs include the path. Masked by `ReadOnlyAccess` today; **once the fallback is removed, `GetRole`/`GetRolePolicy`/`ListAttachedRolePolicies` on these roles will be denied.** Fix: `role/aws-reserved/sso.amazonaws.com/us-west-2/AWSReservedSSO_agent-ai_*` (plus the admin-set twin), or `role/aws-reserved/sso.amazonaws.com/*` for all SSO roles.
2. **CloudTrail role-name assumption wrong:** roles are `AWSReservedSSO_<set>_<hash>`, not `agent-ai-<id>`. Any CloudTrail audit filter for "the agent" must match the `AWSReservedSSO_agent-ai_` prefix.
3. **Quotas/budgets absent:** `service-quotas:*` and `budgets:*`/`ce:*` actions exist in AWS but are absent from the final policy (dropped at provisioning). If the model-gate (spend guard) or invoke-path tracks need them, re-add during tighten.
4. **MCP sandbox gap:** `access-analyzer` is unsupported in `mcp-proxy-for-aws-cli` (the CLI command is `aws accessanalyzer`); works fine via CLI. Tooling gap, not a permission gap.

## Build order (draft — expand as grilling lands)

1. DONE 2026-11-27 — Q2 = A (scoped set on `jeppson`); permission-set name = `agent-ai`
1. DONE 2026-11-27 — allowlist enumerated (read list, write list + teardown rule, never-list all agreed; invoke stays on `bedrock-invoke`) — details in the Open/Decisions sections
1. DONE 2026-11-27 — permission-set policy JSON drafted at [`security/agent-ai-policy.json`](../security/agent-ai-policy.json) (rationale in Decisions; all action names verified against docs)
1. DONE 2026-11-27 — Human: created the `agent-ai` policy in `ai` (+ `ReadOnlyAccess` fallback), set assigned to `jeppson`; role `AWSReservedSSO_agent-ai_d3ae8eca9c6db8bc` verified live; multi-set role selection empirically confirmed (see "Verified live")
1. DONE 2026-11-27 — Rescope agent surface: MCP server → `--profile ai-agent` only (dropped `djeppson`); scoped local profile `ai-agent` added; negative-test passed (`iam:CreateUser` DENIED, scoped reads ALLOW — see "Verified live")
1. PENDING — Tighten: fix `IamScopedVerification` ARNs (Finding 1); re-add quotas/budgets only if downstream tracks need them (Finding 3); **detach `ReadOnlyAccess`**; re-run the test matrix — scoped reads must still ALLOW and the `ec2:DescribeInstances` fallback check must now DENY
1. PENDING — Local hygiene: `chmod 700 ~/.aws`, `600` on config/credentials; disposition of the three static-key sections (after #5); decide what the shell-vs-read-tool gap on `~/.aws` means (keep tool-level deny + discipline, or extend the deny to shell if OpenCode supports it — check)
1. PENDING — Update AGENTS.md (`../frob/AGENTS.md`): "AWS infrastructure & Agent Tooling" section → agent uses the scoped profile, never `djeppson`; record the human-applies / agent-verifies protocol

## Future direction

- A → B upgrade (agent-only principal) if the audit separation becomes a hard requirement.
- The other seven accounts all share `db-work` and admin roles — fully out of scope for this track; candidate for a later posture pass if desired.
