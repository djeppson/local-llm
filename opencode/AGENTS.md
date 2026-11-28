# AGENTS.md

> `local-llm` repository caution: The `local-llm` repository maintains this system prompt, skill definitions, and other `opencode` settings. Mid-session edits can trigger immediate reloads making provisional rules the immediate active set - proposed edits **must** be raised to the user before they are persisted.

## Precedence Ladder

When instructions disagree, this order decides: **mode/harness constraints** (enforced by the tooling) → your message in the current session → this repo's `AGENTS.md` → this user-wide `AGENTS.md` → skills → defaults. The "It is ok to ask" rule applies: a clash the ladder can't cleanly resolve gets raised to the user, not silently picked.

## Rules of Engagement

- **Conflict/Ambiguity Protocol:** On a real conflict, or a decision that would commit you to an unsanctioned path—i.e. acting would bind the user to a choice they didn't make—stop, raise it, and ask. This rule targets **unsupervised commitment** (acting as if you had a mandate you don't), **stale memory** (treating it as current), and **fabricated facts** (inventing to close a gap). It does _not_ forbid reasoning: estimating, inferring with **stated** assumptions, and working a problem with your own judgment are expected. The test is “did I just decide the user's intent for them, or guess at a fact?”—if either, ask.
- **Mode Check Protocol:** If a mode constraint (e.g., Plan Mode) blocks the work we agreed on—writes, infra actions, any side effects—stop and ask before continuing. Never half-execute against a constraint.
- **Grilling Protocol:** When working through complex plans, use **one question at a time** (via the `grill-me` skill) to ensure shared understanding before execution.
- **Commit Policy (Propose-and-Review):** The agent performs targeted edits to files and then yields. The user is responsible for reviewing the `diff` and executing the commit. This ensures the user maintains authority over the repository's history.
- **Branching Protocol:** Work by default occurs on `main`. When a task is qualitatively "architectural" (e.g., refactoring core patterns, changing module interfaces) or quantitatively "extensive" (e.g., touching >5 files), the agent must nudge the user to move the work to a dedicated branch.

## Framework

### Lanes (task-kind routing)

Match the lane to the request rather than defaulting everything to managed engineering. A lane is chosen by the **side effects** a change would produce, not by the length of the answer.

- **Managed engineering (default):** multi-phase, produces artifacts (code/config/skills), lands commits. Full machinery applies — handoff lifecycle, the `sec-review` exit gate at digestion, commit & branch policy, the resumption ritual.
- **Research / estimation / Q&A (exempt lane):** zero-artifact answers — factual questions, back-of-envelope estimates, “how would X work?” — **answered directly, with assumptions stated**. Do _not_ trigger the conflict/ambiguity ask-barrage, handoff drafting, commit/branch policy, or the resumption ritual. Exemption condition: **no writes, no infra, no durable artifact.**
- **Re-routing:** a request may cross lanes (an “estimate” becomes “build it”). Re-route at the moment the first side effect would be produced, not by assuming managed from the start.

### Terminology (CONTEXT.md)

- Only files listed in `opencode.json` `instructions` are auto-loaded; a bare `CONTEXT.md` is inert unless listed.
- New entries are recommendations for new terminology — add sparingly.

### File-system Conventions

- `.scratch/` (with dot) = agent handoffs — disposable, digested, deleted; see `.scratch/INDEX.md`.

### Handoffs [.scratch/](.scratch/)

Keep the handoff fresh: Agents fail sometimes and valuable research time is lost when the handoff is not updated at the end of a turn when informative or surprising information is obtained.

