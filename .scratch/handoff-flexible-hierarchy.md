# Handoff: flexible instruction hierarchy + extraction of mechanical work

Date: 2026-11-17 · Workspace: `local-llm` (moved from `notes` on 2026-11-17) · Status: A-pilot (lane fix) committed 2026-11-17; goals + grounded current-state captured; B-pilot to choose; open decisions #2–#5 pending — ready to resume for the build.

## Context

We stress-tested the current instruction stack against a casual research question ("how many tennis balls fit in an average pool"). The friction it exposed:

- The always-on stack (`AGENTS.md` + `CONTEXT.md`, loaded via `opencode.json` `instructions`) is a **managed multi-phase engineering framework**. A zero-artifact Q&A has no lane in it, so it gets routed through work-management machinery (ask-first, handoff/commit/resume rituals) instead of simply being answered.
- Sharpest conflict: **`Conflict/Ambiguity Protocol` — "Do not attempt to resolve via inference."** It reads as "unsupervised," when the intent is "without user direction" — not "think without a brain." The phrase collides with estimation questions, which are *defined* by making reasonable assumptions and stating them.
- No explicit "exempt" clause: the only current shield is the buried `Bulk Scaffolding` line in "What's deliberately not here."

**User direction (2026-11-17):** create this handoff. Scope = two workstreams — **(A)** a more flexible instruction hierarchy; **(B)** abstract the core *mechanical* pieces into code, tools, and skills.

## Goals

- **A. Flexible hierarchy** — the stack should adapt to the *kind* of task (research/estimation/Q&A vs. managed engineering) rather than defaulting everything to the managed path. Concretely: fix the "by inference" wording; add an explicit **exempt lane** for zero-artifact answers (direct answer, no handoff/commit/ask-barrage); make precedence something a machine can consult, since the ladder currently bottoms at an unstated "defaults."
- **B. Extract mechanical pieces** — move the deterministic, verifiable bits out of prose into **code / tools / skills**, leaving prose only for judgment calls the model must make. The governing principle is already our own: from `handoff-promote-skill.md` → "User Review," a skill knows **when** and a tool executes **deterministically**.

## Current state (grounded)

- **Auto-load tier:** `opencode.json` `instructions` = `[AGENTS.md, CONTEXT.md]`; `default_agent: "plan"` (a plan/research mode split already exists — the "lane" idea must *reconcile* with it, not fight it); the Precedence Ladder is **prose** in `AGENTS.md`.
- **On-demand tier:** skills under `opencode/skills/` (canonical in this repo; `~/.config/opencode` is a single whole-directory symlink to `local-llm/opencode/`): `handoff`, `sec-review` (+ `sec-review-se/ne/cp/so`), `grill-me`, `diagnose`, `triage`, `write-a-skill`, `promote`. This **is** the flexible/progressive-disclosure half of the hierarchy — the rigidity is in the always-on files.
- **Code:** cargo package `notes` (`src/main.rs`, `src/bin/mdshare.rs`, dep `expanduser`) — a natural home for deterministic checks. Gates per `AGENTS.md`: `cargo fmt/clippy/test` + `mdformat --wrap no`.
- **Tools:** OpenCode builtins (shell/read/edit/grep/webfetch/websearch/subagent/skill/question) + `aws` MCP; **Code Mode (`execute`)** is available as a scripted tool-call/HTTP runtime — a candidate vehicle for "tools" without a new binary.
- **Extraction precedent:** `sec-review` is already decomposed into focused sub-skills — the "split one big instruction into small skill+code units" pattern is proven in this repo.

## Candidate mechanical pieces (for B)

Each is a good fit for a deterministic check + a thin skill that knows when to run it:

- **Quality gates** (`cargo fmt/clippy/test` + `mdformat` + "repo `Build & test` first") → `notes gate` (code) + `gate` (skill).
- **Handoff invariant** ("the handoff reflects the last commit, always") + `INDEX.md` consistency → `notes handoff-check` (code) + a freshness step in the `handoff` skill.
- **Lane/precedence routing** (which protocol/skill applies to this request) → a detector: Code Mode or a `route` skill.
- **Digestion** (terminology check + `sec-review` exit gate + removal) → orchestration: a skill calls code, then the gate.
- **Domain blocks** (AWS/Bedrock ops, design principles, resumption ritual) → move to on-demand skills; keep `AGENTS.md` lean.

