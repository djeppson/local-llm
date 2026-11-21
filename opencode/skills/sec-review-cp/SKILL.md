---
name: sec-review — Code unsafe patterns (CP)
description: Code unsafe patterns (CP) area of the sec-review supervisor — closed checklist of code-level unsafe patterns, each with a CWE anchor, a published-standard anchor where applicable, and a CVSS-aligned severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the material under review matches an item's wording, and nothing else. Each item carries its **CVSS-aligned severity** (`Critical`/`High`/`Low`), a **CWE anchor**, and — where one exists — a **published anchor** (see Published anchors below), plus a short operational-discipline tag where the risk is operational rather than a CWE weakness.

## Checklist (closed set)

- **\[Critical\]:** improper neutralization of special elements in a command (OS command injection) — e.g. unquoted variable expansion, `eval`/`sh -c`, pipes from untrusted sources into a shell | CWE-78 · OWASP ASI05 · NIST SSDF
- **\[Critical\]:** improper control of code generation or execution — e.g. `eval`/`exec`, `subprocess` with `shell=True`, `pickle.loads`, `yaml.load` without `SafeLoader` | CWE-94 · OWASP ASI05
- **\[High\]:** unsafe memory operations without a documented safety contract — e.g. Rust `unsafe` blocks, C pointer arithmetic, unchecked array bounds, manual memory management | CWE-119 (operational — memory safety discipline)
- **\[High\]:** check-then-act on a file or resource with no atomicity or lock where a race is possible | CWE-367
- **\[High\]:** destructive operation (force-push, mass delete, drop/recreate, credential wipe) with no backup/verify step in the same phase | CWE: (operational — destructive discipline) · AISVS C9.2

## Guidance (safety context)

- **[Critical] fired (command injection / code execution):** prefer language-native invocation (quoting, parameterized APIs, non-`shell=True`, safe deserialization); any dynamic-input path should be named at the decision site. These are remote-code-execution class — do not mitigate by documentation alone.
- **[High] fired (memory safety / races):** name the safety contract / atomicity mechanism at the decision site, or remove the check-then-act. These are reliability / data-loss class — documentation is the safety contract.
- **[High] fired (destructive op):** the plan needs a backup/verify step in the *same* phase; name the rollback path and what is verified before and after; destructive scope is a user decision.

## Published anchors

- **OWASP ASI05** — Unexpected Code Execution, *OWASP Top 10 for Agentic Applications 2026* (genai.owasp.org): agent-generated or attacker-controlled code reaching execution (RCE class).
- **NIST SSDF** — *Secure Software Development Framework*, NIST SP 800-218 (and its GenAI community profile, SP 800-218A): secure development practices for code produced in AI-assisted workflows.
- **AISVS C9.2** — *OWASP AI Security Verification Standard*, Chapter C9 "Orchestration & Agentic Action" (github.com/OWASP/AISVS): reversibility classification and approval requirements for irreversible, high-impact actions.
