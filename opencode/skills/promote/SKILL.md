---
name: promote
description: Promote a workstream's handoff and project brief out of `notes` into its own repo under `~/projects` — clone an empty repo, stand the scaffold, copy brief and handoff (freshness fixes only), set up `.scratch/` with INDEX and a minimal `AGENTS.md`, run the gates, leave the commit to the user. Use when the user asks to "promote" a handoff or project, spin a project off, or give it its own standalone repo.
---

# Promote

Re-home a workstream: the working state (handoff) and the durable intent (project brief, a README) move from `notes/.scratch/` to the new repo — brief at root, handoff in the repo's own `.scratch/` — and the work continues there. `notes` stays pure config: its copies become known transient duplicates until a requested digestion.

## Preconditions (verify before acting)

- The workstream's artifacts exist in `notes`: a handoff in `.scratch/` plus its project brief (README, e.g. `.scratch/<project>/README.md`).
- The target repo **exists, is empty, and is reachable**: `git ls-remote -h <remote>` → empty list, exit 0 — a successful `ls-remote` *is* the auth-path proof (ssh preferred; https fallback if the org uses one). Never name a credential or its storage location in handoff or skill text; state the capability and verify it by use.
- Repo **creation** is out of scope: if there is no empty repo yet, stop and ask how/where it should be created.

## Steps

1. **Clone** the empty repo into `~/projects/<name>`.
1. **Scaffold** the project type: Rust → `cargo init` (bin package; `.gitignore` carries `/target`; `Cargo.lock` is committed). Other stacks: the repo-appropriate equivalent.
1. **Copy the brief verbatim**: `notes` `.scratch/<project>/README.md` → `<repo>/README.md`. No edits.
1. **Copy the handoff**: → `<repo>/.scratch/<name>.md`. Allowed deviations are **mechanical freshness fixes only**, each one disclosed to the user: the workspace pointer (`notes` → new repo plus path/remote), links broken by the move (most often the brief's new location), and stale `Location`/`Next` lines (executed steps drop). No other content or meaning changes.
1. **New index**: `<repo>/.scratch/INDEX.md` in the standard format, one `active` entry.
1. **Minimal repo `AGENTS.md`**: handoff/README conventions plus a `Build & test` section with the repo's gates (repo-authority rule: the local section is checked first).
1. **Gates, all green**: Rust → `cargo fmt`, `cargo clippy` (no new warnings), `cargo test`; markdown → `mdformat --wrap no` over what is being committed.
1. **Yield for commit** (propose-and-review): the agent stages the tree; the user reviews the diff and commits + pushes (the first push seeds the empty repo).

## Notes-side bookkeeping (always, after the above)

- The `notes` copy of the handoff moves to **`pending-digestion`**: update its status line (history preserved inline) and flip its INDEX entry — `pending-digestion`, promoted to `<repo>`, notes copy a known transient duplicate.
- Do **not** delete the `notes` copy: removal is still a requested digestion with its sec-review exit gate.

## sec-review at promotion (default, waivable by the user)

Every promotion ends with a security review of what *persists after the move* — the committed brief, handoff, and scaffold, plus the `notes`-side residue — and is user-settled on 2026-11-17. Load the `sec-review` skill and present the result: `ESCALATE` halts the affected work pending the user's guidance; advisory findings are recorded and surfaced. Waiver must be the user's explicit words.
