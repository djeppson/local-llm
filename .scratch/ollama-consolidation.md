# Handoff — Ollama consolidation (systemd + official binary)

**Date:** 2026-11-26 · **Machine:** Arch, RX 7900 XTX (gfx1100, 24 GiB) · **Status:** Cutover verified; AUR packages removed; 11434/11435 port inconsistency documented (restart landmine). · **Next session:** START with the decision — resolve the redundant user-unit + repo `ollama.service` symlink (Pending Steps #1); verification ✅; port decision deferred.

## Goal
One canonical install: **systemd service** running the **official binary** `/usr/local/bin/ollama`, with the **AUR packages removed**.

## Observed State (2026-11-26)
- [x] **Cutover:** The service is `active` and running `/usr/local/bin/ollama serve` via `/etc/systemd/system/ollama.service` (system-level).
- [x] **Store:** Models are resident in `/var/lib/ollama/.ollama/models`.
- [x] **AUR Removal (done 2026-11-26):** `ollama` and `ollama-rocm` uninstalled via `pacman`.
- [ ] **Cleanup:** A user-level service exists at `~/.config/systemd/user/ollama.service` and should be reviewed/removed to avoid confusion.
- [ ] **Symlink Alignment:** The repo's `ollama.service` symlink currently points to the redundant **user** unit; it must be repointed to the live **system** unit to align with the live-redirect map.
- [ ] **Symlink Scope:** Symlink changes (repointing, deletion, or copying contents to new files) are **in scope** for this work. **Caution:** the system prompt (AGENTS.md "keep the symlinks" rule) may be outdated — user has sanctioned treating the symlink as a normal artifact here.

## AUR non-use confirmation (2026-11-26)
- [x] `ldd` on `/usr/local/bin/ollama`: only system base libs; binary ships its own libs in `/usr/local/lib/ollama/`, including a self-contained `rocm_v7_2/` — AUR `ollama-rocm`'s `libggml-hip.so` is not loaded.
- [x] `lsof` on running service: zero open handles into AUR-owned paths (`/usr/bin/ollama`, `/usr/lib/ollama/*`); child `llama-server` is from `/usr/local/lib/ollama/`.
- [x] Active unit is `/etc/systemd/system/ollama.service`; AUR's `/usr/lib/systemd/system/ollama.service` is shadowed, never loaded.
- [x] `which ollama` → `/usr/local/bin/ollama`; AUR `/usr/bin/ollama` shadowed.
- Note: official binary may link system ROCm stack (libhsa etc.) — removing the two AUR packages does not touch it.

## ⚠️ Documented inconsistency: 11434 vs 11435 (2026-11-26)
- **State:** Running server binds **11434** (default; started 23:21). Drop-in `/etc/systemd/system/ollama.service.d/blue-green.conf` (added 23:43, *after* start — not yet in effect) sets `OLLAMA_HOST=127.0.0.1:11435`.
- **Consumers on 11434:** Open WebUI (`podman-compose.yml` `OLLAMA_BASE_URL=http://localhost:11434`), OpenCode (`opencode.json` `baseURL: http://127.0.0.1:11434/v1`), all docs.
- **Landmine:** Next `systemctl restart ollama` binds 11435 → breaks Open WebUI, OpenCode (this session's provider), and everything else on 11434.
- **Decision (user, 2026-11-26):** Leave as-is, document only. Port direction undecided. Do NOT restart the service until this is resolved.

## Verification (2026-11-26, re-confirmed)
- ✅ System unit `active` + `enabled`, running `/usr/local/bin/ollama serve` as `ollama`.
- ✅ Single binary in `PATH` (`/usr/local/bin/ollama`); AUR gone.
- ✅ Serving **127.0.0.1:11434** (11435 not bound; blue-green drop-in pending, not in effect).
- ⚠️ User unit `inactive` but **enabled on boot** (latent 11434 conflict).
- ⚠️ Repo `ollama.service` symlink → user unit (stale).

**One-liner:** `systemctl is-active ollama; systemctl cat ollama | grep -Ei 'ExecStart|OLLAMA_HOST'; ss -ltnp | grep -E '11434|11435'; which -a ollama`
Expect: `active` · ExecStart → `/usr/local/bin/ollama serve` · config shows **11435** (pending) · `ss` shows **11434** (live bind) · one binary.

## Pending Steps
1. **NEXT — decide the redundant user-unit + repo symlink** (start here): user unit is enabled-on-boot and binds 11434 (latent conflict); repo symlink points at it (stale). Symlink changes + content-copying are **in scope**; AGENTS.md "keep symlinks" rule may be outdated (user-sanctioned). Options:
   - **(a) Keep canonical + track (recommended):** disable user unit (keep file as ref); repoint repo symlink → live system unit; update repo AGENTS.md live-redirect map.
   - **(b) Remove + drop tracking:** disable + delete user unit; remove repo symlink.
   - **(c) Disable only:** disable user unit; leave file + symlink as-is (stale).
2. **Final Verification:** ✅ **done (2026-11-26)** — see Verification section.
3. **Deferred (user decision pending):** Resolve 11434 vs 11435 (see above) — keep 11434, or complete the move to 11435 across all consumers + docs.

## Completed
- [x] **AUR Removal (2026-11-26):** `pacman -Qs ollama` → empty; AUR `ollama` + `ollama-rocm` uninstalled. Service remained active; server still on 11434.

## Recovery runbook
- If service fails: `journalctl -u ollama -n 100 --no-pager`.
- If binary issues: Verify `/usr/local/bin/ollama` is the one in `PATH`.
- Rollback store: `sudo mv /var/lib/ollama/.ollama/models /home/jeppson/.ollama/models`.
