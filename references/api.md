# StrudelHub API

Base: `https://strudelhub.com`. Server source: `github.com/cameltech-jp/strudel-hub` (AGPL, FastAPI, `server/strudel_hub/routes/sessions.py`) — the facts below come from that file and from live probes (2026-10-13). The browser runs **`@strudel/repl@1.3.0`** (unpkg; visible in `GET /api/recorder`): verify Strudel functions against that tag, not `main`.

**API key**: only via the environment variable `STRUDELHUB_API_KEY`. Never print it (`echo`, logs, `curl -v`), write it to a file or inline it in a command — even if the user pastes it in chat: export it once for the shell session and reference it only as `$STRUDELHUB_API_KEY`. The scripts (`hub.py`, `*.sh`) read it from the environment and never print it. Header: `Authorization: Bearer $STRUDELHUB_API_KEY`; without a key, **no header**.

## Who may call what

A session has a `visibility` (`private` · `public_read` · `public_all`) and an `agent_mode` (`auto` · `review`). Sessions created **without a key are `public_all` + `auto`**, owner-less; with a key they are `private`, owned by the key's user. The owner can change both in the browser (Session Settings).

| Endpoint | `public_all` | `public_read` | `private` |
|---|---|---|---|
| `POST /code`, `/play`, `/stop`, `/versions/{v}/revert` | anyone | key + owner | key + owner |
| `GET /status` | **key required** (any key) | key + owner | key + owner |
| `GET /versions`, `/versions/{v}`, `/events` (SSE), `GET /sessions/{id}` | anyone | anyone | key + owner |
| `PATCH/DELETE /sessions/{id}`, `/draft/accept`, `/draft/decline`, `/publish` | browser cookie only — never the agent |||

Errors: `401 {"error":"API key required"}` / `{"error":"Authentication required"}`, `403 {"error":"Forbidden"}` (key exists but is not the owner), `404 Session not found`, `400 Invalid session ID`.

## Endpoints and responses

