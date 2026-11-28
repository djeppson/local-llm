# Handoff: Agent Security Posture (lock down the agent's AWS surface)

**Date:** 2026-11-07 **Status:** IN PROGRESS — steps 1–3 done (2026-11-27); next: step 4 — human creates the `agent-ai` permission set in Identity Center **Prereq:** none — independent track, runs alongside the bedrock hardening series

**Context:** Interim state: the agent currently operates overpermissioned — `AWSAdministratorAccess` on both `ai` and `djeppson` profiles. Goal: replace the agent's AWS surface with a scoped, allowlisted permission set on **`ai` only**, so agent actions are auditable, boundary-locked, and never self-modifying. This session landed Q1 (surface) and parked Q2 (identity shape) at "leaning A".

**Suggested skills:** docs-verify — for step 4+ provisioning checks; grilling is done for steps 1–3.

## Triage (2026-11-21)

**Decision: Keep.** Head of the AWS security chain — Q1 already landed in `AGENTS.md` as a preflight guard; one decision (Q2 identity shape) unblocks the seven-step build order. Abandoning would cascade to the downstream two.

**Next step + LOE:** Resume grill at Q2 (A vs B identity shape, settle permission-set name) → unblocks allowlist enumeration. **[S = \<1hr]** — single-decision grilling, no artifacts/infra yet.

**Dependencies:** `model-gate-guardrails` and `invoke-path` both depend on this being applied first (the "handoff-access-hygiene" prerequisite named in model-gate-guardrails is this track). Keep this and the chain stays alive.

## Decisions

- **Q2 — identity shape (AGREED 2026-11-27): A** — scoped set assigned to `jeppson`; no dedicated SSO user. Audit separation falls out of the machinery: agent actions land in the scoped role on `ai`, human-admin actions in the `AWSAdministratorAccess` role — CloudTrail separates by role, same person. B stays a future upgrade (policy is identity-agnostic; re-assignment is a 1h human step).
- **Permission-set name (AGREED 2026-11-27): `agent-ai`** — Identity Center set name; produces CloudTrail role `agent-ai-<id>`. Deliberately not `*-readonly`: the set includes scoped control writes (budgets, logging, quotas).
- **Policy JSON (AGREED 2026-11-27):** draft at [`security/agent-ai-policy.json`](../security/agent-ai-policy.json) — 12 pure-allow statements (default-deny; no Deny blocks), zero invoke actions, structurally cannot touch identity/SSO/org. Deltas settled at approval: `PutUseCaseForModelAccess` **out** (Anthropic-only one-time form, human-shaped); **no** `aws-marketplace:Subscribe` (Z.AI has no product key — docs; add scoped by `aws-marketplace:ProductId` if a product-key model becomes the gate); quota-tracking reads **in** (`GetRequestedServiceQuotaChange`, `ListRequestedServiceQuotaChangeHistory`); IAM reads include `arn:aws:iam::741297776185:policy/*` so `GetPolicy`/`GetPolicyVersion` can actually read the attached policies.
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
- **2026-11-27 addendum (docs check):** SSO profile-flow role selection when a user holds multiple permission sets on `ai` (admin + `agent-ai` \[+ possibly `bedrock-invoke`\]) is **unverified** — `GetRoleCredentials` is per-role, but no profile-config role-pinning key confirmed in docs yet. Deterministic fallback: scoped profile = admin SSO profile as `source_profile` + `role_arn` AssumeRole into `agent-ai-<id>`. Verify empirically after the set is created.

## Build order (draft — expand as grilling lands)

1. DONE 2026-11-27 — Q2 = A (scoped set on `jeppson`); permission-set name = `agent-ai`
1. DONE 2026-11-27 — allowlist enumerated (read list, write list + teardown rule, never-list all agreed; invoke stays on `bedrock-invoke`) — details in the Open/Decisions sections
1. DONE 2026-11-27 — permission-set policy JSON drafted at [`security/agent-ai-policy.json`](../security/agent-ai-policy.json) (rationale in Decisions; all action names verified against docs)
1. PENDING — Human: create the permission set in Identity Center (1h session, `djeppson`), assign to `jeppson`; verify the new role exists on `ai` — then empirically confirm the multi-set role-selection fallback (see 2026-11-27 addendum)
1. PENDING — Rescope agent surface: MCP server profiles → scoped profile only (drop `djeppson`); add the scoped local profile; negative-test (an admin action rejected, a scoped read accepted)
1. PENDING — Local hygiene: `chmod 700 ~/.aws`, `600` on config/credentials; disposition of the three static-key sections (after #5); decide what the shell-vs-read-tool gap on `~/.aws` means (keep tool-level deny + discipline, or extend the deny to shell if OpenCode supports it — check)
1. PENDING — Update AGENTS.md (`../frob/AGENTS.md`): "AWS infrastructure & Agent Tooling" section → agent uses the scoped profile, never `djeppson`; record the human-applies / agent-verifies protocol

## Future direction

- A → B upgrade (agent-only principal) if the audit separation becomes a hard requirement.
- The other seven accounts all share `db-work` and admin roles — fully out of scope for this track; candidate for a later posture pass if desired.
