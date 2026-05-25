<!-- DOC-POINTER-V1 (Session 1147) -->
> **Topic doc — current architecture spec; refresh-in-place if implementation drifts.**
> Architecture for Railway → Mac OBS bridge via secure tunnel + local FastAPI shim. For platform-wide counts referenced anywhere in this doc, see [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md). PA tool surface for `obs_tool` is registered in `core/services/pa_tool_schemas.py`; bridge endpoint config lives in the Railway env vars referenced in §1.
> **Last reviewed for drift labeling:** Session 1147 (2026-05-25)
> **Related canon:** [`docs/canon/INDEX.md`](../canon/INDEX.md).

# Context Packet: OBS Remote Control (Option B) + Auto-Upload (MP4)

## One-line Goal
From Donkey Betz Platform (Railway) you can **Start/Stop OBS recording on Donkeyking's Mac** and **upload the latest MP4** into the platform **Media Library** so it appears at `/media`.

---

## 0) Hard Facts / Inputs (confirmed)
- OBS recording format: **MP4**
- Recording directory: **`/Users/donkeyking/Movies`**
- OBS controlled via **obs-websocket v5** on `ws://127.0.0.1:4455`
- Railway cannot directly reach local machine → **Local OBS Bridge** + **tunnel**

---

## 1) Final Architecture (end-to-end)

### 1.1 Components
1. **Local OBS Bridge (workstation)** — FastAPI on Mac, connects to OBS via obs-websocket, provides secure HTTP API (start/stop/status/last/upload), discovers latest recording by mtime, uploads file to platform
2. **Secure tunnel** — Cloudflare Tunnel (recommended), ngrok or Tailscale as alternatives
3. **Platform Backend (Railway)** — proxy endpoints under `/api/obs/*`, stores bridge URL + token in env vars, calls bridge with Bearer token, emits OpsRun events
4. **Cockpit Frontend** — page at `/cockpit/obs`, buttons for Start/Stop/Upload/Stop+Upload, displays status and last file/upload
5. **PA Tool** — `obs_tool` with actions, calls platform proxy endpoints (never bridge directly)

---

## 2) Security Model (non-negotiable)

### 2.1 Trust boundaries
- OBS websocket stays **local only**: `127.0.0.1:4455` (never tunneled)
- Only the **Bridge HTTP API** is exposed via tunnel
- Platform is the only intended caller of the bridge

### 2.2 AuthN/AuthZ
- Bridge requires: `Authorization: Bearer <OBS_BRIDGE_TOKEN>`
- Platform stores `OBS_BRIDGE_TOKEN` and sends it when proxying calls
- Frontend calls platform only (normal platform auth/session)

### 2.3 Secrets handling
- Tokens/passwords are **only environment variables**
- Do not store any secret in memory system

### 2.4 Optional hardening (v2)
- Cloudflare Access / IP allowlist
- Simple rate-limit in bridge (30 req/min)
- Request id header propagation (`X-Request-ID`)

---

## 3) Local OBS Bridge Spec (Workstation)

### 3.1 Language/Framework
- Python 3.11+, FastAPI + Uvicorn
- OBS Websocket v5 client: `obsws-python` or raw `websockets` with minimal v5 RPC

### 3.2 File paths
- `services/obs_bridge/`
- `services/obs_bridge/app/main.py` — FastAPI routes
- `services/obs_bridge/app/config.py` — env validation + defaults
- `services/obs_bridge/app/auth.py` — Bearer token guard
- `services/obs_bridge/app/obs_client.py` — obs-websocket connect + RPC wrappers
- `services/obs_bridge/app/recordings.py` — scan dir, newest by mtime
- `services/obs_bridge/app/uploader.py` — multipart streaming upload to platform
- `services/obs_bridge/app/schemas.py` — Pydantic request/response models
- `services/obs_bridge/requirements.txt`

### 3.3 Bridge environment variables (workstation)

