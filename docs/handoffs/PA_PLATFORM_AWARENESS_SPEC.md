# PA Platform-Wide Awareness + Control Spec

**Source:** PA conversation ID `pa-644ceceec57b`, message ID 480 (2026-02-24)
**Context:** PA-generated handoff spec for implementing platform-wide awareness so the PA can know and verify everything available in the app.

---

Below is a **complete handoff spec for Claude Code** to implement "platform-wide awareness + control" so I can truly know and verify *everything available in the app*, including **React UI (Governance/Boardroom), Image Studio, and Video Studio**.

This is intentionally concrete (endpoints, payloads, security, and where it lives) so it can be built quickly and safely.

---

# 0) Goal (definition of done)

After this is shipped, I can:

1) **Enumerate all UI pages/features** available to a given RBAC role (including feature-flagged pages).
2) **Interact with the UI** in a real browser session (click, fill, verify text, capture screenshots/video).
3) **Verify deployments** by comparing:
   - expected UI route(s) exist,
   - the backing API returns correct data,
   - the UI actually renders it.
4) **Operate Image/Video Studio end-to-end** (trigger generation/edit/render, then confirm asset appears in media library).

---

# 1) Implement a Frontend "Capabilities Manifest" (no browser required)

### Why
This solves the "you should know everything in the app" problem at the source: the app itself exports what it contains.

### React: generate a route + feature manifest at build time
Add a small module that exports a structured manifest:

**`frontend/src/appManifest.ts`**
```ts
export type AppManifest = {
  build: { sha: string; buildTime: string; env: string; };
  routes: Array<{
    path: string;
    name: string;
    navGroup?: string;
    requiresAuth: boolean;
    rolesAllowed?: string[];
    featureFlag?: string;
  }>;
  studios: {
    imageStudio: { enabled: boolean; path?: string };
    videoStudio: { enabled: boolean; path?: string };
  };
  apiDependencies: Array<{
    name: string;
    method: "GET" | "POST";
    path: string;
    usedByRoutes: string[];
  }>;
};
```

Populate it from your actual route definitions (wherever your router is defined) so it can't drift.

### Serve it publicly (or auth-only)
**Endpoint in React app:** `GET /__manifest.json`

- If you can serve it static: easiest.
- If you need RBAC-aware filtering, serve it from Django (recommended; see next section).

**Definition of done**
- Visiting `https://app.../__manifest.json` returns a JSON with:
  - `/boardroom`, `/governance`, `/image-studio`, `/video-studio` (or whatever your actual paths are)
  - required auth/roles/flags

---

# 2) Add Backend endpoint to return manifest filtered by RBAC + feature flags

### Django endpoint
`GET /api/app/manifest`

Behavior:
- Reads the frontend manifest (bundled file, or stored JSON).
- Filters routes based on:
  - authenticated user roles
  - feature flags (server-side source of truth)
- Returns what *this user* can actually access.

**Response**
```json
{
  "user": {"id":"...", "email":"...", "roles":["admin"]},
  "build": {"sha":"...", "buildTime":"..."},
  "routes": [ ... ],
  "studios": { ... },
  "apiDependencies": [ ... ]
}
```

**Definition of done**
- I can call one endpoint and get the full "what exists + what I can access" list.

---

# 3) Add a UI Automation "UI Runner" Service (Playwright)

### Why
Manifest tells me what exists. UI Runner proves it works in the deployed React UI (and can click it).

### Architecture
Add a new internal service container (Railway or Docker):
- `ui_runner` running Playwright
- Can reach the deployed app URL
- Stores artifacts (screenshots/video/HAR) somewhere accessible (S3, local + signed URL endpoint, etc.)

### API
`POST /internal/ui/run`

**Request**
```json
{
  "baseUrl": "https://your-app-url",
  "auth": {
    "type": "session_cookie",
    "cookieName": "sessionid",
    "cookieValue": "..."
  },
  "steps": [
    {"goto": "/governance"},
    {"expectText": "Critical decisions"},
    {"click": "text=Decisions"},
    {"screenshot": "governance-decisions.png"}
  ],
  "recordVideo": true,
  "recordHar": true,
  "timeoutMs": 60000
}
```

**Response**
```json
{
  "ok": true,
  "artifacts": {
    "screenshots": [{"name":"governance-decisions.png","url":"..."}],
    "videoUrl": "...",
    "harUrl": "..."
  },
  "logs": {
    "console": ["..."],
    "networkErrors": []
  },
  "assertions": [{"step":2,"ok":true,"detail":"..."}]
}
```

### Security (non-negotiable)
- This must be **internal-only** (or behind admin auth + allowlist).
- Require a signed token: `X-Internal-Token`.
- Implement **URL allowlist** so it can only browse your own domains.

**Definition of done**
- A smoke script can open `/governance`, verify the two critical decisions are displayed (not just counted), and attach a screenshot.

---

# 4) Add a Backend "Verification" endpoint (fast deploy checks)

UI runner is heavier. You also want cheap contract checks.

