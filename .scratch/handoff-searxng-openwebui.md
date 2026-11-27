# Handoff — SearXNG ↔ Open WebUI web-search/RAG (+ `:8411` exposure)

**Date:** 2026-11-26 · **Machine:** dj7900 (endeavor-7900) · **Status:** NEW TRACK — spun off from the Ollama-consolidation sec-review. Web search / RAG in Open WebUI "not working as expected"; **not yet diagnosed.** Deferred future work, not urgent.

## Goal

Diagnose and fix web search / RAG in Open WebUI (backed by SearXNG), and decide the disposition of the LAN-exposed `:8411` port.

## Why this is a separate track

Spun out of the Ollama-consolidation digestion — it was the one **out-of-scope** finding there (the **NE High**: SearXNG published on `0.0.0.0:8411` with no auth). The functional "web search not working" concern is the same component and belongs with it. The Ollama consolidation itself is complete; this is the remaining loose end on SearXNG.

## Current state (verified 2026-11-26)

**SearXNG (`searxng-core` container):**
- Image: `docker.io/searxng/searxng:${SEARXNG_VERSION:-latest}` — **NOT pinned** (uses `latest` unless `SEARXNG_VERSION` is set in the env).
- Port: `0.0.0.0:8411:8411` (LAN-exposed, no auth) — the NE High.
- Env: only `SEARXNG_PORT=8411`. `SEARXNG_BIND_ADDRESS`, `SEARXNG_LIMITER`, `SEARXNG_SECRET` are **not** set in the compose file.
- Config `core-config/settings.yml` (bind-mounted to `/etc/searxng/`, i.e. **live**):
  - `search.formats: [html, json]` — **json IS enabled** (so the #1 "JSON format not enabled" cause is ruled out).
  - `server.limiter: false` (client won't be rate-limited), `public_instance: false`.
  - `server.bind_address: 127.0.0.1`, `port: 8888` (overridden to 8411 by `SEARXNG_PORT`).
  - `server.secret_key` — **hardcoded in the file** (a secret; do not paste it).
- Cache: named volume `local-llm_core-data` → `/var/cache/searxng/`.

**Open WebUI (`open-webui` container):**
- Pinned **v0.9.4** (v0.9.5 **regressed web retrieval** → rolled back; the pin is load-bearing).
- `network_mode: host`; `SEARXNG_API_URL=http://localhost:8411`.
- Admin Settings (in `webui.db`, last read 2026-11-11): **RAG web search enabled**, engine `searxng`, `http://localhost:8411`, lang `all`, 8 results; custom RAG prompt template (inline `[id]` citations).

## Suspects (rough order)

1. **Open WebUI-side** — the known v0.9.5 web-retrieval break (already rolled back to v0.9.4); confirm v0.9.4's SearXNG path actually works with the current `webui.db` config (lang `all`, custom template).
2. **Endpoint reachability / binding** — verify the published `:8411` actually serves JSON (first diagnostic below). Config `bind_address: 127.0.0.1` + unset `SEARXNG_BIND_ADDRESS` is a candidate to confirm.
3. **Unpinned image** — `latest` may have drifted to a version that changed JSON API / behavior; consider pinning a known-good tag.
4. **The `:8411` exposure** — decide loopback-only vs LAN (below), independent of the functional fix.

## First diagnostic (disambiguating)

```sh
curl -sS 'http://localhost:8411/search?q=test&format=json'
```
- **Returns JSON** → endpoint + json format + reachability all OK → problem is **Open WebUI-side** (config / RAG path / version).
- **Fails** (refused / timeout / HTML) → problem is the **SearXNG container** (binding / publish / image drift).

Then read `podman logs --tail 100 searxng-core` and `podman logs --tail 100 open-webui` (grep `searx`/`rag`/`web search`), and re-test the Open WebUI "web search" toggle with the same query.

## The `:8411` exposure decision (NE High, carried from consolidation)

- **Option A (recommended — matches the stack's loopback-only pattern):** bind loopback-only: `0.0.0.0:8411:8411` → `127.0.0.1:8411:8411` (Open WebUI reaches it via host `localhost`; no LAN exposure). Closes the CWE-923 finding.
- **Option B:** keep it LAN-exposed but add auth (SearXNG token / `users.yml`) and document the trust boundary — only if LAN access to SearXNG is actually wanted.

## References (not duplicated here)

- `podman-compose.yml` — both container definitions.
- `core-config/settings.yml` — live SearXNG config (large; read by section).
- `docs/openwebui.md` — Open WebUI setup, the v0.9.5 pin note, `webui.db` location.
- `docs/ollama.md` — sibling component (context only).
- SearXNG docs — https://docs.searxng.org (JSON format, limiter, token auth).

## Suggested skills (next session)

- **diagnose** — reproduce → instrument → fix loop for the web-search failure.
- **sec-review** — only if the `:8411` decision changes the network surface (Option B adds auth; re-review that surface).

## Guardrails

- `core-config/` is the **live** SearXNG config (bind-mounted) — changes take effect on container restart; treat as live, not reference.
- `webui.db` holds a secret (HF API key) — don't paste the config JSON; keep backups private.
- Open WebUI is **pinned** — don't bump the version without re-testing the SearXNG RAG path first.