**Required:**
- `OBS_BRIDGE_TOKEN` — random 32+ chars (must match platform)
- `OBS_WEBSOCKET_URL` — `ws://127.0.0.1:4455`
- `OBS_WEBSOCKET_PASSWORD` — OBS websocket password
- `OBS_RECORDINGS_DIR` — `/Users/donkeyking/Movies`
- `PLATFORM_BASE_URL` — `https://<railway-domain>`
- `PLATFORM_UPLOAD_URL` — `https://<railway-domain>/api/media/upload`
- `PLATFORM_UPLOAD_TOKEN` — scoped platform token for upload endpoint

**Optional:**
- `BRIDGE_HOST` — `127.0.0.1`
- `BRIDGE_PORT` — `8787`
- `SETTLE_DELAY_SECONDS` — `2`
- `ALLOWED_EXTENSIONS` — `.mp4`

### 3.4 Bridge API — Exact Endpoints

#### Common
- Header required: `Authorization: Bearer <OBS_BRIDGE_TOKEN>`
- Response header: `X-Bridge-Version: 1`

#### Error response schema (all endpoints)
```json
{
  "ok": false,
  "error": {
    "code": "STRING_ENUM",
    "message": "human readable",
    "detail": "optional long detail"
  }
}
```

**Error codes:** `UNAUTHORIZED`, `OBS_NOT_RUNNING`, `OBS_AUTH_FAILED`, `OBS_CONNECTION_FAILED`, `OBS_CALL_FAILED`, `RECORDINGS_DIR_NOT_FOUND`, `NO_RECORDINGS_FOUND`, `UPLOAD_FAILED`, `PLATFORM_AUTH_FAILED`, `INTERNAL_ERROR`

---

#### 3.4.1 `POST /v1/recording/start`
Starts OBS recording.

- Request body: empty `{}`
- Success response:
```json
{
  "ok": true,
  "isRecording": true,
  "startedAt": "2026-03-02T20:10:00Z"
}
```
- If already recording: return `ok:true` with `isRecording:true` (idempotent)

---

#### 3.4.2 `POST /v1/recording/stop`
Stops OBS recording.

- Request body: empty
- Success response:
```json
{
  "ok": true,
  "isRecording": false,
  "stoppedAt": "2026-03-02T20:12:34Z",
  "settleDelaySeconds": 2
}
```
- After stop, bridge waits `SETTLE_DELAY_SECONDS` before scanning files

---

#### 3.4.3 `GET /v1/recording/status`
Returns whether OBS is currently recording.

- Success response:
```json
{
  "ok": true,
  "isRecording": false,
  "recordingTimecode": "00:00:00",
  "obsVersion": "30.x.x",
  "websocketVersion": "5.x.x"
}
```
- If OBS not reachable: `{ "ok": false, "error": { "code": "OBS_NOT_RUNNING", "message": "..." } }`

---

#### 3.4.4 `GET /v1/recording/last`
Finds newest recording file by **mtime** in `OBS_RECORDINGS_DIR`.

**Selection rules:**
- Directory: `OBS_RECORDINGS_DIR` (default `/Users/donkeyking/Movies`)
- Allowed extensions: `.mp4`
- Choose newest by `os.path.getmtime(path)`
- Ignore non-files
- If none found → `NO_RECORDINGS_FOUND`

- Success response:
```json
{
  "ok": true,
  "recordingsDir": "/Users/donkeyking/Movies",
  "allowedExtensions": [".mp4"],
  "file": {
    "path": "/Users/donkeyking/Movies/2026-03-01 19-41-41.mp4",
    "filename": "2026-03-01 19-41-41.mp4",
    "ext": ".mp4",
    "sizeBytes": 123456789,
    "mtime": "2026-03-01T19:41:55Z"
  }
}
```

---

#### 3.4.5 `POST /v1/recording/upload_last`
Uploads newest MP4 into the platform media library.

- Request body (optional):
```json
{
  "title": "OBS Recording (optional override)",
  "tags": ["obs", "recording"],
  "stopIfRecording": false
}
```

**Behavior:**
1. If `stopIfRecording=true` and `status.isRecording=true`: call OBS stop, wait `SETTLE_DELAY_SECONDS`
2. Determine latest file via `/v1/recording/last` logic
3. Upload via `PLATFORM_UPLOAD_URL` using `multipart/form-data` streaming
4. Return platform `media_id`

