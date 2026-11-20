---
name: sec-review — Credentials & secrets (SE)
description: Credentials & secrets (SE) area of the sec-review supervisor — closed checklist of credential-handling risks, each with a CWE anchor and a CVSS severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the handoff under review matches an item's wording, and nothing else. Each item carries its **CVSS severity** (`Critical`/`High`/`Low`) and a **CWE anchor** where applicable.

## Checklist (closed set)

- **[Critical]:** credential material (keys, tokens, secret files, credential caches) written into logs, the handoff text itself, committed content, or any readable shared state | CWE-532
- **[Critical]:** credential material moved or exposed to a remote host without the user's local presence (local terminal = physical persistence of credentials; an unattended host may never act as their proxy) | CWE-200
- **[High]:** long-lived or shared credential reached for where a scoped, session-bound one would do | CWE-522
- **[High]:** credentials touched without stating scope, lifetime, or how they are verified as live | CWE: (operational — credential discipline)

## Guidance (what to gather on escalation)

- **[Critical] fired (credential leak into persistent state):** name the material that leaked and where it landed (item + section); whether it is still live and how that is verified; which account/role it spans; which account can rotate it. User decision needed: rotate-first vs. revoke-first, and whether a scoped, session-bound credential replaces it.
- **[Critical] fired (credential exposure to remote host):** name the exact crossing — which credential, through which path, to which destination host, and whether delivery there is confirmed. Standing position: an unattended host may never act as a credential proxy; any deviation needs an explicit user decision.
- **[High] fired (credential scope/lifetime):** the phase wording should state scope, lifetime, and how the credential is verified as live; prefer the scoped, session-bound credential.
