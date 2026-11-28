---
name: handoff-lifecycle
description: Manage `.scratch/` handoffs across their lifecycle — the states (new, active, pending-digestion), `INDEX.md` bookkeeping, and digestion (the pre-removal checklist, the waivable sec-review exit gate, and removal). Use when asked to digest a handoff, mark one pending-digestion, or explain what a handoff's state means.
argument-hint: "the handoff to act on (defaults to the pending-digestion entry in .scratch/INDEX.md)"
---

Owns the handoff lifecycle: the states, the `INDEX.md` bookkeeping, and the terminal digestion event. Drafting the handoff document is the **handoff** skill's job; the security gate itself is the **sec-review** skill's job — this skill sequences them.

## States

- **new** — intake: the handoff exists, but no decisions or progress have been made yet.
- **active** — work is in progress.
- **pending-digestion** — the pre-terminal stage: all phases complete; what remains is the user's commit and a requested digestion.

There is no "digested" state: digestion is an **event** that deletes the handoff and its index entry — afterwards the handoff is simply gone. Historical references to digested handoffs (telemetry, docs, commit messages) are expected and left in place.

Transitions: created → `new`; first decision or phase begins → `active`; work settled (nothing left but commit + digestion) → `pending-digestion`; digestion event → removed.

## INDEX.md

One line per handoff:

- **`<state>`** — [handoff-name.md](handoff-name.md) — a one-line summary of what it is + where the work stands.

Update the state word in place when the handoff transitions. Digestion removes the line entirely.

## Digestion (the terminal event)

**Runs only on explicit user request.** Marking a state (e.g. "mark X pending-digestion") is a separate allowed action and never triggers removal.

1. **Pre-removal checklist.** The handoff is the only container for the session's context and recorded findings, and removal is irreversible — answer "what survives the deletion?" first:
   - **Terminology:** surface any new recurring terms from the finished work as recommendations for `CONTEXT.md` (or explicitly decline) — while the context is still warm.
   - **Durability:** confirm the durable subset of the work is captured in durable form (docs, commits, config). If knowledge exists *only* in the handoff, distill it first (e.g. a `docs/` or `machine/` note).
   - **State:** confirm the handoff has no open phases and its `INDEX.md` entry is consistent (correctly at `pending-digestion`). Open phases block digestion — surface them and let the user decide.
1. **Waiver question.** Unless the user's request already explicitly waived the gate ("no security review needed"), ask: *"Do you want to waive the security review? Recommendation: …"* — ground the recommendation in the checklist results (e.g. inert docs and commits only → recommend waiving; changed live config, credentials, network surface, or trust anchors → recommend running the gate).
1. **sec-review exit gate.** If not waived: invoke the **sec-review** skill over the *remaining artifacts* — what persists after the handoff is removed (committed code and config, credentials, network surface, trust changes). The handoff is the map; the artifacts are the target. The gate's own semantics (ESCALATE, cleared-by-user, the `## Security Review` section) are defined by sec-review — do not restate them here. An `ESCALATE` stops the affected work: stop and gather guidance before proceeding.
1. **Removal.** Delete the handoff document and its `INDEX.md` line.

Order matters: the gate runs *before* removal because removal deletes the handoff's context and recorded findings with it — what survives is what gets reviewed.