- Success response:
```json
{
  "ok": true,
  "uploaded": true,
  "media": {
    "id": "3c9c3b4f-2f37-4f7a-9d8b-8ef5c59c8caa",
    "type": "video",
    "contentType": "uploaded",
    "title": "OBS Recording 2026-03-01 19-41-41",
    "filename": "2026-03-01 19-41-41.mp4",
    "sizeBytes": 123456789
  }
}
```

---

## 4) Platform Proxy API (Railway)

### Platform env vars (Railway)

**Required:**
- `OBS_ENABLED=true`
- `OBS_BRIDGE_URL=https://<tunnel-domain>` (no trailing slash)
- `OBS_BRIDGE_TOKEN=<random-32+>`

**Optional:**
- `OBS_PROXY_TIMEOUT_SECONDS=10`

### Endpoints
All require standard platform auth (session/JWT).

| Endpoint | Bridge Call | Notes |
|---|---|---|
| `POST /api/obs/start` | `POST {OBS_BRIDGE_URL}/v1/recording/start` | |
| `POST /api/obs/stop` | `POST {OBS_BRIDGE_URL}/v1/recording/stop` | |
| `GET /api/obs/status` | `GET {OBS_BRIDGE_URL}/v1/recording/status` | Add `bridgeReachable`, `lastBridgeContactAt` |
| `GET /api/obs/last` | `GET {OBS_BRIDGE_URL}/v1/recording/last` | |
| `POST /api/obs/upload_last` | `POST {OBS_BRIDGE_URL}/v1/recording/upload_last` | Pass body through |
| `POST /api/obs/stop_and_upload` | `POST {OBS_BRIDGE_URL}/v1/recording/upload_last` with `stopIfRecording:true` | Convenience endpoint |

### Platform proxy client file
- `core/services/obs_bridge_client.py`
  - Methods: `start()`, `stop()`, `status()`, `last()`, `upload_last(payload)`
  - Uses `httpx`/`requests` to call `${OBS_BRIDGE_URL}/v1/...` with Bearer token

### Platform API routes file
- `core/api/obs.py` (or add to existing views)

---

## 5) Database Models (Platform) — Optional

### 5.1 Recommended: `OBSEvent` model
- `id`: UUID pk
- `created_at`: DateTime auto_now_add
- `action`: Text choices (`START_RECORDING`, `STOP_RECORDING`, `STATUS`, `LAST_RECORDING`, `UPLOAD_LAST`, `STOP_AND_UPLOAD`)
- `ok`: Boolean
- `bridge_url`: Text
- `request_id`: Text null=True
- `response_json`: JSONField null=True
- `error_code`: Text null=True
- `error_message`: Text null=True
- `media_id`: UUID null=True
- `filename`: Text null=True
- `size_bytes`: BigInteger null=True

Indexes: `created_at` desc, `(action, created_at)` optional

### 5.2 No model option (allowed for v1)
- Skip DB model entirely
- Log everything via structured logs + OpsRun events
- Cockpit reads live state from `/api/obs/status`

---

## 6) PA Tool Schema — `obs_tool`

### Tool schema
```python
{
    "type": "function",
    "name": "obs_tool",
    "description": (
        "Control OBS Studio recording remotely: start/stop recording, check status, "
        "find latest recording, upload last recording to media library. "
        "Use when user asks to record, stop recording, check OBS, or upload a recording."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "start_recording", "stop_recording", "status",
                    "last_recording", "upload_last_recording", "stop_and_upload",
                ],
            },
            "title": {
                "type": "string",
                "description": "Optional title for uploaded media",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags for uploaded media",
            },
            "stopIfRecording": {
                "type": "boolean",
                "description": "Stop recording before uploading (default true for upload actions)",
            },
        },
        "required": ["action"],
    },
}
```

### Action → API mapping
- `start_recording` → `POST /api/obs/start`
- `stop_recording` → `POST /api/obs/stop`
- `status` → `GET /api/obs/status`
- `last_recording` → `GET /api/obs/last`
- `upload_last_recording` → `POST /api/obs/upload_last` with `{ stopIfRecording: true, title?, tags? }`
- `stop_and_upload` → `POST /api/obs/upload_last` with `{ stopIfRecording: true }`

