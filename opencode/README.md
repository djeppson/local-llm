# OpenCode global config

Global-scoped OpenCode config lives in this directory, under the `local-llm` repo. It reaches the runtime as a **single symlink**: `~/.config/opencode -> ~/projects/local-llm/opencode`. Everything OpenCode loads from that directory is a real, git-managed file — no per-file or per-skill symlinks remain.

## What is in here

- `opencode.json` — the global config document (model, providers, MCP, permissions, `instructions` array).
- `skills/` — the skill registry, one directory per skill (including `sec-review`'s `sec-review-{se,ne,cp,so}` sub-skills).
- `AGENTS.md` — user-wide rules (the working surface while its owning repo is being edited).
- `CONTEXT.md` — the user-wide glossary.
- This `README.md`.
- `.gitignore` — keeps OpenCode's runtime state out of git (see below).

`AGENTS.md` and `CONTEXT.md` are listed in `opencode.json`'s `instructions` array — the single source of truth for which instruction text gets injected:

```json
"instructions": [
  "~/projects/local-llm/opencode/AGENTS.md",
  "~/projects/local-llm/opencode/CONTEXT.md"
]
```

## Runtime state

OpenCode also writes runtime state into `~/.config/opencode/`. Since that path is this directory, the state lands in the checkout: `node_modules/`, `package.json`, `package-lock.json`, `cli.json`, `service.json`, `agents/`, and `auth.json` (if ever created). `.gitignore` keeps all of it out of git — the config is the only durable content here.

## Provenance

- 2025-05 (`6b4286c`): symlink-based delivery from the `notes` config repo — per-file link for `opencode.json`, per-skill links for `skills/`, managed by the POC Rust dotfiles app in that repo.
- 2025-11 (`df1d8f6`): `AGENTS.md` / `CONTEXT.md` de-symlinked and delivered via the `instructions` array instead; structural links kept.
- 2026-11-17: config moved from `notes/config/.config/opencode/` into `local-llm/opencode/`; `~/.config/opencode` became the single whole-directory symlink; the Rust app's `opencode.json` link entry was dropped; runtime state moved into the checkout and git-ignored. The `df1d8f6` mechanism was retired **by explicit user direction** — this is a sanctioned supersession, not a quiet revert.
