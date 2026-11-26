# AGENTS.md — local-llm

This is a **docs + live-config repo, not a code project.** Nothing builds, there is no test suite. The local LLM stack is the largest tenant; host inventory, agent tooling, and ancillary services also live here.

## Read first

1. `README.md` — stack overview, endpoints, and **Testing/Verification** for confirming live changes.
1. User-wide agent rules live in [`opencode/AGENTS.md`](opencode/AGENTS.md) (auto-loaded by OpenCode). Per its precedence ladder, **this file governs work in this repo; it wins over the global file here.** Inherited protocols (commit policy, handoffs, lanes) are not restated.

## Live redirect map — read before editing

Some files in this repo **are** the running system (or the machine-wide agent config). Editing them has immediate or restart-gated live effects:

| In this repo                    | Actually                                                                             | Editing it                                                                                                                                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `local-llm.service` (symlink)   | systemd **user** unit `~/.config/systemd/user/local-llm.service`                     | live user unit; starts `podman compose -f <this repo>/podman-compose.yml up -d` with `WorkingDirectory=<this repo>`                                                                                                             |
| `ollama.service` (symlink)      | systemd **user** unit in the same dir                                                | live user unit (Ollama, loopback-only)                                                                                                                                                                                          |
| `nginx-local.service` (symlink) | systemd **system** unit `/etc/systemd/system/`                                       | live **system**-scoped unit — different reload path than the user units                                                                                                                                                         |
| `podman-compose.yml`            | the compose file the `local-llm` unit runs                                           | live stack (Open WebUI `:8080`, SearXNG `:8411`); change takes effect on `podman-compose up` / unit restart                                                                                                                     |
| `core-config/`                  | bind-mounted as `/etc/searxng/` in the live `searxng-core` container                 | **live SearXNG config, not reference material**                                                                                                                                                                                 |
| `opencode/`                     | the **global** OpenCode config — `~/.config/opencode` is a symlink to this directory | `AGENTS.md`, `CONTEXT.md`, `opencode.json`, `skills/` are injected with hot-reload into **every session of every repo on this machine**. User confirmation required before persisting edits (per the global file's own caution) |

Traps agents have tripped on:

- The `*.service` symlinks are the mechanism, not clutter — **keep them as symlinks.** Don't replace them with file copies, delete them, or "clean them up."
- `machine/raspberry-pi/.config/` is **staging material for the Pi** (deployed there), not this host's live config and not a symlink.
- `opencode/` can accumulate runtime state files (e.g. `cli.json`, `service.json`, `node_modules`, `package.json`) written by OpenCode — those are transient, gitignored, and **not** configuration.
- "Docs" vs "live": `machine/`, `docs/`, `telemetry/`, `security/`, `network/`, `development/` are knowledge-base notes — edits are inert. The table above is the live surface — verify after editing (README Testing/Verification).
- Large files in context: prefer **sliced reads** — `grep`, `sed -n "X,Yp"`, `head`/`tail`, or offset/limit — over dumping whole files (e.g. `cat core-config/settings.yml` ≈ 20k tokens). For multi-step surveys of large material, hand the work to a subagent and keep only its conclusions in this session.

## Where things live

- `machine/` — per-host hardware inventory + live diagnostics; `dj7900/` is the primary LLM host.
- `docs/` — stack setup guides + experiment notes; `prompts/` holds prompt-engineering notes.
- `telemetry/` — point-in-time baselines; newest date first.
- `core-config/` — live SearXNG config (see map above).
- `opencode/` — global agent config + skills (see map above).
- `.scratch/` — agent handoffs; **disposable**, lifecycle + state in `INDEX.md`. On resuming work, check `INDEX.md` before anything else.
- `scratch/` — user scratchpads; **permanent** — never digest, delete, or reorganize.

## Quality gates (repo-specific)

- No build/test cycle exists; "nothing lands broken" here means:
  - Markdown: `mdformat --wrap no` over the directories being committed.
  - YAML (`.service`, `*.yml`): `yamllint` per `.yamllint.yml`.
  - Live-config changes: verified per README **Testing/Verification** (`podman-compose ps`, service endpoints) before being called done.

## What belongs where

- **Repo-specific rules → this file.** Keep it short; this map is its job.
- **User-wide / cross-repo rules → `opencode/AGENTS.md`** (a live file — confirm before editing).
- **Knowledge** (how X works, what was tried, hardware facts) → `docs/` / `machine/`, not this file.
