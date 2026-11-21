---
name: sec-review — Credentials & secrets (SE)
description: Credentials & secrets (SE) area of the sec-review supervisor — closed checklist of credential-handling risks, each with a CWE anchor, a published-standard anchor where applicable, and a CVSS-aligned severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the material under review matches an item's wording, and nothing else. Each item carries its **CVSS-aligned severity** (`Critical`/`High`/`Low`), a **CWE anchor**, and — where one exists — a **published anchor** (see Published anchors below).

## Checklist (closed set)

- **\[Critical\]:** credential material (keys, tokens, secret files, credential caches) written into logs, the review material itself, committed content, or any readable shared state | CWE-532 · OWASP ASI03
- **\[Critical\]:** credential material moved or exposed to a remote host without the user's local presence (local terminal = physical persistence of credentials; an unattended host may never act as their proxy) | CWE-200 · OWASP ASI03
- **\[High\]:** long-lived or shared credential reached for where a scoped, session-bound one would do | CWE-522 · OWASP ASI03 · AISVS C9.4
- **\[High\]:** credentials touched without stating scope, lifetime, or how they are verified as live | CWE: (operational — credential discipline) · Joint guidance 2026

## Guidance (what to gather on escalation)

- **[Critical] fired (credential leak into persistent state):** name the material that leaked and where it landed (item + location); whether it is still live and how that is verified; which account/role it spans; which account can rotate it. User decision needed: rotate-first vs. revoke-first, and whether a scoped, session-bound credential replaces it.
- **[Critical] fired (credential exposure to remote host):** name the exact crossing — which credential, through which path, to which destination host, and whether delivery there is confirmed. Standing position: an unattended host may never act as a credential proxy; any deviation needs an explicit user decision.
- **[High] fired (credential scope/lifetime):** the review material should state scope, lifetime, and how the credential is verified as live; prefer the scoped, session-bound credential.

## Published anchors

- **OWASP ASI03** — Identity & Privilege Abuse, *OWASP Top 10 for Agentic Applications 2026* (genai.owasp.org): inherited, cached, or leaked credentials exploited to escalate access beyond intended scope.
- **AISVS C9.4** — *OWASP AI Security Verification Standard*, Chapter C9 "Orchestration & Agentic Action" (github.com/OWASP/AISVS): agent identity and credential discipline, including credential rotation.
- **Joint guidance 2026** — *Careful Adoption of Agentic AI Services* (CISA/NSA/ACSC/NCSC-NZ/NCSC-UK, Apr 2026): replace static, long-lived secrets with ephemeral credentials that expire when the job completes; limit entitlements to the exact resources, operations, and timeframes needed.
