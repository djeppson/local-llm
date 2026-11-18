# CONTEXT.md — common user vocabulary

Loads with the instructions (see `instructions` in `opencode.json`) — a glossary in context, not a pointer.

- **working surface** — a rules file that is in force while the session edits it (here: the user-wide AGENTS.md, worked in the local-llm repo under `opencode/`). Mid-session edits take effect when the file is re-read from disk; until then, work from the session-start copy.
