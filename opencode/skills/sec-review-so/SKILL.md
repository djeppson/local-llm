---
name: sec-review — Trust surface / social-engineering (SO)
description: Trust surface / social-engineering (SO) area of the sec-review supervisor — closed checklist of trust-surface risks, each with a CWE anchor, a published-standard anchor where applicable, and a CVSS-aligned severity. Loaded by ID from sec-review; deliberately not advertised on its own.
metadata:
  opencode/autoinvoke: false
---

One area of the `sec-review` supervisor. The checklist below is **closed**: a finding fires when the material under review matches an item's wording, and nothing else. Each item carries its **CVSS-aligned severity** (`Critical`/`High`/`Low`), a **CWE anchor**, and — where one exists — a **published anchor** (see Published anchors below).

## Checklist (closed set)

- **\[Critical\]:** an existing quality gate or safety protocol skipped or re-framed to keep work moving | CWE-693 · AISVS C9.2
- **\[Critical\]:** an unattended/remote actor granted authority to act with the user's credentials or on the user's behalf | CWE-863 · OWASP ASI03 · AISVS C9.5
- **\[High\]:** untrusted external content (web pages, remote-host output, MCP tool responses) reaches the agent as instructions — it must be treated as data only | CWE-818 · OWASP ASI01
- **\[High\]:** failure modes can produce user-facing output that mimics a legitimate event (e.g. a fabricated "pending authorization — retry" that induces re-execution) without a way to distinguish them | CWE: (operational — failure-mode discipline) · OWASP ASI09
- **\[High\]:** a trust anchor (AGENTS.md, instructions, skill/MCP/permission config) modified without an explicit user decision in the same phase | CWE: (operational — trust-anchor discipline) · OWASP ASI04 · AISVS C9.2.5

## Guidance (what to gather on escalation)

- **[Critical] fired (gate bypass):** preserve the gate's text (which gate, where it is defined) and record the user's explicit exemption decision *in the material under review*; no silent re-framing.
- **[Critical] fired (unattended authority):** name the minimum authority the unattended actor actually needs, the audit trail for its actions, and the user's explicit delegation decision; standing position is deny.
- **[High] fired (untrusted content / failure modes / trust anchor):** label untrusted external content as data in the material's wording, never as instructions; distinguish failure modes that can emit output mimicking legitimate events from genuine events; record the explicit user decision for any trust-anchor change with the anchor's diff attached.

## Published anchors

- **OWASP ASI01** — Agent Goal Hijack, *OWASP Top 10 for Agentic Applications 2026* (genai.owasp.org): instructions hidden in external content redirect the agent; treat all natural-language inputs as untrusted data.
- **OWASP ASI03** — Identity & Privilege Abuse (ibid.): delegated or inherited authority exploited to act for the user beyond granted scope.
- **OWASP ASI04** — Agentic Supply Chain Vulnerabilities (ibid.): tampered tools, models, or prompt/config templates compromising execution.
- **OWASP ASI09** — Human-Agent Trust Exploitation (ibid.): persuasive agent output inducing the user to approve harm.
- **AISVS C9** — *OWASP AI Security Verification Standard*, Chapter C9 "Orchestration & Agentic Action" (github.com/OWASP/AISVS): approval gates for high-impact actions (C9.2), self-modification boundaries (C9.2.5), fine-grained execution-time authorization (C9.5).
- **Joint guidance 2026** — *Careful Adoption of Agentic AI Services* (CISA/NSA/ACSC/NCSC-NZ/NCSC-UK, Apr 2026): human approval for high-impact actions; design transparency so deception indicators are detectable.