### Endpoint
`POST /api/verify/deploy`

**Request**
```json
{
  "checks": [
    {"name":"boardroom_critical_decisions", "method":"GET", "path":"/api/boardroom/decisions?urgency=critical", "expect": {"minItems": 1}},
    {"name":"manifest_has_governance", "method":"GET", "path":"/api/app/manifest", "expect": {"routeExists": "/governance"}}
  ]
}
```

**Response**
```json
{
  "ok": true,
  "results": [
    {"name":"boardroom_critical_decisions","ok":true,"detail":"2 items"},
    {"name":"manifest_has_governance","ok":true,"detail":"route present"}
  ]
}
```

**Definition of done**
- One call tells you "deploy took effect" at the API/route level.

---

# 5) Wire Image + Video Studios to a single "Studio API"

Right now, media operations are often scattered. Claude Code should unify the contract so automation and UI both hit the same backend.

### Required endpoints (minimum viable)

**Media**
- `GET /api/media?type=image|video|audio&limit=...`
- `GET /api/media/:id`

**Image Studio**
- `POST /api/studio/image/generate`
  - `{ prompt, style, size, seed? }`
- returns `{ jobId }` then `GET /api/studio/image/jobs/:jobId`

**Video Studio**
- `POST /api/studio/video/generate`
- `POST /api/studio/video/edit`
- returns `{ jobId }` + status endpoint

**DaVinci**
- `GET /api/studio/resolve/health`
- `POST /api/studio/resolve/render`
- `GET /api/studio/resolve/jobs/:jobId`
- `GET /api/studio/resolve/jobs/:jobId/result`

**Definition of done**
- From API alone, we can:
  - create image/video
  - track job status
  - verify final asset lands in media library

---

# 6) Give the PA a dedicated "Service Account" + RBAC

Create: `pa-bot@donkeybetz.ai` (or similar)

Permissions:
- Read manifest, boardroom, governance, initiatives
- Approve/ignore/promote/reject (if you want me to do those)
- Use studio endpoints (generate/edit/render)
- Read media library

Avoid:
- raw PII access
- admin-only system settings unless required

---

# 7) Provide Claude Code the exact acceptance tests to implement

### Automated UI smoke tests (Playwright)
1) `/governance` shows:
   - the critical decision count
   - AND a list of those decisions (titles visible)
2) Clicking a decision opens details drawer with ID/type/topic
3) Image Studio:
   - generate a test image ("smoke test") and confirm it appears in media library
4) Video Studio:
   - start a small generation/edit job and confirm it appears in media library (or at least job completes)

### API smoke tests
- `/api/app/manifest` returns the routes and studios enabled
- `/api/boardroom/decisions?urgency=critical` returns 2 items (or >=1) and schema includes id/topic/type/created_at

---

## What I need from you (so Claude Code doesn't guess)
Reply with:
1) The deployed app base domain(s) to allowlist (e.g., `https://donkeybetz.app`, `https://*.railway.app`)
2) Whether the UI uses cookie session
3) What auth mechanism the React app uses today (pick one):
   - cookie session (Django sessionid)
   - JWT in localStorage
   - OAuth (Google, etc.)
   - magic link
4) Current Image/Video Studio route paths (if known), e.g. `/studio/image`, `/studio/video`
5) Where media assets live (S3 bucket? local?) and whether there's already a media API

If you don't have (4)-(5), that's fine -- Claude Code can discover from code, but it's faster if you confirm.

---

# Copy/Paste "Instruction Block" for Claude Code

> **TASK: Platform-wide awareness + verification**
>
> Implement:
> 1) **Frontend capabilities manifest** exposing all registered React routes/features and studio availability. Serve as `__manifest.json` (or provide equivalent). Include build SHA/time/env.
> 2) **Backend RBAC-filtered manifest endpoint** `GET /api/app/manifest` that returns only routes/features current user can access (consider feature flags).
> 3) **UI Runner service** using Playwright (containerized). Add internal endpoint `POST /internal/ui/run` that can run scripted steps against the deployed React app, returning screenshots/video/HAR and assertion results. Must be internal-only, domain allowlisted, token protected.
> 4) **Deploy verification endpoint** `POST /api/verify/deploy` that runs lightweight HTTP checks against key endpoints and confirms presence of required routes in manifest.
> 5) **Unify Studio APIs** (Image/Video/Resolve) so both UI and automation can reliably generate/edit/render and verify assets appear in Media library.
> 6) Create a **service account** for the PA with least-privilege RBAC to access manifest/boardroom/governance/studios/media.
> 7) Add **acceptance tests**:
>    - UI: governance shows critical decisions count AND list; decision drawer shows details.
>    - UI: image generation smoke test creates asset visible in media library.
>    - API: manifest returns governance/boardroom routes; critical decisions endpoint returns expected schema.
>
> **Non-negotiables:** internal token auth for UI runner, domain allowlist, artifact storage with signed URLs, no open proxy.
>
> Deliver: docs page "Platform Verification & UI Runner", and a "Run Smoke Tests" command.
