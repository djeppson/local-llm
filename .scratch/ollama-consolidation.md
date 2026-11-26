# Handoff — Ollama consolidation (systemd + official binary)

**Date:** 2026-11-26 · **Machine:** Arch, RX 7900 XTX (gfx1100, 24 GiB) · **Status:** Cutover to official binary/systemd service verified; AUR removal remains. · **Next session:** Remove AUR packages and clean up shadowed user-level service.

## Goal
One canonical install: **systemd service** running the **official binary** `/usr/local/bin/ollama`, with the **AUR packages removed**.

## Observed State (2026-11-26)
- [x] **Cutover:** The service is `active` and running `/usr/local/bin/ollama serve` via `/etc/systemd/system/ollama.service` (system-level).
- [x] **Store:** Models are resident in `/var/lib/ollama/.ollama/models`.
- [ ] **AUR Removal:** `ollama` and `ollama-rocm` packages are still installed via `pacman`.
- [ ] **Cleanup:** A user-level service exists at `~/.config/systemd/user/ollama.service` and should be reviewed/removed to avoid confusion.

## Pending Steps
1. **AUR Removal:** `sudo pacman -R --noconfirm ollama ollama-rocm`.
2. **User-service Cleanup:** Disable/remove `~/.config/systemd/user/ollama.service`.
3. **Final Verification:** Ensure no other `ollama` binaries exist in `PATH` and `systemctl is-active ollama` remains stable.

## Recovery runbook
- If service fails: `journalctl -u ollama -n 100 --no-pager`.
- If binary issues: Verify `/usr/local/bin/ollama` is the one in `PATH`.
- Rollback store: `sudo mv /var/lib/ollama/.ollama/models /home/jeppson/.ollama/models`.
