# Handoff: Access & Hygiene (SSO, logins, root user)

**Date:** 2026-11-07 **Status:** PENDING **Prereq:** none — first in series (splits the old Bedrock account-hardening handoff, dissolved 2026-11-07)

**Context:** Hardening a new account, `ai` (741297776185), for Amazon Bedrock as a "personal remote Ollama" — privacy-first, cost-lean owner, ~$5–10/mo fixed cap. Org admin account `djeppson` (422622447102) hosts Identity Center. Identity model: SSO + passkey MFA only; no IAM users, no long-lived access keys; named SSO profile per account. Region scope: us-west-2 only (org SCP already in force).

## Verify first

- `~/.aws/config` — which SSO profiles exist; `ai` should be present, `djeppson` was reported removed
- `~/.aws/credentials` — holds a static-keys entry for `djeppson`; that is a posture violation (see Future Direction), but do not depend on it
- `ai` console — root MFA status, root access keys, root + alternate contacts

## Build order

1. PENDING — Confirm current state per "Verify first"
1. PENDING — Restore the `djeppson` SSO profile (org admin / Identity Center, 422622447102) in `~/.aws/config`, matching the shape of the working `ai` profile
1. PENDING — `aws sso login` for both `djeppson` and `ai` (user passkey); both must pass a trivial per-profile command
1. PENDING — `ai` console: root MFA is a hardware/passkey device, no root access keys exist, root + alternate contacts set

## Future direction

- Revisit the `djeppson` static-keys entry in `~/.aws/credentials`: remove it, keep SSO-only identity. Posture cleanup, not a blocker for this series.
