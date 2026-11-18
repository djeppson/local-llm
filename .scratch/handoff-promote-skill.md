# Handoff: `promote` — skill for moving a settled handoff into its own repo

Date: 2026-11-17 · Workspace: `local-llm` (moved from `notes` on 2026-11-17) · Status: brief settled — process captured, constraints set (below), open decisions listed; next is decision resolution, then skill authoring.

## Context

2026-11-16/17: the `handoff-infinity-agent-runtime` work moved out of `notes` and into its own repo — `~/projects/ia` (github `djeppson/ia`): clone the empty repo, `cargo init`, copy the project brief and the handoff (freshness fixes only), stand a `.scratch/` with INDEX, add a minimal repo `AGENTS.md`, run the gates, user reviews and commits. The user found the process good and wants it captured as a reusable OpenCode **skill**: "promote" a settled handoff into an independent repo (skill work lives in this repo: `opencode/skills/`, canonical).

## The captured process (as executed for the infinity promotion)

1. **Pre-checks:** target repo exists and is empty (`git ls-remote -h <repo>` → empty, exit 0); a working auth path to the remote (ssh preferred; https as fallback when the org has one configured) — prove it with `ls-remote`, never name a credential or its location in handoff text; toolchain + git identity present (cargo 1.97.1).

- User review: I would like to understand the `gh` notes above and what the token being referred to is for.

1. **Clone** the empty repo into `~/projects/<name>`.
1. **Scaffold:** `cargo init` (bin package; `.gitignore` contains `/target`; `Cargo.lock` committed).
1. **Copy the brief** — `notes` `.scratch/<project>/README.md` → repo root `README.md`, verbatim.
1. **Copy the handoff** — → `<repo>/.scratch/`, applying **mechanical freshness fixes only** (workspace pointer, links broken by the move, stale Location/Next lines) — no other content edits, each one disclosed to the user.
1. **New index** — `<repo>/.scratch/INDEX.md` in the same format, one `active` entry.
1. **Repo `AGENTS.md`** — minimal: `.scratch/` = handoffs, README = source of truth for intent, and a `Build & test` section (repo-authority rule: the local section checks first).
1. **Gates:** `cargo fmt` / `clippy` / `test` pass; `mdformat --wrap no` over the markdown.
1. **Commit policy:** agent stages the tree; user reviews the diff and commits/pushes (first push seeds the empty repo).

## Constraints (user-settled 2026-11-17)

- **sec-review is part of the promotion process** — every promotion ends with a security review over what persists after the move (committed brief/handoff/scaffold, and the notes-side residue). Same shape as the digestion exit gate: default, waivable by the user. The user will run the **infinity promotion's** review in a separate session (recorded 2026-11-17).
- **Notes-side lifecycle:** promotion moves the notes copy to `pending-digestion` (settled, awaiting a *requested* digestion) — removal still requires the explicit digestion request + its sec-review exit gate. The notes copy stays as a known transient duplicate until then (infinity case: both copies live).

## Open decisions (resolve before authoring)

- **Name/invocation:** `promote`? `promote-repo`? — pick the verb the user will actually type.
- **Scope:** Rust/cargo repos only (what both uses are today) or generic (clone + brief + handoff + per-project gates)?
- **Empty-repo assumption:** first promotions start from a pre-created empty GitHub repo. Should the skill also cover *creating* the repo (no `gh` — mechanism undecided), or only consume an existing empty one?
- **Duplication policy:** is notes-side `pending-digestion` always the post-promotion state, or per-case?

## Next

1. User runs the security review for the infinity promotion (separate session) — recorded 2026-11-17.
1. Resolve the open decisions (grill, one at a time).
1. Author the skill under `opencode/skills/<name>/` per `write-a-skill`; house formatting applies (`mdformat`); delivery is via the `~/.config/opencode` → `local-llm/opencode/` whole-directory symlink.
1. First dry run against a throwaway empty repo, or the next real promotion.

## Suggested skills

- `write-a-skill` — when authoring begins.
- `grill-me` — one-question-at-a-time for the open decisions.
- `sec-review` — the promotion exit gate (see Constraints).

## Security Review (sec-review · 2026-11-17)

Result: **ESCALATE** (1 H-class finding; run complete 4/4)

- SE: complete
  - SE-1 · SE — the handoff writes the credential's location into its own text — "gh CLI is not installed — token sits in `~/.config/gh/hosts.yml` if needed" — naming a token + secret file in the handoff body; the same wording survives in `config/.config/opencode/skills/promote/SKILL.md` (Preconditions) — The captured process, step 1 "Pre-checks"; also SKILL.md Preconditions — H1. Guidance to gather: whether the `djeppson` gh OAuth token is still live and how that is verified; which account/role it spans; which account can rotate it; **user decision needed: rotate-first vs revoke-first, and whether a scoped, session-bound credential replaces it.**
  - SE-3 · SE — leans on a long-lived/shared gh credential where a scoped, session-bound credential would do — The captured process, step 1 "Pre-checks" — AD. Phase wording should state scope, lifetime, liveness check; prefer the scoped, session-bound credential.
  - SE-4 · SE — touches the credential without stating scope, lifetime, or liveness verification — The captured process, step 1 "Pre-checks" — AD.
- NE: complete — no findings
- CP: complete — no findings
- SO: complete — no findings

Do not proceed on the affected phase. Gather guidance first: the user decision above — the token reference is **uncommitted** in `notes` (handoff + skill SKILL.md, both staged); no committed content carries it; the token *value* is not named anywhere, only the file location. Digestion of this handoff is held until the escalation is resolved/cleared.

Digestion exit gate: object of review is the remaining artifacts — what persists after this handoff is removed. Principal target: `opencode/skills/promote/SKILL.md` (a machine-obeyed instruction file, the durable outcome of this workstream), plus the promotion it describes (`~/projects/ia` state) and the `notes`-side residue.

## User Review

- Would like this to become a scripted (deterministic, executable) tool that the skill would be responsible for knowing how to call