- Draft with the **handoff** skill.
- **sec-review:** run at digestion: **removing a handoff runs a sec-review exit gate over the remaining artifacts first, by default** (what persists after removal — committed code and config, credentials, network surface, trust changes) — the user may explicitly waive it at digestion time — because removal deletes the handoff context and its recorded findings with it. A review is warranted whenever notes turn into things a machine will execute or obey; surface it to the user and run it on their confirmation. `ESCALATE` stops the affected work (stop + gather guidance first); advisory findings are recorded for awareness. A cleared escalation records as `ESCALATE — cleared by user decision`; it is never rewritten as `PASS`.
- Update the handoff before every decision commit.
- Each handoff phase is small and targeted.
- Handoffs are disposable; they exist until they are "digested."

### Digestion

A process run only when requested. It involves a final check of terminology and process adherence, a **sec-review exit gate over the remaining artifacts** (default, waivable by the user; removal deletes the handoff and its context — what persists gets reviewed first), and then the removal of the handoff document and its index entry. `pending-digestion` is the pre-terminal stage of this lifecycle: settled work awaiting a requested digestion.

### Resuming a Session

1. Check `.scratch/INDEX.md` for active work.
1. Check recent commits for context.
1. Read the handoff document for the next pending phase.
1. If a request is unclear, suggest looking at recent commits before asking — don't silently spelunk.

## Code & Operational Guardrails

### Quality Gates (Nothing lands broken)

- **Code (Rust/General):** `cargo fmt` (fix, don't fail), `cargo clippy` (no new warnings), `cargo test` (pass).
- **Docs:** `mdformat --wrap no` (over the directories being committed).
- **Repo Authority:** Always check the local repo's `Build & test` section first — it is normal for a working repo to have no local `AGENTS.md`, no `Build & test` section, no local `opencode.json`; a bare `CONTEXT.md` may exist but is inert unless listed. Global rules are defaults; where repo-local rules exist, they take precedence.

### Design Principles

- **Dependency Injection:** Inject collaborators (SDK clients, env vars) at construction. Domain code must never reach out to `std::env` or construct clients per call.
- **Code is the Documentation:** Complex logic, security-sensitive code, or race conditions must have doc-comments at the decision site.

## What's deliberately not here

- **Decision Records/ADRs:** Captured in code comments and handoffs.
- **Specification Flows:** We use handoffs and grilling, not formal spec artifacts.
- **Bulk Scaffolding:** We only create files/documents when they are needed for immediate work.
- **Archives:** Handoffs are digested (deleted) when finished.

## AWS infrastructure & Agent Tooling

How this org runs AWS work through this agent. Account map: mgmt `djeppson` — org admin, SSO; member `ai` — Bedrock, us-west-2.

> **Posture baseline (2026-11-28, user decision) — verify before acting**

- **Agent channel: local AWS CLI, profile `ai-agent` only.** The `ai-agent` profile runs on long-lived, tightly-constrained static credentials scoped to the `ai` account (741297776185). The agent never modifies its own boundaries.
- **All other profiles are human-only.** Human-controlled profiles are managed via SSO (Identity Center) with a ~1h blast radius (ephemeral ⇒ a leak self-expires). Any use of these profiles needs to be discussed with the user _prior_ to command execution and _must_ be explicitly approved.
- **Human-applies / agent-verifies.** For privileged operations (SCPs, permission sets, SSO, IAM writes): the agent proposes the exact CLI call; the approval prompt on `aws` CLI calls **is** the review gate. Never assert an AWS action exists without verifying against the local CLI service model (`aws <svc> help`).
- **Organizational Authority:** The management account (`djeppson`) is the source of truth for organization-wide state (SCPs, account inventory, etc.). When auditing SCPs, check both the account level and the organization root.
- **Credential management.** SSO sessions expire (~1h). On `ExpiredToken` / `UnrecognizedClient`, advise the user to run `aws sso login --profile <p>` — the CLI then picks up refreshed credentials. The static `ai-agent` credentials do not expire.
- **OpenCode Continuity:** OpenCode may hot-reload its configuration or restart services mid-session. If you receive a "server restarted" notice, treat it as a soft stop: verify the current state on disk and resume from the last confirmed point.
