---
name: sec-review SE — Credentials & secrets
description: SE area of the sec-review supervisor — closed checklist SE-1..SE-4 with class tags and CWE anchors, plus guidance on what to gather when an H1 fires. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the handoff under review matches an item's wording, and nothing else. Each item's `[class]` tag is a lookup into the class table owned by `sec-review` (tag → behavior; no judgment). Anchor codes are CWE references, not a requirement to cite them.

## Checklist (closed set)

- **SE-1 \[H1\]:** The handoff writes credential material (keys, tokens, secret files, credential caches) into logs, the handoff text itself, committed content, or any readable shared state.
- **SE-2 \[H1\]:** The handoff moves or exposes credential material to a remote host without the user's local presence. (Local terminal = physical persistence of credentials; an unattended host may never act as their proxy.)
- **SE-3 \[AD\]:** The handoff reaches for a long-lived or shared credential where a scoped, session-bound one would do.
- **SE-4 \[AD\]:** The handoff touches credentials without stating scope, lifetime, or how they are verified as live.

## Guidance (what to gather on escalation)

- **SE-1 [H1] fired:** name the material that leaked and where it landed (item + section); whether it is still live and how that is verified; which account/role it spans; which account can rotate it. User decision needed: rotate-first vs. revoke-first, and whether a scoped, session-bound credential replaces it.
- **SE-2 [H1] fired:** name the exact crossing — which credential, through which path, to which destination host, and whether delivery there is confirmed. Standing position: an unattended host may never act as a credential proxy; any deviation needs an explicit user decision.
- **SE-3 / SE-4 [AD] fired:** the phase wording should state scope, lifetime, and how the credential is verified as live; prefer the scoped, session-bound credential.
