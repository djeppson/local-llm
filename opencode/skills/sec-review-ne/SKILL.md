---
name: sec-review — Network / SSH exposure (NE)
description: Network / SSH exposure (NE) area of the sec-review supervisor — closed checklist NE-1..NE-4 with class tags and CWE anchors, plus advisory guidance on new network surface. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the handoff under review matches an item's wording, and nothing else. Each item's `[class]` tag is a lookup into the class table owned by `sec-review` (tag → behavior; no judgment). Anchor codes are CWE references, not a requirement to cite them.

## Checklist (closed set)

- **NE-1 \[A1\]:** The handoff opens a listener, port forward, or tunnel without stating its auth and the trust boundary at both ends.
- **NE-2 \[A1\]:** The handoff makes a credential-bearing endpoint reachable from a lower-trust position (e.g. an OAuth callback exposed to a shared LAN/host, a port published without auth).
- **NE-3 \[AD\]:** The handoff leaves tunnels/forwards alive past their phase with no explicit kill/trap/verify in that same phase.
- **NE-4 \[AD\]:** The handoff changes firewall/DNS/routing state without naming the surface it exposes.

## Guidance (advisory context)

- **NE-1 [A1] fired:** the phase should state the listener's auth mechanism, the trust boundary at both ends, and its lifetime bound to the phase (with explicit kill/trap/verify in the same phase).
- **NE-2 [A1] fired:** name who can reach the endpoint, from which position, with what credential; a user decision stands on the acceptability of the boundary, with any mitigation (token scoping, origin restriction, revocation path).
- **NE-3 / NE-4 [AD] fired:** name the surface the change exposes, and keep the tunnel/forward from outliving its phase.