**Target end-shape (candidate, pending decisions):** `AGENTS.md` reduced to precedence-as-data, the lane definitions, the 2–3 inviolables, and pointers to skills. Deterministic logic lives in the `notes` crate (+ Code Mode for glue); skills describe *when* and *what to call*; prose keeps only the judgment calls.

## Open decisions (resolve before authoring)

1. **Priority/pilot — RESOLVED 2026-11-17:** lane fix first (A), then build (B). Pilot = the safe, prose-only `AGENTS.md` delta: rewrite the "by inference" wording + add the exempt lane for zero-artifact Q&A; the code/skills platform (B) follows. B-pilot piece still to choose (candidate: **quality-gate**).
1. **Vehicle for "code":** extend the existing `notes` cargo package, a new package, or Code-Mode/`execute`-only (no compiled binary)?
1. **Hierarchy representation:** a data file (e.g. `lanes.json`) the agent consults, vs. keep prose + a detector that infers the lane?
1. **Scope of B:** start with the top 2–3 pieces, or do a full survey of every prose rule first?
1. **Relationship to `promote`:** that workstream's "User Review" already asks for "a scripted (deterministic, executable) tool the skill knows how to call" — fold `promote` onto the same code/skills platform, or keep it separate?

## Next

1. **Resolve remaining open decisions** — Vehicle for "code" · hierarchy representation · scope of B · relationship to `promote` (decisions #2–#5) — one at a time.
1. **Branch:** the *implementation* is architectural (new skills + crate changes + `AGENTS.md` restructure) — per `Branching Protocol`, move it to a dedicated branch rather than `main`. (This handoff, a `.scratch/` scratchpad, stays on `main`.)
1. **Author the B-pilot** as a (code + skill) pair — candidate: the **quality-gate** — and test it against the research-estimate question class.
1. Digestion + `sec-review` only when a handoff settles to removal.

> **Done this session (committed 2026-11-17):** A-pilot — the safe, prose-only `AGENTS.md` delta: rewrote the `Conflict/Ambiguity Protocol` (dropped "by inference"; scoped to unsupervised commitment / stale memory / fabricated facts) and added `Framework → Lanes` (managed-engineering default + research/estimation/Q&A exempt lane + re-routing). Verified in place at `opencode/AGENTS.md` (Conflict/Ambiguity @ L11; Lanes @ L19–L25).

## Suggested skills

- `grill-me` — resolve the open decisions, one at a time.
- `write-a-skill` — when authoring new skills.
- `diagnose` — if a piece (detector/gate) misbehaves.
- `sec-review` — at digestion, and when a machine-obeyed artifact (the crate/tools/skills) lands — default exit gate, waivable.

## Security notes

- This handoff intentionally names **no** credentials, profile names, or secret/infra specifics (per the `promote` escalation lesson — keep machine-obeyed bodies clean). Domain ops content stays in the existing config, referenced by path only.

## Security Review (sec-review · 2026-11-21)
Result: ESCALATE — 1 Critical finding (SO), NOT cleared by user. Do not proceed on the affected work (digestion/removal of this handoff). The AGENTS.md Lanes prose adjustment is separate work, outside this triage's scope.
- SE: complete — no findings
- NE: complete — no findings
- CP: complete — no findings
- SO: complete
  - concern: "Research / estimation / Q&A (exempt lane): ... Do _not_ trigger the conflict/ambiguity ask-barrage, handoff drafting, commit/branch policy, or the resumption ritual. Exemption condition: **no writes, no infra, no durable artifact.**" | where: opencode/AGENTS.md → Framework → Lanes (Research/estimation/Q&A exempt lane, ~L24) | severity: Critical | CWE: CWE-693 · AISVS C9.2

**User decision (2026-11-21):** escalation NOT cleared. The user judged that the AGENTS.md Lanes prose reads as a silent gate bypass and needs adjustment so the Conflict/Ambiguity Protocol re-framing is explicit rather than implied by the "no writes, no infra, no durable artifact" condition. That adjustment is separate work outside this triage. The handoff stays on disk as `pending-digestion (blocked)` until the prose is fixed and the exit gate re-run.

Do not proceed on the affected work. Gather guidance first: SO Guidance for [Critical] gate-bypass — "preserve the gate's text (which gate, where it is defined) and record the user's explicit exemption decision *in the material under review*; no silent re-framing." The fired checklist item: an existing quality gate or safety protocol (the Conflict/Ambiguity Protocol) skipped or re-framed to keep work moving.