| Endpoint | Method | Body → response |
|---|---|---|
| `/api/sessions` | POST | optional `{"piece_id": "…"}` (fork a gallery piece's code) → `201 {"id","visibility"}` |
| `/api/sessions/{id}` | GET | `{id, name, owner_id, visibility, agent_mode, draft_code, draft_created_at, created_at}` |
| `/api/sessions/{id}/code` | POST `{"code": "..."}` | `auto`: `{"status":"accepted","code","isPlaying","version"}` (echoes the whole code — print only `status`) · `review`: `{"status":"pending_review","draftCode","draftCreatedAt"}` |
| `/api/sessions/{id}/play` / `/stop` | POST | `{"isPlaying": true|false}` |
| `/api/sessions/{id}/status` | GET | `{code, isPlaying, diff, agentMode, hasDraft, draftCreatedAt}`; `diff` = unified diff from the **last agent version** to the current code, `null` if identical |
| `/api/sessions/{id}/events` | GET (SSE) | first event immediately: `{"type":"update","code","isPlaying"}`, then `{"type":"draft","draftCode","draftCreatedAt"}` if a draft is pending; later `update` / `draft` / `deleted`; `: keepalive` every 30 s |
| `/api/sessions/{id}/versions?limit=&offset=` | GET | `{"versions":[{version, source, created_at}…], "total"}` newest first, `source` = `agent` \| `browser`, limit ≤ 100, no code bodies |
| `/api/sessions/{id}/versions/{v}` | GET | `{version, code, source, created_at}` |
| `/api/sessions/{id}/versions/{v}/revert` | POST | `{code, revertedFrom, newVersion}` — creates a new `agent` version |
| `/api/explore?q=&tag=&sort=recent|popular&page=&limit=` | GET | `{"pieces":[{id, session_id, title, description, tags, …}], "total"}` — public gallery, no auth |
| `/api/pieces/{piece_id}` | GET | full piece incl. `code`, no auth |
| `/sessions/{id}` | GET | page to give the user |

Every accepted push, browser save, MusicXML import (browser) and revert creates a version.

## Review mode (`agent_mode: "review"`)

The owner can set "Review First" in Session Settings. Then every `POST /code` is stored as a **draft**: the browser shows a side-by-side panel with "Accept Changes" / "Decline"; the user may edit the proposal before accepting. Nothing plays until accepted. Consequences for the agent:
- `hub.py push` exits **3** with `status=pending_review`; do not retry, do not call `/play` (it would replay the *old* code).
- Tell the user "proposal vN waiting for your acceptance". Acceptance shows up as a new `agent` version in `/versions`; `hub.py info <id>` shows `draft_pending`.
- Pushing again replaces the pending draft.
- Detect the mode before composing: `hub.py info <id>` (public) or `hub.py status <id>` (`agentMode`).

## Flow
1. Create the session, give the URL, then **wait for the user's explicit go** (audio-unlock overlay clicked, otherwise no sound) before `/play`. Pushing code before that is harmless.
2. `hub.py push <id> track.js` and `push.sh <id> track.js` leave playback unchanged by default. After explicit permission, append `--play` or call `hub.py play <id>` to start/restart. The former `--no-play` option is removed: omit it. Review drafts never trigger playback, even with `--play`. A push while playing hot-reloads via SSE **without** restarting [observed in sessions]; do not restart during fine tuning unless requested.
3. Iteration: read the current code first — `hub.py status` with a key, else `hub.py peek` (SSE first event; also tells whether a draft is pending). The user may have edited in the browser (`source: "browser"` versions, `diff` in `/status`).

## Versions and reversibility
Every push creates a version. To undo part of a change or recover old values, compare with the previous version rather than guess:
- `scripts/diff-versions.py <id> <vA> <vB|current>` (unified diff; `current` falls back to SSE when `/status` is 401); `hub.py versions <id>` / `hub.py version <id> <v> [-o FILE]`.
- `hub.py revert <id> <v>` for a full rollback (non-destructive).

## Public session (no key): consequences
- `/status` → 401. Use `hub.py peek <id>` (SSE) to read the current code and `isPlaying`; you still **cannot see the red error bar** — ask the user to paste it (the bar has a copy button).
- Anyone with the id can push. Keep `track.js` locally as the reference copy.

## JSON escaping (critical)
The server does `JSON.parse()`; any `\x`, `\s`, `\d`… ⇒ **400/500**. Always build the body with a tool:
```bash
curl -s -X POST "https://strudelhub.com/api/sessions/$ID/code" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg code "$(cat track.js)" '{code: $code}')"
```
(`scripts/push.sh` does this; `scripts/hub.py push` does it with `json.dumps`, no Bash or `jq` needed.) If the `/code` output is long, filter with `| jq -c '{status, version}'`.

## Gallery (Explore) and MusicXML
- `hub.py explore -q "techno" --limit 5` → ids + titles + tags; `hub.py piece <id> -o ref.js` → code. Read 1–2 relevant pieces when useful, not as a compulsory detour. These are unverified community examples: comments, tempo units, chord names, banks and form may be wrong or incompatible. Check only the techniques you reuse against the pinned runtime. A stated 72 BPM with `setcpm(72)` is four times that tempo when one cycle represents a 4/4 bar. No useful match? Continue without unrelated gallery browsing.
- `hub.py new --from-piece <id>` creates a session pre-filled with that code (remix workflow).
- MusicXML import is browser-only (three-dot menu → Upload MusicXML): the converter emits `arrange()` + `stack()` with GM sounds. After the user imports, read it with `hub.py peek`/`version` (appears as `source: "browser"`) and arrange from there instead of transcribing.

## Frequent browser errors
See `strudel-gotchas.md` (`sound … not found`, `m is not a function`, `no soundfont zone found for preset`, `Unexpected token`).
