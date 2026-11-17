# Open WebUI on dj7900 (endeavor-7900)

How Open WebUI is set up on this machine. Focus: Open WebUI itself — its stack mates (Ollama, SearXNG, nginx) are noted only at the pointers level and can be documented separately.

Verified live: **2026-11-11**.

## TL;DR

- **What** — Open WebUI **v0.9.4** (pinned — 0.9.5 regressed web search, see [Gotchas](#gotchas))
- **How it runs** — Rootless **Podman** container (`open-webui`) in the `local-llm` compose stack, **host network**, port **8080**
- **Managed by** — User systemd unit `local-llm` (enabled, autostart)
- **Data** — Named volume `local-llm_owui-data` → `/app/backend/data`
- **Access** — `http://localhost:8080` direct; `https://dj7900-local.darrenjeppson.com/` via nginx (443)
- **Config** — Mostly in the UI (persisted to `webui.db`); three endpoints via env vars in the compose file
- **Health** — `curl http://127.0.0.1:8080/health` → `{"status":true}`

## File map (Open WebUI-specific)

- `~/projects/local-llm/podman-compose.yml` — defines the `open-webui` container (image pin, env, volume)
- `~/.config/systemd/user/local-llm.service` — `podman compose up -d` / `down` for the whole stack
- `~/projects/local-llm/local-llm.service` — symlink to the unit (repo convenience)
- `~/.local/share/containers/storage/volumes/local-llm_owui-data/_data/` — Open WebUI state: `webui.db`, `vector_db/`, `uploads/`, `cache/`

## How it runs

- **Container:** image `ghcr.io/open-webui/open-webui:v0.9.4`, `network_mode: host`, `restart: always`, entrypoint `bash start.sh` which launches **uvicorn, 1 worker** (`UVICORN_WORKERS:-1`), binding `0.0.0.0:8080`.

- **Supervision:** user service `local-llm` (checked `active`, enabled). Start/stop it and the Open WebUI + SearXNG containers come up/down together.

- **Env vars** (compose file, the only Open WebUI env overrides):

- `OLLAMA_BASE_URL` — `http://localhost:11434` — local LLM backend

- `SEARXNG_API_URL` — `http://localhost:8411` — web-search backend for RAG

- `OPENAI_API_BASE_URL` — `https://router.huggingface.co/v1` — external "OpenAI-compatible" connection

- **Access:**

  - LAN: `https://dj7900-local.darrenjeppson.com/` — nginx (`/etc/systemd/system/nginx-local.service`, config `~/projects/nginx-local/conf.d/default.conf`) proxies 443 → `127.0.0.1:8080` with buffering disabled and 30-min timeouts for LLM streaming.
  - Localhost: `http://localhost:8080` (host networking, no port mapping).

## Configuration

Open WebUI has two configuration surfaces:

1. **Env vars** (above) — only used to seed initial connection URLs.
1. **Admin Settings in the UI** — the live source of truth, persisted to the `config` table (single JSON row) in `webui.db`. Current state (read from the DB on 2026-11-11):

- **Signups** — **disabled** (`ui.enable_signup: false`) — single user
- **User** — `darren.jeppson@gmail.com` (role `admin`) — the only account
- **Ollama** — enabled, `http://localhost:11434`
- **External OpenAI-compatible connection** — **enabled** → HuggingFace router (`router.huggingface.co/v1`) with an **HF API key stored in the DB**
- **RAG web search** — **enabled**, engine `searxng`, `http://localhost:8411`, lang `all`, 8 results
- **RAG prompt template** — custom — inline `[id]` citations only when the source has an explicit id
- **Chats stored** — 8
- **Knowledge bases / API keys / models table / custom functions, pipelines, extensions** — all **empty** — model list is fetched live from Ollama

> ⚠️ `webui.db` contains a secret (the HF API key). Keep backups of that directory private, and don't paste the config JSON into chat.

## Data & state

Everything lives in one named volume, `local-llm_owui-data`, mounted at `/app/backend/data` (z-flag):

```text
~/.local/share/containers/storage/volumes/local-llm_owui-data/_data/
├── webui.db, webui.db-wal, webui.db-shm   # ~2 MB — users, chats, all config
├── vector_db/                             # ~217 MB — RAG embeddings (SQLite)
├── uploads/                               # user uploads
└── cache/                                 # ~1.1 GB — embedding/tiktoken/whisper model caches
```

- **Backup** = `tar` that one directory (cleanest with the container stopped, or after `sqlite3 webui.db "PRAGMA wal_checkpoint(TRUNCATE);"`).
- Regenerating `cache/` is safe (it refetches models). `vector_db/` and `uploads/` are not.

## Day-2 operations

```sh
# Status / logs
systemctl --user status local-llm
podman logs --tail 100 open-webui

# Restart (single container, config unchanged)
podman compose -f ~/projects/local-llm/podman-compose.yml restart open-webui

# Update Open WebUI (careful — see pin note)
# 1. edit image tag in ~/projects/local-llm/podman-compose.yml
# 2. podman compose -f ~/projects/local-llm/podman-compose.yml pull open-webui
# 3. podman compose -f ~/projects/local-llm/podman-compose.yml up -d open-webui
# 4. test web search + RAG before keeping it; commit the compose file
#    (git history is the version record, e.g. 44a2449 "revert Open WebUI to fix broken Web search")

# Shell inside (debug)
podman exec -it open-webui bash
```

## Gotchas

- **Keep the pin.** v0.9.5 broke web retrieval; the stack was rolled back to v0.9.4 for that reason (compose comment + git history). If updating, test the SearXNG RAG path first, and restore `v0.9.4` if search regresses.
- 1 uvicorn worker is fine for single-user use; raise `UVICORN_WORKERS` only if needed.
- The TLS cert for the domain was reported **expired** in prior research notes (2026-11-11). Out of scope here, but it affects access via `dj7900-local.darrenjeppson.com` — verify cert renewal before treating "not reaching the site" as an Open WebUI issue.

## Related components (pointers only)

- **Ollama** (LLM, ROCm/GPU, `:11434`) — user service `~/.config/systemd/user/ollama.service`; models in `~/.ollama/models/`
- **SearXNG** (web search, `:8411`) — sibling container `searxng-core` in the same `podman-compose.yml`; config in `~/projects/local-llm/core-config/`
- **nginx** (TLS, `:443` → `:8080`) — `~/projects/nginx-local/` + `/etc/systemd/system/nginx-local.service`
- **Cert renewal** (certbot → S3 → `~/projects/nginx-local/certs/`) — see `~/projects/nginx-local/README.md`
