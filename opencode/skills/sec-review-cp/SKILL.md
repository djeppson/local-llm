---
name: sec-review — Code unsafe patterns (CP)
description: Code unsafe patterns (CP) area of the sec-review supervisor — closed checklist CP-1..CP-5 with class tags and CWE anchors, plus safety guidance for destructive operations (A2). Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the handoff under review matches an item's wording, and nothing else. Each item's `[class]` tag is a lookup into the class table owned by `sec-review` (tag → behavior; no judgment). Anchor codes are CWE references, not a requirement to cite them.

## Checklist (closed set)

- **CP-1 \[AD\]:** The handoff uses shell with unquoted variable expansion of untrusted data, `eval`/`sh -c` with dynamic input, or pipes from untrusted sources into a shell (CWE-78).
- **CP-2 \[AD\]:** The handoff uses Python `subprocess` with `shell=True` on untrusted input, `eval`/`exec`, or unsafe deserialization — `pickle.loads`, `yaml.load` without `SafeLoader` (CWE-94).
- **CP-3 \[AD\]:** The handoff uses Rust `unsafe` blocks without a documented safety contract at the decision site, or `unwrap`/`expect` on data that can fail or is external.
- **CP-4 \[AD\]:** The handoff performs check-then-act on a file or resource with no atomicity or lock where a race is possible (CWE-367).
- **CP-5 \[A2\]:** The handoff runs a destructive operation (force-push, mass delete, drop/recreate, credential wipe) with no backup/verify step in the same phase.

## Guidance (safety context)

- **CP-5 [A2] fired:** the phase needs a backup/verify step in the *same* phase; name the rollback path and what is verified before and after; destructive scope is a user decision.
- **CP-1 / CP-2 [AD] fired:** prefer language-native invocation (quoting, non-`shell=True`, safe deserialization); any dynamic-input path should be named in the handoff.
- **CP-3 [AD] fired:** Rust `unsafe` needs a documented safety contract at the decision site; `unwrap`/`expect` needs a statement that failure is impossible there.
- **CP-4 [AD] fired:** name the atomicity/lock mechanism, or the wording should remove the check-then-act.
