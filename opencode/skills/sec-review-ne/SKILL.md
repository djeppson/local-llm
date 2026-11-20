---
name: sec-review — Network / SSH exposure (NE)
description: Network / SSH exposure (NE) area of the sec-review supervisor — closed checklist of network exposure risks, each with a CWE anchor and a CVSS severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the handoff under review matches an item's wording, and nothing else. Each item carries its **CVSS severity** (`Critical`/`High`/`Low`) and a **CWE anchor** where applicable.

## Checklist (closed set)

- **[High]:** a listener, port forward, or tunnel opened without stating its auth and the trust boundary at both ends | CWE-306
- **[High]:** a credential-bearing endpoint made reachable from a lower-trust position (e.g. an OAuth callback exposed to a shared LAN/host, a port published without auth) | CWE-923
- **[Low]:** tunnels/forwards left alive past their phase with no explicit kill/trap/verify in that same phase | CWE: (operational — tunnel lifetime discipline)
- **[Low]:** firewall/DNS/routing state changed without naming the surface it exposes | CWE: (operational — routing discipline)

## Guidance (advisory context)

- **[High] fired (listener/tunnel without auth):** the phase should state the listener's auth mechanism, the trust boundary at both ends, and its lifetime bound to the phase (with explicit kill/trap/verify in the same phase).
- **[High] fired (credential endpoint exposed):** name who can reach the endpoint, from which position, with what credential; a user decision stands on the acceptability of the boundary, with any mitigation (token scoping, origin restriction, revocation path).
- **[Low] fired (tunnel/routing lifetime):** name the surface the change exposes, and keep the tunnel/forward from outliving its phase.
