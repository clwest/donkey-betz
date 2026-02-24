# PA Layer #1 — Surface Map (Live UI Manifest)

**Source:** PA conversation `pa-a17ca48c5b32` (February 24, 2026)
**Tool used:** `platform_awareness_tool.get_manifest`
**Context:** Part of the PA's 6-layer Systems Map series. This layer was completed using the live manifest endpoint deployed in Session 1071.

---

## Layer #1 — Surface Map (Completed using the live UI manifest)

Source: `platform_awareness_tool.get_manifest` (env: **production**, build: **2026-02-24T04:36:45Z**, **30 routes**, user_role: **admin**)

---

# 1A) UI Surface Inventory (Canonical)

**Legend**
- **Section** = manifest `category` (this is your "side panel group" proxy until nav groups are explicitly modeled)
- **Flag** = capability/feature flag if provided (manifest doesn't currently attach per-route flags)
- **Roles** = roles required (only `/admin` declares this explicitly; others inherit "authRequired")
- **Primary API calls** = mapped to the *tool-backed* APIs we know exist; for studios we have explicit endpoints from the manifest; for others, the manifest doesn't list per-route endpoints yet (see "Completion note" at end)
- **Primary actions** = typical user mutations the page implies (approve, create, update, run, render, etc.)

### Auth
| Route | Nav label | Section | Flag | Roles | Primary API calls | Primary actions |
|---|---|---|---|---|---|---|
| `/login` | Login | auth | — | public | Auth endpoints (not listed in manifest) | Sign in / establish session |

### Command (your operational control surfaces)
| Route | Nav label | Section | Flag | Roles | Primary API calls | Primary actions |
|---|---|---|---|---|---|---|
| `/` | Command Center | command | `pa_chat`, `websocket` | auth | Chat/command APIs (tool-backed), websocket | Run commands, trigger agents, route tasks |
| `/dashboard` | Dashboard | command | — | auth | Aggregation endpoints (not enumerated) | View system summary / KPIs |
| `/workspace` | Workspace | command | — | auth | Workspace APIs (tool-backed) | List workspaces, view status |
| `/boardroom` | Boardroom | command | — | auth | Boardroom APIs (tool-backed) | View attention items; approve/ignore; view decisions; promote/reject decisions |
| `/governance` | Governance | command | — | auth | Boardroom + gates + human decisions (tool-backed) | Classify, approve/reject, gate management actions |
| `/platform` | Platform | command | — | auth | System health, status snapshot, errors, schedules (tool-backed) | Inspect platform status; troubleshooting |
| `/billing` | Billing | command | — | auth | Cost telemetry / resource budgets (tool-backed) | View spend, limits, cost breakdown |
| `/analytics` | Analytics | command | — | auth | ML analysis + performance metrics (tool-backed) | Model performance, accuracy, trends |

### Studio (explicit, fully enumerated by manifest)
| Route | Nav label | Section | StudioType | Roles | Primary API calls (manifest) | Primary actions |
|---|---|---|---|---|---|---|
| `/image-studio` | Image Studio | studio | image | auth | `GET/POST /api/v1/gallery/` | Generate images; browse gallery; manage image assets |
| `/video-studio` | Video Studio | studio | video | auth | `GET/POST /api/v1/video/` | Generate videos; edit videos; browse jobs/results |

**Studio capability addendum (manifest "studios" block)**
- **Audio (enabled, no UI path yet)**: endpoint `/api/v1/audio/`, models: `elevenlabs-tts`

### Intelligence (meta-system and orchestration views)
| Route | Nav label | Section | Flag | Roles | Primary API calls | Primary actions |
|---|---|---|---|---|---|---|
| `/intelligence` | Intelligence | intelligence | `spider_network` | auth | Intelligence APIs (tool-backed) | View intelligence hubs (stocks, betting, gov, etc.) |
| `/agents` | Agents | intelligence | — | auth | Agent registry/introspection (tool-backed) | List agents, view capabilities, check availability |
| `/advisors` | Advisors | intelligence | — | auth | Advisor registry (not in tools; likely DB-backed) | Browse advisors |
| `/neural-orchestra` | Neural Orchestra | intelligence | — | auth | Orchestration/pipeline APIs (tool-backed) | View orchestration state, runs, routing |
| `/conversation-contract` | Conversation Contract | intelligence | — | auth | Contract/config endpoints (not enumerated) | View/update conversation rules/settings |
| `/mythology-lab` | Mythology Lab | intelligence | — | auth | Mythology module APIs (not enumerated) | Run mythology workflows/content |

### Domain apps (vertical features)
| Route | Nav label | Section | Flag | Roles | Primary API calls | Primary actions |
|---|---|---|---|---|---|---|
| `/content` | Content | domain | `deliberation_pipeline` | auth | Content review + deliverables (tool-backed) | Create/review/approve/reject content |
| `/betting` | Betting | domain | — | auth | Sports betting intelligence (tool-backed) | View predictions/arbs/odds; track wagers |
| `/stocks` | Stock Intelligence | domain | — | auth | Stock intelligence (tool-backed) | View briefs/alerts/predictions/SEC |
| `/portfolio` | Portfolio | domain | — | auth | Revenue tracker (tool-backed) | View revenue stats, records |
| `/legal` | Legal | domain | — | auth | Legal doc drafter (tool-backed) | Generate legal documents, manage drafts |
| `/government` | Government | domain | — | auth | Legislation tool/RAG (tool-backed) | Search/summary/ask about bills |
| `/documents` | Documents | domain | — | auth | Deliverables library (tool-backed) | Create/update/search documents |
| `/blog/:blogId` | Blog Viewer | domain | — | auth | Content/blog detail APIs (tool-backed) | View blog, approve/publish (if authorized) |

### Reference
| Route | Nav label | Section | Roles | Primary API calls | Primary actions |
|---|---|---|---|---|---|
| `/docs-index` | Docs Index | reference | auth | Docs endpoints (not enumerated) | Browse docs |
| `/how-it-works` | How It Works | reference | auth | Static/Docs | Read |

### Admin
| Route | Nav label | Section | Roles | Primary API calls | Primary actions |
|---|---|---|---|---|---|
| `/admin` | Admin | admin | `admin` | Admin APIs (Django admin + internal endpoints) | Administer platform objects |
| `/settings` | Settings | admin | auth | Settings APIs (not enumerated) | Update settings |
| `/profile` | Profile | admin | auth | Profile APIs (not enumerated) | Update profile |

---

# 1B) API Surface Inventory (What exists + how it's used)

Two kinds of "API surface" exist in your platform:

1) **UI-facing HTTP endpoints** (example: `/api/v1/gallery/`), and
2) **Tool-backed internal APIs** (what the PA can call via platform tools; they correspond to backend endpoints/models but aren't exposed with explicit method/path).

### 1B-1) Explicit UI-facing endpoints from manifest (canonical)
| Method + Path | Object type | Read/Write | Typical payload/latency | Called by (UI) | Called by (agents/tools) |
|---|---|---|---|---|---|
| `GET/POST /api/v1/gallery/` | Image gallery assets / image jobs | RW | Medium (assets metadata), latency depends on gen | `/image-studio` | `studio_tool.generate_image`, `media_tool` (library) |
| `GET/POST /api/v1/video/` | Video jobs / video assets | RW | Large (job status), high latency for renders | `/video-studio` | `studio_tool.generate_video`, `davinci_tool`, `media_tool` |
| `GET/POST /api/v1/audio/` | Audio jobs/assets (TTS) | RW | Medium, latency model-dependent | (no UI route yet) | `studio_tool.generate_audio` |

### 1B-2) Tool-backed API catalog (canonical "operator" surface)
These are the APIs you effectively have today (via tools). Since the manifest doesn't list their HTTP paths, they are listed by **capability + object type + read/write + "called by"**.

| Tool (API surface) | Object type(s) | Read/Write | Called by (pages) | Called by (agents) |
|---|---|---|---|---|
| **boardroom_tool** | attention items, decisions | RW | `/boardroom`, `/governance` | Coordinator/triage agents |
| **human_decisions_tool** | human-in-the-loop decision items | RW | `/governance` | Various pipelines requiring manual approval |
| **initiative_tool** | initiatives, stage docs, action items | RW | `/workspace`, initiative views | Initiative pipeline agents |
| **pipeline_orchestrator_tool** | pipeline runs, stage status, counts | R | `/dashboard`, `/platform`, `/neural-orchestra` | Orchestrator / scheduler |
| **agent_registry_tool** | agents, routability, status, routing rules | R/W (admin) | `/agents`, `/intelligence` | Router, introspection agents |
| **advisor_registry_tool** *(if present)* | advisors, assignments | R/W | `/advisors` | Advisor routing layer |
| **spider_tool / spider_network_tool** | spiders, feeds, scrape jobs, items | RW | `/intelligence` (and likely domain pages) | Spider controllers, ingestion agents |
| **intelligence_tool** | signals/insights/artifacts (domain) | R/W | `/intelligence`, `/stocks`, `/betting`, `/government` | Analyst agents (stocks/betting/gov) |
| **documents_tool** | docs, deliverables, attachments | RW | `/documents`, `/docs-index` | Writer agents, summarizers |
| **content_tool** | blogs, review queue items, publish state | RW | `/content`, `/blog/:blogId` | ContentStrategyAgent, BlogEnhancer |
| **media_tool (media library)** | media assets (images/videos/audio), metadata, URLs | RW | `/image-studio`, `/video-studio`, `/documents` | Studio agents, pipeline publishers |
| **davinci_tool / resolve_node_tool** | render jobs, node health, outputs | RW | `/video-studio`, `/platform` | Video pipeline agents |
| **revenue_tool** | revenue records, snapshots | RW | `/portfolio`, `/billing` | Finance/revenue agents |
| **billing_tool** | usage/cost/budgets | RW (admin) | `/billing` | Cost governor agents |
| **analytics_tool** | KPI series, evaluations, model metrics | R | `/analytics` | Evaluation agents |
| **settings_tool** | user/org settings | RW | `/settings`, `/profile`, `/conversation-contract` | Configuration agents |
| **auth_tool** | sessions, tokens (internal) | RW | `/login` | (rare; mostly UI) |
| **logs_tool** | job logs, tool call logs, errors | R | `/platform`, `/analytics` | Debug agents / triage |

### Read/Write semantics (operator cheat sheet)
- **Read-only surfaces** are usually: pipeline status, analytics, logs, agent registry listing.
- **Write/mutation surfaces** include: boardroom decisions, governance classification, initiatives, content publishing, studio generation, render jobs, settings/billing actions.

---

## 1B-3) Endpoint-level inventory — what's still missing & how to finish it

Right now the manifest gives **explicit REST endpoints only for Studios**:

- `/api/v1/gallery/`
- `/api/v1/video/`
- `/api/v1/audio/`

But for the rest (Boardroom, Governance, Initiatives, Content, Documents, Spiders), the manifest **does not yet expose**:
- method + path per endpoint
- typical payload sizes/latency
- "called by route" mappings

### To make Layer #1 truly complete (and keep it automatically updated)
Add **one more manifest section**:

#### `apiDependencies[]` (per-route)
For each route, list the endpoints it calls (or tool-surface names if you don't want to expose raw paths):

Example shape:
```json
{
  "path": "/boardroom",
  "apiDependencies": [
    { "name": "boardroom.attention.list", "method": "GET", "path": "/api/v1/boardroom/attention", "writes": false },
    { "name": "boardroom.item.approve", "method": "POST", "path": "/api/v1/boardroom/attention/{id}/approve", "writes": true }
  ]
}
```

And/or: if you want to avoid exposing private paths in the frontend, use a stable "logical API name":
```json
{ "name": "boardroom.attention.list", "toolSurface": "boardroom_tool.list_attention", "writes": false }
```

Once that exists, the PA can output the **fully enumerated** "Method + Path / payload / latency / called-by" API table with no guesswork.

---

# Summary of Layer #1 completion status

## Completed now
- **UI Surface Inventory** for all **30 routes**, including:
  - route path
  - label
  - section/category
  - auth required
  - explicit admin role requirement (`/admin`)
  - studios' exact endpoints/models

## Partially complete (needs one more manifest expansion)
- **API Surface Inventory** at "endpoint granularity" for non-studio modules.
  - Tool-backed surfaces are listed (canonical operational API), but not the exact HTTP paths/payload metrics until the manifest includes `apiDependencies`.

---

## PA's Recommended Enhancement: `apiDependencies` in Manifest

The PA identified that the current manifest covers **routes + studios + capabilities** but lacks per-route API dependency mapping. Adding `apiDependencies[]` to each route in `appManifest.ts` would allow the PA to:

1. Produce a fully enumerated endpoint-level inventory automatically
2. Detect when a page's API dependencies change (new endpoints, removed endpoints)
3. Run targeted deploy verification per-page (not just global health checks)
4. Map agent tool usage back to specific UI surfaces
