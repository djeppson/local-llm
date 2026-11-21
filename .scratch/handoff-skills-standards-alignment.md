# Handoff — skills-standards-alignment

**Status:** active — work complete in the working tree, uncommitted, pending review

**Where:** worktree `~/.local/share/opencode/worktree/1ec3c3/skills-standards-alignment`, branch `skills-standards-alignment`, based on `main` @ `4854773`. No commits on the branch yet — all work is in the working tree.

**Updated:** 2026-11-21

## Context

The prior session's conversation was lost to a reattach failure (session pinned to the worktree cwd, client reattached from `~/projects/local-llm` → "session does not belong to cwd"). The surviving record of that session's work is the uncommitted diff itself; this handoff reconstructs the state around it. The diff is authoritative — this doc does not duplicate it.

## Work in flight (uncommitted, 6 files, +141/−105)

All under `opencode/skills/`. Read with `git diff` in the worktree.

1. **`sec-review` family aligned to published standards** — `sec-review/SKILL.md` plus area skills `sec-review-se`, `sec-review-ne`, `sec-review-cp`, `sec-review-so`:
   - Each checklist item now carries a **published-standard anchor** beside its CWE anchor — OWASP Top 10 for Agentic Applications 2026 (`ASIxx`), OWASP AISVS (`C9.x`), NIST SSDF (SP 800-218), and the CISA/NSA et al. *Careful Adoption of Agentic AI Services* (Apr 2026, "Joint guidance 2026"). Each area skill gains a `## Published anchors` section defining its references.
   - **Review target generalized** from "the handoff" to bounded "material under review": sec-review now explicitly supports direct (non-handoff) targets — a repo/directory, a diff or commit range, a config set. New hard constraints: the target is resolved never fabricated; a review never creates its own input (no generating a handoff/scratch fixture to review against).
   - Findings are reported in the conversation as each area completes; handoff-mode persistence (the `## Security Review` section) is kept for handoff targets only.
   - Cosmetic: `\[Critical\]`-style brackets escaped so they don't render as markdown links; "phase"-bound lifetimes reworded to task/purpose-bound; severity table described as "aligned to CVSS severity categories" rather than "CVSS".
1. **`write-a-skill/SKILL.md` rewritten around the Agent Skills open standard** (spec: agentskills.io; AAIF/Linux Foundation custody since Oct 2026):
   - Standard directory layout (`references/`, `assets/`, `scripts/`) replacing the legacy flat `REFERENCE.md`/`EXAMPLES.md` convention (legacy noted as still working).
   - Frontmatter rules from the spec: `name` matches the folder, 1–64 chars lowercase/digits/hyphens; `description` ≤1024 chars; optional `license`, `compatibility`, `metadata`.
   - Three-stage progressive disclosure formalized; description-as-router emphasized.
   - New "Watch upstream (AAIF)" section: versioned releases, proposal process, and skill-security guidance are on the AAIF roadmap but unshipped — this skill fills that gap until they land.

## Recovery / environment notes

- A branch checked out in a worktree cannot be checked out simultaneously in the main repo (the Zed `GitChangeBranch` error). To view the branch in an editor, open the **worktree directory** as the project (or add it as an extra folder). To move the branch into the main repo: commit the work here, `git worktree remove` the worktree, then check out the branch in the main repo.
- OpenCode sessions are pinned to their cwd. Resume old sessions only from the directory they ran in; new sessions can start anywhere.
- `.scratch/` is git-tracked in this repo (unusual, but true here) — committing this handoff on the branch is what carries it to the other system. The main repo's `.scratch/INDEX.md` and this branch's will need a routine merge when the branch lands.

## Next steps

1. User reviews the diff (propose-and-review: user executes the commit).
1. Commit on `skills-standards-alignment` — suggested as one commit ("align skills with published standards") or two (sec-review family / write-a-skill).
1. Push the branch; pick up on the other system via fetch + check out, or by opening a worktree there.
1. Open question to reconfirm with the user (the lost session held the answer): was the alignment effort scoped to these six files, or are more skills pending alignment (e.g. the promote, diagnose, or triage skills)? Do not extend scope without a user decision.

## Suggested skills

- **handoff** — keep this document current as the workstream progresses.
- **sec-review** — run at digestion of this handoff (default exit gate); note the skill under review here is sec-review itself, so the review runs against the *pre-change* committed text plus the diff.
- **write-a-skill** — if further skills are authored or aligned to the standard.
