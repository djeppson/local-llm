---
name: sec-review — Code unsafe patterns (CP)
description: Code unsafe patterns (CP) area of the sec-review supervisor — closed checklist of code-level unsafe patterns, each with a CWE anchor and a CVSS severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the handoff under review matches an item's wording, and nothing else. Each item carries its **CVSS severity** (`Critical`/`High`/`Low`) and a **CWE anchor** where applicable. plus a short operational-discipline tag where the risk is operational rather than a CWE weakness.

## Checklist (closed set)

- **[Critical]:** improper neutralization of special elements in a command (OS command injection) — e.g. unquoted variable expansion, `eval`/`sh -c`, pipes from untrusted sources into a shell | CWE-78
- **[Critical]:** improper control of code generation or execution — e.g. `eval`/`exec`, `subprocess` with `shell=True`, `pickle.loads`, `yaml.load` without `SafeLoader` | CWE-94
- **[High]:** unsafe memory operations without a documented safety contract — e.g. Rust `unsafe` blocks, C pointer arithmetic, unchecked array bounds, manual memory management | CWE-119 (operational — memory safety discipline)
- **[High]:** check-then-act on a file or resource with no atomicity or lock where a race is possible | CWE-367
- **[High]:** destructive operation (force-push, mass delete, drop/recreate, credential wipe) with no backup/verify step in the same phase | CWE: (operational — destructive discipline)

## Guidance (safety context)

- **[Critical] fired (command injection / code execution):** prefer language-native invocation (quoting, parameterized APIs, non-`shell=True`, safe deserialization); any dynamic-input path should be named in the handoff. These are remote-code-execution class — do not mitigate by documentation alone.
- **[High] fired (memory safety / races):** name the safety contract / atomicity mechanism at the decision site, or remove the check-then-act. These are reliability / data-loss class — documentation is the safety contract.
- **[High] fired (destructive op):** the phase needs a backup/verify step in the *same* phase; name the rollback path and what is verified before and after; destructive scope is a user decision.
