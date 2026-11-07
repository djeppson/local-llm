# Handoff: Agent Security Posture (lock down the agent's AWS surface)

**Date:** 2026-11-07 **Status:** PENDING **Prereq:** none — independent track, runs alongside the bedrock hardening series

**Context:** Interim state: the agent currently operates overpermissioned — `AWSAdministratorAccess` on both `ai` and `djeppson` profiles. Goal: replace the agent's AWS surface with a scoped, allowlisted permission set on **`ai` only**, so agent actions are auditable, boundary-locked, and never self-modifying. This session landed Q1 (surface) and parked Q2 (identity shape) at "leaning A".

**Suggested skills:** grill-with-docs — resume at Q2, one question at a time.

## Decisions (this session)

- **Q1 — agent surface (AGREED):** `ai` only. Scoped control plane: investigative reads + the specific control writes the hardening needs (budgets, invocation logging, quotas, model access, guardrail config). Zero mgmt permissions; zero on the other seven accounts. Identity Center / org / IAM-creating operations stay **human-applied** (under `djeppson`). **The agent never modifies its own boundaries** — no permission sets, SCPs, policies, or SSO.
  - Consequence: the "(under `djeppson`)" steps in the bedrock handoff series (SCP create/attach, permission-set create/assign) become human-applies / agent-verifies.
- **Model:** allowlist (scoped permission set, default-deny) rather than admin-plus-deny-lists — a deny list is only as good as what you thought to deny.
- **Process guard added to AGENTS.md today (2026-11-07):** Preflight section — mode-constraint conflicts get raised before acting, not half-executed around. (`../frob/AGENTS.md`, symlinked from this repo.)

## Open (next grilling branch)

- **Q2 — identity shape (leaning A, UNCONFIRMED):**
  - **A:** scoped `agent-ai`-style permission set assigned to `jeppson` (human identity). Passkey works as-is; auditability falls out of the machinery — each permission set materializes as a distinct IAM role on `ai`, so CloudTrail separates agent actions (scoped role) from human-admin actions (`AWSAdministratorAccess` role) even under the same person.
  - **B:** dedicated Identity Center user that alone may receive the set — adds the guarantee "no human principal can hold the agent policy", at the cost of a second identity (extra passkey registration or password flow, one more SSO user). Trivially upgradeable from A later; the policy is identity-agnostic.

## Verified (local machine, 2026-11-07)

- `~/.aws/config`: nine account profiles, **all `AWSAdministratorAccess`**, one shared `db-work` SSO session; `fin`/`certbot` chain via `source_profile = djeppson`.
- `~/.aws/credentials`: three static key sets — one is `djeppson` (flagged posture violation in an earlier handoff); the other two have not been named yet.
- Permissions: `~/.aws/` is `755`, `config`/`credentials` are `644` (world-readable on a laptop).
- `opencode.json` already denies the agent `read` on `**/.aws/**` — but the **shell** tool reads the same files without check; the guardrail covers a tool, not the path.
- AWS MCP server (`mcp-proxy-for-aws-cli` → AWS-managed endpoint, per AGENTS.md) is configured for profiles `ai djeppson` — the agent's *remote* surface today is full admin on both accounts.
- The `djeppson` SSO profile appears **restored** in local config (previously the open item in handoff-access-hygiene) — its phases should be checked off next session.

## Build order (draft — expand as grilling lands)

1. PENDING — Confirm Q2 (A vs B); settle the permission-set name (e.g. `agent-ai`)
1. PENDING — Enumerate the allowlist: investigative reads + control writes, and the explicit never-list (identity, SCPs, policies, SSO, org). Decide whether invoke/test actions live here or stay on `bedrock-invoke`
1. PENDING — Draft the permission-set policy JSON (allowlist; rationale stays in handoff/AGENTS.md since JSON can't carry prose)
1. PENDING — Human: create the permission set in Identity Center (1h session), assign to `jeppson`; verify the new role exists on `ai`
1. PENDING — Rescope agent surface: MCP server profiles → scoped profile only (drop `djeppson`); add the scoped local profile; negative-test (an admin action rejected, a scoped read accepted)
1. PENDING — Local hygiene: `chmod 700 ~/.aws`, `600` on config/credentials; disposition of the three static-key sections (after #5); decide what the shell-vs-read-tool gap on `~/.aws` means (keep tool-level deny + discipline, or extend the deny to shell if OpenCode supports it — check)
1. PENDING — Update AGENTS.md (`../frob/AGENTS.md`): "AWS infrastructure & Agent Tooling" section → agent uses the scoped profile, never `djeppson`; record the human-applies / agent-verifies protocol

## Future direction

- A → B upgrade (agent-only principal) if the audit separation becomes a hard requirement.
- The other seven accounts all share `db-work` and admin roles — fully out of scope for this track; candidate for a later posture pass if desired.