---

## 7) Cockpit Frontend — `/cockpit/obs`

### Route
- `/cockpit/obs`

### Data sources
- `GET /api/obs/status` (poll every 5s, every 2s while recording)
- `GET /api/obs/last` (on demand / after stop)
- `POST /api/obs/start`
- `POST /api/obs/stop`
- `POST /api/obs/upload_last`

### UI Components
1. **Header** — "OBS Control" + status pill (Connected/Stale/Disconnected)
2. **Primary controls** — Start Recording, Stop Recording, Upload Last, Stop + Upload buttons
3. **Status panel** — isRecording, recordingTimecode, lastBridgeContactAt
4. **Last recording panel** — filename, size (human readable), modified time
5. **Last upload panel** — Media ID, link to `/media`
6. **Logs panel** (optional) — last 20 actions from OBSEvent if implemented

### UX Behavior

**Start Recording:**
- Disabled when `isRecording=true` or loading
- On success: set `isRecording=true`, poll every 2s
- On failure: re-enable, show error banner

**Stop Recording:**
- Disabled when `isRecording=false` or loading
- On success: set `isRecording=false`, show "Finalizing file…" for 2s, then auto-call `GET /api/obs/last`
- On failure: re-enable, show error banner

**Upload Last Recording:**
- Calls `POST /api/obs/upload_last` with `{ stopIfRecording: false }`
- On success: display `media.id` + "View in Media Library" link → `/media`

**Stop + Upload:**
- Calls `POST /api/obs/upload_last` with `{ stopIfRecording: true }`
- UI progress phases: "Stopping…" → "Waiting for file flush… (2s)" → "Uploading MP4…"
- On success: display `media.id` + `/media` link

**Connection state:**
- Connected if `bridgeReachable=true`
- Stale if last contact > 60s
- Disconnected if last call failed

**Error display:**
- Standard banner with `error.code`, `error.message`, collapsible "Details" for `error.detail`
- Contextual guidance: OBS_NOT_RUNNING → "Open OBS and enable obs-websocket", NO_RECORDINGS_FOUND → "No MP4 in /Users/donkeyking/Movies"

### State model
```typescript
interface OBSState {
  status: { isRecording: boolean; recordingTimecode: string; bridgeReachable: boolean; lastBridgeContactAt: string } | null;
  lastFile: { filename: string; sizeBytes: number; mtime: string } | null;
  lastUpload: { mediaId: string; title: string } | null;
  loading: { start: boolean; stop: boolean; upload: boolean; stopUpload: boolean };
  error: { code: string; message: string; detail?: string } | null;
}
```

### API client file
- `frontend/src/lib/api/obs.ts` (or similar)

---

## 8) Implementation Steps — Exact Order

### Phase A — Local OBS Bridge (workstation)
1. Create `services/obs_bridge/` folder structure
2. Add all files: `main.py`, `config.py`, `auth.py`, `obs_client.py`, `recordings.py`, `uploader.py`, `schemas.py`
3. Add `requirements.txt`
4. Implement all 5 endpoints
5. Local verification: start OBS, run uvicorn, curl each endpoint

### Phase B — Tunnel (Cloudflare)
6. Create Cloudflare Tunnel config → `http://127.0.0.1:8787`
7. Verify remote access with Bearer token

### Phase C — Platform Proxy API (Railway backend)
8. Set Railway env vars: `OBS_ENABLED`, `OBS_BRIDGE_URL`, `OBS_BRIDGE_TOKEN`
9. Create `core/services/obs_bridge_client.py` — proxy client
10. Create `core/api/obs.py` — proxy endpoints
11. (Optional) Create `OBSEvent` model + migration
12. Ensure media upload endpoint exists and accepts large MP4s

### Phase D — PA Tool (`obs_tool`)
13. Add tool schema to `core/services/pa_tool_schemas.py`
14. Add handler to `core/services/tool_dispatcher.py`
15. Register in `_register_default_handlers()`
16. Add to `TOOL_ENRICHMENT_MAP` and `TOOL_TO_INTENT_MAP`
17. Smoke test via PA chat

