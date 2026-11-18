# Handoff — KB reorganization (digest docs/* notes into permanent structure)

## Context

Repo is evolving into a tech-platform knowledge base (user-stated 2026-11-17). A batch of loose notes arrived as **untracked** files in `docs/` (and `machine/jeppair/`). They must be "digested" — routed into their permanent homes and deleted — while the existing axes stay intact: `docs/` = LLM stack (its README scope is authoritative), `machine/<host>/` = per-host inventory (README = context + file index), `telemetry/`, `.scratch/`.

Companion verification (done, 2026-11-17): all 11 `handoff-*.md` files are represented in `INDEX.md` — no gaps. `.scratch/notes.md` is the user's private pad (do not digest); `plan-llama-cpp-rocm.md` and `aws-cli-creds-refresh.sh` are artifacts of indexed handoffs.

Work is **managed engineering**: sequential clusters, per-gate user review + user commit (Commit Policy — never commit in-session), handoff updated before each gate.

## Locked decisions (grilled 2026-11-17)

1. `docs/` keeps LLM-stack scope; stack guides + `prompts/` do **not** move.
2. Linux/terminal/containers notes describe **dj7900** (EndeavourOS + GSkill RAM + B650 match; user-confirmed "all dj7900") → `machine/dj7900/`.
3. New flat top-level axes: `security/`, `network/`, `development/` — each gets a one-line README.
4. Pi kiosk → `machine/raspberry-pi/` (new host entry; add to `machine/README.md` hosts table).
5. `kbd67mkiirgbv3.layout.json` is the layout of the **physical kbd67 keyboard on dj7900** → `machine/dj7900/` (a `projects/` axis was proposed then retracted by user).
6. Digestion depth = **faithful merge**: move + tidy headings + merge true duplicates + fix in-cluster links only; **no prose rewrites**.

## State @ checkpoint (all 5 clusters executed; c1–c3 committed, c4–c5 gate pending)

- **Cluster 1 committed by user** (2026-11-17): all 7 files in `machine/dj7900/` (`setup.md`, `customization.md`, `audio.md`, `nginx.md`, `terminal.md`, `containers.md`, `kbd67mkiirgbv3.layout.json`); links fixed; README "Setup & how-tos" index added. Context: dead refs left untouched (`./rust-cargo.md` ×2, `linux-gpu.md`, `../src/main.rs`); starship sections in `customization.md` vs `terminal.md` complementary — kept both; credential sweep clean (only placeholder `AKIAEXAMPLE...`); inbound ref check clean pre-move; `machine/jeppair/README.md` untouched.
- **Cluster 2 committed by user** (2026-11-17): `security/` axis + README; sweep clean (no seeds; `keith.jeppson@gmail.com` in key table is an account label); intra-cluster link `./mfa-totp.md` stayed valid; no inbound refs.
- **Cluster 3 committed by user** (2026-11-17): `network/` axis + README; sweep clean (no IPs/keys/secrets); no inbound refs or internal links.
- **Cluster 4 done, awaiting user diff review + commit:** `development/` axis created; `development-tools.md` moved (untracked, plain `mv`); one-line README written (git, Homebrew, toolchain installs); sweep clean (no keys/secrets — install notes only); no inbound refs, no internal links.
- **Cluster 5 done, awaiting user diff review + commit:** `docs/raspberry-pi/` → `machine/raspberry-pi/` (plain `mv`, internal layout incl. hidden `.config/autostart/kiosk.desktop` kept); `machine/README.md` hosts table gained `jeppair/` (MacBook Air M1) + `raspberry-pi/` (kiosk) rows; self-link to `kiosk.desktop` stays valid; no inbound refs found repo-wide. `machine/jeppair/README.md` content untouched (row only).
- **`docs/` now =** `README.md` + `ollama.md` + `openwebui.md` + `vllm.md` + `prompts/` — matches the digestion condition. No loose notes remain.

## Queue (each gate: make edits → user reviews diff → user commits)

| # | Cluster | `docs/` source → new home |
|---|---------|---------------------------|
| ~~1~~ | dj7900 host notes | **committed 2026-11-17** — all into `machine/dj7900/` + README index. |
| ~~2~~ | security (new axis) | **committed 2026-11-17** — `security/` + README. |
| ~~3~~ | network (new axis) | **done, gate pending (user review + commit)** — `network.md` → `network/` + README. |
| ~~4~~ | development (new axis) | **done, gate pending (user review + commit)** — `development-tools.md` → `development/` + README. |
| ~~5~~ | raspberry-pi host | **done, gate pending (user review + commit)** — `machine/raspberry-pi/` + `machine/README.md` host rows (`jeppair/` + `raspberry-pi/`). |

Per-cluster mechanical steps (identical pattern):
1. **Cluster 1:** fix intra-cluster links in moved files: `./linux-audio.md` → `./audio.md`; the broken `dj7900.md` link in `setup.md` → `../../docs/ollama.md`. Add a "Setup & how-tos" index section to `machine/dj7900/README.md` (house pattern: README indexes host files).
2. **Clusters 2–4:** move file, add one-line README (topic + one sentence), **run credential sweep on the file before presenting the gate** (TOTP seeds in `mfa-totp.md`; VPN details in `network.md` are the risk points).
3. **Cluster 5:** `git mv`-neutral plain moves (files are untracked), keep internal layout, update `machine/README.md` hosts table (jeppair row too, while there).
4. Update this handoff's state before each gate.

## Suggested skills

- `sec-review` — at digestion only (default exit gate, user-waivable); no pre-phase gate.
- `grill-me` — only if a new ambiguity surfaces mid-execution (e.g., a cluster-3 VPN detail the user didn't anticipate); don't re-litigate locked decisions.

## Digestion condition

All 5 clusters committed by the user; `docs/` contains only README + `ollama.md` + `openwebui.md` + `vllm.md` + `prompts/`; no loose notes remain anywhere. Then: sec-review exit gate (or user waiver), remove this handoff + its INDEX entry.
