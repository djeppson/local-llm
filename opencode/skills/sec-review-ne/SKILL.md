---
name: sec-review — Network / SSH exposure (NE)
description: Network / SSH exposure (NE) area of the sec-review supervisor — closed checklist of network exposure risks, each with a CWE anchor, a published-standard anchor where applicable, and a CVSS-aligned severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the material under review matches an item's wording, and nothing else. Each item carries its **CVSS-aligned severity** (`Critical`/`High`/`Low`), a **CWE anchor**, and — where one exists — a **published anchor** (see Published anchors below).

## Checklist (closed set)

- **\[High\]:** a listener, port forward, or tunnel opened without stating its auth and the trust boundary at both ends | CWE-306 · Joint guidance 2026 (zero trust / least privilege)
- **\[High\]:** a credential-bearing endpoint made reachable from a lower-trust position (e.g. an OAuth callback exposed to a shared LAN/host, a port published without auth) | CWE-923 · AISVS C9.5
- **\[Low\]:** tunnels/forwards left alive past their purpose with no explicit kill/trap/verify attached to the same task | CWE: (operational — tunnel lifetime discipline) · Joint guidance 2026 (revoke when finished)
- **\[Low\]:** firewall/DNS/routing state changed without naming the surface it exposes | CWE: (operational — routing discipline)

## Guidance (advisory context)

- **[High] fired (listener/tunnel without auth):** the material should state the listener's auth mechanism, the trust boundary at both ends, and its lifetime bound to its task (with explicit kill/trap/verify attached to it).
- **[High] fired (credential endpoint exposed):** name who can reach the endpoint, from which position, with what credential; a user decision stands on the acceptability of the boundary, with any mitigation (token scoping, origin restriction, revocation path).
- **[Low] fired (tunnel/routing lifetime):** name the surface the change exposes, and keep the tunnel/forward from outliving its purpose.

## Published anchors

- **AISVS C9.5** — *OWASP AI Security Verification Standard*, Chapter C9 "Orchestration & Agentic Action" (github.com/OWASP/AISVS): agent actions authorized at execution time against fine-grained, scoped policies.
- **Joint guidance 2026** — *Careful Adoption of Agentic AI Services* (CISA/NSA/ACSC/NCSC-NZ/NCSC-UK, Apr 2026): least privilege and zero-trust patterns (cf. NIST SP 800-207); entitlements limited to exact resources, operations, and timeframes; elevated rights revoked immediately when the task finishes.