### Phase E — Cockpit Frontend (`/cockpit/obs`)
18. Add page component (React)
19. Add API client wrapper
20. Implement state model + polling
21. Implement all buttons + status displays
22. Add nav item: Cockpit → OBS

---

## 9) Verification Checklist

### A) Local Bridge (no tunnel)
- [ ] OBS installed, running, obs-websocket v5 enabled, recording format MP4
- [ ] Calling without Authorization → `UNAUTHORIZED`
- [ ] Calling with wrong token → `UNAUTHORIZED`
- [ ] `GET /v1/recording/status` returns `ok:true`, includes `isRecording`
- [ ] OBS closed → returns `OBS_NOT_RUNNING`
- [ ] `POST /v1/recording/start` → `ok:true`, OBS shows active recording
- [ ] Start twice → idempotent, no crash
- [ ] `POST /v1/recording/stop` → `ok:true`, recording stops
- [ ] Stop when not recording → idempotent
- [ ] After stop, bridge waits `SETTLE_DELAY_SECONDS` before scanning
- [ ] `OBS_RECORDINGS_DIR` doesn't exist → `RECORDINGS_DIR_NOT_FOUND`
- [ ] No `.mp4` in dir → `NO_RECORDINGS_FOUND`
- [ ] `GET /v1/recording/last` returns newest `.mp4` by mtime
- [ ] Returned metadata correct: `filename`, `sizeBytes > 0`, valid ISO `mtime`
- [ ] `POST /v1/recording/upload_last` → `ok:true`, returns `media.id`
- [ ] Upload streams file (no full read into memory)
- [ ] Bad platform token → `PLATFORM_AUTH_FAILED`

### B) Tunnel
- [ ] From external network: `GET /v1/recording/status` with token → success
- [ ] Missing/wrong token → `UNAUTHORIZED`
- [ ] OBS websocket port (4455) not accessible externally
- [ ] Tunnel stable for 10+ min under repeated calls

### C) Platform Proxy (Railway)
- [ ] `OBS_ENABLED=true`, `OBS_BRIDGE_URL` correct, `OBS_BRIDGE_TOKEN` matches
- [ ] All proxy endpoints work: start, stop, status, last, upload_last
- [ ] `GET /api/obs/status` includes `bridgeReachable`, `lastBridgeContactAt`
- [ ] Bridge down → `ok:false` with clear error, no hang (respects timeout)
- [ ] Responses/logs never include tokens or passwords

### D) Media Library
- [ ] After upload, video appears in `/media`
- [ ] Correct type/title/size/timestamp
- [ ] Video plays in browser, no CORS errors
- [ ] 413 Payload Too Large → clear error (raise limits if needed)

### E) Cockpit UI (`/cockpit/obs`)
- [ ] Page renders, immediately calls status
- [ ] Connection pill shows correct state
- [ ] Start → disabled while recording, recording indicator + 2s polling
- [ ] Stop → "Finalizing…" 2s delay → auto-shows last file
- [ ] Upload Last → returns media.id + media library link
- [ ] Stop + Upload → progress phases → media.id + link
- [ ] Error banners with contextual guidance
- [ ] No secret leakage in network tab

### F) PA Tool (`obs_tool`)
- [ ] "start OBS recording" → calls start, returns ok
- [ ] "OBS status" → returns isRecording + bridgeReachable
- [ ] "stop recording" → calls stop, returns ok
- [ ] "upload last OBS recording" → returns media.id
- [ ] "stop and upload" → returns media.id
- [ ] Bridge unreachable → `ok:false` with readable error
- [ ] Tool output never includes secrets

---

## Gotchas (read before coding)
- **Most common blocker:** platform upload size limits (413). Plan to raise limits or use signed direct-to-storage upload.
- **Spaces in filenames** (e.g., `2026-03-01 19-41-41.mp4`) must be handled safely — always pass as file bytes, not shell commands.
- **Settle delay matters:** without 1–2s delay after stop, you can upload a partially-written MP4.
- Keep OBS websocket **local-only**; only the bridge is tunneled and token-protected.
