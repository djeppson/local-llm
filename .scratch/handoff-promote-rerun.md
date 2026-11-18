# Handoff: `promote` skill scrubbing and sec-review rerun

Date: 2026-11-17 · Workspace: `local-llm` (moved from `notes` on 2026-11-17) · Status: scrub complete, sec-review reset pending — **rerun required**.

## Context

The goal was to create and install a new `promote` skill. The initial implementation of the skill and the handoff document both contained a hard-stop (H1) security finding: referencing the specific location of a GitHub token (`~/.config/gh/hosts.yml`) in the text.

The user requested a scrub of these references.

## Current State

- **`opencode/skills/promote/SKILL.md`**: Scrubbed. The mention of the `~/.config/gh` token path has been replaced with general capability/verification requirements.
- **`.scratch/handoff-promote-skill.md`**: Scrubbed. All specific mentions of the token/file location and the historical SE-1 finding findings have been removed.
- **`.scratch/handoff-promote-skill.md` (Review section)**: Incomplete. The `Security Review` section is currently in a broken/truncated state because the previous session hit the output limit while attempting to update it.

## Next Steps

1. **Fix the handoff document**: Rewrite the `Security Review` section in `.scratch/handoff-promote-skill.md` to a clean `IN PROGRESS (0/4)` state.
1. **Rerun the security review**: Execute the `sec-review` skill (which will spawn SE, NE, CP, SO subagents) against the scrubbed handoff and the scrubbed skill.
1. **Digestion**: If the review passes, proceed with digesting the handoff.

## Suggested skills

- `sec-review` — to rerun the review once the handoff is reset.
- `handoff` — to create the final handoff once the review passes.
