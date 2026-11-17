# Handoff — Hugging Face token hygiene

**Status:** active — rotate done; scrub done; verifications open.

## What happened

`notes/guides/vllm.md` (now moved to `docs/vllm.md`) contained two inline copies of a Hugging Face access token (`hf_Btjh…`, public-read-only scope, last used ~2026-07-27). The token was committed to `djeppson/notes` (private repo). During the `it-landscape-consolidate` move the two literals were scrubbed to `${HF_TOKEN:?set HF_TOKEN from ~/.cache/huggingface/token}`.

## Done

- [x] **User rotated the token** at huggingface.co/settings/tokens on 2026-11-17 (old value revoked; new public-read-only token stored in `~/.cache/huggingface/token`). Confirmed: old prefix no longer present in the token file.
- [x] **Scrubbed on move:** both literals in `docs/vllm.md` replaced with `${HF_TOKEN:?…}`. `grep` confirms no token literals remain under `docs/`.
- [x] **Old value stays in `notes` git history** — accepted (token revoked, private repo); no history rewrite.

## Open (verify before digest)

- [ ] **Open WebUI external connection:** `docs/openwebui.md` records that an HF API key for `router.huggingface.co` is stored inside Open WebUI's `webui.db`. If it was the **same** key that was revoked, that connection is now dead — confirm it still works, or update the key in Open WebUI → ⚙️ Admin Settings → Connections → OpenAI. If it's a different key, close this item.
- [ ] **Other locations:** scan for the old token prefix in `~/.config`, `~/projects`, and shell rc files (a prior `grep` of shell rc came back clean; the repo grep is clean after the move).

## Digestion condition

Both verifications above pass (or are waived by the user).
