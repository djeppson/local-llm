# Handoff: AWS SSO session refresh from the remote host

Date: 2026-11-14 · Workspace: `local-llm` (diagnostics session; moved from `notes` on 2026-11-17) · Status: approach decided — scripted ssh tunnel from the Mac (original option B); script drafted at `.scratch/aws-cli-creds-refresh.sh`; first run pending. **`djeppson` credentials still stale.** · **2026-11-16: work paused** — new question raised (see `## Trust-seam question` below); goal held in abeyance.

## Context

User needs the `djeppson` SSO session (mgmt account, us-west-2) refreshed **on the session host `dj7900`** (Route53 `dj7900-local.darrenjeppson.com` → local LLM host, static IP). Work has moved to Zed on the Mac (previously OpenCode TUI in iTerm). The user wants the refresh scripted from a local terminal, staying in Zed — no app switching.

## What we established

1. `aws sso login --no-browser` still ends at `http://127.0.0.1:<random-port>/oauth/callback` on the machine where the CLI runs — `--no-browser` alone cannot serve a browser on another machine. Proven twice (port 38879; "pending authorization … expired").
1. **Chosen approach (original option B):** a scripted ssh port-forward driven from the Mac:
   - login runs **on dj7900** → creds land in dj7900's `~/.aws` (sso cache + cli cache)
   - tunnel `127.0.0.1:<port>` (Mac → dj7900) lets the Mac's browser complete the redirect
   - the human at the Mac does the browser sign-in (incl. MFA); the unattended host can never mint creds alone
1. **User's security rationale ("YubiKey model"):** the local terminal is treated as the physical persistence of credentials, so unattended remote execution must not be able to perform the refresh.
1. Host facts (verified on dj7900, 2026-11-14): aws-cli 2.34.45; profile `djeppson` = v2 `sso_session` (`db-work`), account `422622447102`, region us-west-2; `nohup`/`pgrep` present.

## Deliverable

`.scratch/aws-cli-creds-refresh.sh` (bash, runs on the Mac):

1. sshes to dj7900, kills any stale login, starts `aws sso login --no-browser --profile djeppson` in the background (`nohup` + work file), polls for the auth URL + callback port
1. opens `ssh -N -L <port>:127.0.0.1:<port>` (PID captured; `trap EXIT` kills it + cleans the work file)
1. prints the auth URL and `open`s it in the Mac browser (`--no-open` skips that)
1. waits (≤600 s, the SSO pending-auth budget) for the remote login to finish, then verifies with `aws sts get-caller-identity` on dj7900

## Current state

- Script drafted, **not yet run**; old messy draft (`aws-sso-refresh-local-script.sh`) discarded.
- `djeppson` session on dj7900 still stale; `ai` profile untouched.
- After a successful run, the refreshed `djeppson` credential is live for the SSO session's lifetime — default ~1 h; exact expiry in the sts `expiration` key in dj7900's `~/.aws` sso cache. Re-run the script when it goes stale.

## Next-session phases (small, targeted; agent edits, user commits)

1. **P1 — first run** from the Mac (Zed terminal or iTerm): `bash .scratch/aws-cli-creds-refresh.sh`. Expected: auth URL → browser → MFA → `==> OK — profile djeppson is live …`.
   - Tunnel fails → port busy on the Mac (kill stale `ssh -N -L`, or just re-run)
   - "timed out" → pending auth expired; re-run (a new attempt supersedes the stale one)
   - ssh leg fails → check the assumed ssh user (`jeppson`) and key auth Mac→dj7900
1. **P2 — confirm on dj7900:** `aws sts get-caller-identity --profile djeppson`; then an AWS MCP call to confirm the proxy picked up the refreshed credential (per the credential-management rule in the user-wide AGENTS.md).
1. **P3 — optional, only if the user agrees:** promote the script to a stable location (e.g. `opencode/`) so the `aws-cli-creds-refresh` name used in the AGENTS.md AWS section points at a real file; optionally parameterize for the `ai` profile.

## Trust-seam question (2026-11-16 — raised, deferred)

Re-evaluated the goal against the original "YubiKey" rationale (local presence = the credential). The script enforces only the weaker half:

- MFA gates the **mint**, not the **use**. After a human signs in, creds sit in dj7900 `~/.aws` for ~1h and are usable by *any* process able to read that profile. This is stock `aws sso login` behavior — the script did not introduce it, but does not guard against it.
- That includes unattended consumers: the org AGENTS.md says the AWS MCP proxy "automatically detects and uses the updated credentials." This is the `djeppson` **management / org-admin** account. The felt invariant — "presence also gates *use*" — is **not** implemented.

Stronger goal if we later want it: don't mint standing creds at all — short-lived, scoped-down, **per-operation** tokens from a broker that presence gates. That is an architecture change, not a script tweak.

Status: **valid goal, held in abeyance** — revisit before relying on `djeppson` from unattended paths.

## Open questions

- ssh user Mac→dj7900: script assumes `jeppson` — confirm.
- Should the `ai` profile be refreshed the same way (second run / profile flag)?

## Security Review (sec-review · 2026-11-14)

Result: PASS

- SE: complete — no findings
- NE: complete — no findings
- CP: complete — no findings
- SO: complete — no findings

## Suggested skills

- `handoff` — digest this doc (remove file + index entry) once the refresh is verified and the user confirms.
