# PA 6-Layer Systems Map

**Source:** PA conversation `pa-a17ca48c5b32` (2026-02-24)
**Context:** PA-generated operator/manual-grade systems map. The PA inventoried all backend capabilities, queues, tasks, agents, spiders, gates, storage, and failure modes using its tools/telemetry. UI surface was partially inferred (no browser automation at time of writing — resolved in Session 1071 with `platform_awareness_tool` + Playwright runner).

---

Below is the **completed 6-layer "Systems Map"** you asked for. It's written as an operator/manual-grade map.

**Important constraint (transparent):** I can fully inventory **backend capabilities, queues, tasks, agents, spiders, gates, storage and failure modes** from the tools/telemetry I have. I **cannot** currently crawl the **React UI** to enumerate every route and button because there is no browser automation tool wired into my toolset.
So for the **UI Surface Inventory** I'm providing:
- **(A) a "Known/Confirmed UI surface" list** (things we have strong evidence exist because they correspond to first-class subsystems you actively use: Governance/Boardroom/Initiatives/Studios), and
- **(B) a "UI discovery contract"** (exactly what Claude Code should add: `/__manifest.json` + Playwright runner) so this layer becomes complete and auto-updating.

If you want, I can then regenerate this map with **100% enumerated routes** once that manifest tool exists.

---

# 1) Surface Map (Humans can click + APIs exist)

## 1A) UI Surface Inventory (current + how to make it canonical)

### Confirmed top-level UI domains (evidence-based)
These are "real" because they map to active queues/tools and you referenced them explicitly:

| UI area | Evidence it exists/is wired |
|---|---|
| **Governance / Boardroom** | Boardroom attention + decisions are active and queryable; gates exist and are being waived/not_started. |
| **Initiatives** | Pipeline orchestrator shows initiatives by stage/status; "advance initiative pipeline" runs every 15 min. |
| **Image Studio / Video Studio** | Media polling tasks exist; media agent category rotation exists; DaVinci tools exist; "poll_processing_videos" runs. |
| **Content/Blogs** | Auto-enhance blogs, podcast generation, surgical moves sessions for publish/revise/kill. |

### Known/likely routes (NOT guaranteed without UI manifest)
These are the routes you and I have used as labels, but they need to be confirmed by a UI manifest:

- `/governance` (Boardroom overview: attention + decisions + gates)
- `/boardroom` (decision/attention control plane)
- `/initiatives` (pipeline overview and initiative detail pages)
- `/studios/image`
- `/studios/video`
- `/content` or `/blogs` (drafts/review/publish)
- `/spiders` or `/intel` dashboards (spider feeds / intelligence modules)

### What Claude Code needs to add so this becomes complete (canonical)
Add **one frontend endpoint** that exports the app's routable surfaces.

**Contract: `GET /__manifest.json`**
- Includes: `routes[]`, `nav groups`, `featureFlag`, `rolesAllowed`, and the **primary API dependencies** per route.
- This becomes the canonical UI inventory, and I can reflect it exactly.

**Then** add a Playwright "UI Runner" so I can interact with the UI (click/verify) and not just infer via backend.

---

## 1B) API Surface Inventory (what exists now in the backend/tool plane)

Because we don't have a raw HTTP endpoint crawler tool, the **most reliable API surface map** I can provide is the platform's **tool/API contracts** (these are your stable backend "entry points" used by UI and agents).

### Control-plane / Governance APIs (via tools)
| API/Tool entry point | Reads/Writes | Object type(s) | Called by |
|---|---:|---|---|
| `boardroom_tool.list_attention` | Read | AttentionItem | Governance UI / PA |
| `boardroom_tool.approve_attention` / `ignore_attention` | Write | AttentionItem status | Human operator actions |
| `boardroom_tool.list_decisions` | Read | DecisionItem | Governance UI / PA |
| `boardroom_tool.promote_decision` / `reject_decision` | Write | DecisionItem status | Human operator actions |
| `gates_tool.list/details` | Read | Gate | Governance UI / automation |
| `human_decisions_tool.list/decide` | Read/Write | HITL Decision | Human approvals |

### Initiative pipeline APIs
| Tool | Reads/Writes | Object type(s) |
|---|---:|---|
| `initiative_tool.list/stats/details` | Read | Initiative |
| `initiative_tool.action_items` | Read | InitiativeActionItem |
| `initiative_tool.start_action_item/complete_action_item` | Write | ActionItem status |
| `initiative_tool.stage_document` | Read | StageDocument |
| `pipeline_orchestrator_tool.status` | Read | Pipeline status snapshot |

### Studios / media APIs
| Tool | Reads/Writes | Object type(s) |
|---|---:|---|
| `media_tool.list/detail/delete` | Read/Write | MediaAsset |
| `davinci_tool.health/render/status/result/jobs/grades` | Read/Write | Resolve render jobs + outputs |
| `run_agent` with `image_generation_agent`, `video_generation_agent`, `video_editing_agent`, `resolve_agent` | Write | Job + deliverables/media |

### Intelligence modules APIs
| Tool | Reads/Writes | Object type(s) |
|---|---:|---|
| `stock_intelligence_tool.*` | Read | Market briefs/alerts/predictions/SEC filings |
| `sports_betting_tool.*` | Read | Predictions, arbs, sharp action, wagers, odds |
| `legislation_tool.*` | Read | Bills, summaries, status, RAG answers |
| `spider_data_tool.*` | Read | Scraped items, feeds |

### Observed performance notes (where we do have telemetry)
- **Celery throughput:** ~1022 tasks/hour; **99.6% success** (system healthy).
- Known tool failures in last 7 days include:
  - `workflow_orchestration_agent` tool calls timing out at 60s (PA)
  - `strategic_review` unknown agent mapping error (PA)
  - Video generation tool returning HTTP 400 (VideoAgent)
  - Redis connectivity error hit `legal_doc_drafter_agent` once (infra/network)

---

# 2) Capability Graph (How stuff flows end-to-end)

Below are the "canonical flows" in graph form. Each flow lists: triggers -> queue -> tasks -> state objects -> approval landing zone.

## Flow A: Spider -> Signal/Insight -> Artifact -> Gate -> Boardroom
- Scheduled: `autonomous-intelligence-loop` (every 15 min)
- Direct spider runs (spider network tasks)

**Queues / tasks (observed)**
- Celery tasks in rotation + autonomous monitors (agents queue / long_running)
- Spider freshness is actively updating (items in last 2h)

**State objects created**
- SpiderData items (scraped content)

**Gates**
- `gates_tool` shows many gates being created and then "waived" (risk_level low). That implies a gate layer exists in the artifact execution path.

**Approval landing zones**
- Boardroom attention items / decisions (human review)
- Human decisions queue (if configured per action type)

---

## Flow B: Initiative Stage -> Gate -> Action Items -> Agent Execution -> Deliverable -> Review -> Publish
- User creates initiative / promotes from TRIAGE
- Scheduled: `advance-initiative-pipeline` (every 15 min)
- Scheduled: `auto-kickstart-stuck_initiatives` (every 10 min)

**Queue / tasks**
- `core.tasks.advance_initiative_pipeline`
- `core.tasks.process_initiative_auto_progression`
- `core.tasks.generate_initiative_stage_document` (notably: **this is the #1 failing task in 7-day error summary**: 157 failures)

**State objects**
- Initiative
- Stage documents (per stage)
- Action items
- Deliverables (library entries, content, plans)
- Content review items (blogs/deliverables) + "Surgical Moves" sessions

**Approval landing zones**
- Content review queue (`content_review_tool`)
- Surgical moves verdict ("publish/revise/kill" sessions)
- Boardroom (if escalated)

---

## Flow C: Studio request -> Job -> Render -> Media Asset -> Review -> Publish
- User action in Image/Video Studio UI (not directly browsable yet)
- Agent-driven: autonomous content studio loop (every 4h)
- Scheduled polling: `core.tasks.poll_processing_videos` (every ~2 min per breakdown)

**Queue / tasks**
- Media jobs created by agents or UI
- Pollers update state and finalize outputs

**State objects**
- Job records (generation/edit/render)
- Media assets stored in media library (listable via `media_tool`)
- DaVinci job records (if Resolve node used)

**Approval landing zones**
- Content review / editorial gate (if required)
- Boardroom (if a gate flags risk/cost)

---

## Flow D: RAG-style module (Legislation / filings) -> retrieve -> answer -> (optional) artifact
- User queries (legislation_tool.ask/summary/status)
- Scheduled SEC filings analyzers (`autonomous-sec-filing-analyzer`)

**State objects**
- Retrieved documents (spider data / filings)
- Answer outputs (and potentially saved deliverables)

**Approval landing zones**
- Usually none (read-only), unless the answer becomes an artifact promoted to boardroom or content.

---

# 3) System Registry (canonical subsystems + "what's real")

This is a canonical registry of "subsystems that are actively wired," with risk/cost flags.

## 3A) Governance / Boardroom Control Plane
- **Purpose:** Human-in-the-loop control of attention, decisions, and gates.
- **Outputs:** approve/ignore/promote/reject actions.
- **Dependencies:** Postgres + Celery + agent router.
- **Storage:** attention items, decisions, gate records.
- **Schedules/tasks:** `auto-approve-boardroom-items` (every 4h) + orchestration checks.
- **Agents used:** WorkflowAgent, coordinators (StockAuditCoordinator), etc.
- **UI surfaces:** Governance/Boardroom pages (to be enumerated via UI manifest).
- **Demo mode:** active.
- **Risk level:** **Medium** (it triggers real execution/promotion decisions).

## 3B) Initiative Pipeline
- **Purpose:** Convert ideas -> staged execution -> deliverables.
- **Inputs:** user-created initiatives, autonomous kickstarts.
- **Outputs:** stage docs, action items, deliverables.
- **Dependencies:** content queue + agents.
- **Schedules:** `advance-initiative-pipeline` (15m), `auto-kickstart-stuck_initiatives` (10m).
- **Risk level:** Medium (can create lots of work, cost).

**Operational note:** `core.tasks.generate_initiative_stage_document` is a top failure source in last 7 days (157 failures). That's a real reliability hotspot.

## 3C) Spiders / Data Ingestion
- **Purpose:** Bring external data into platform (news, jobs, legal, finance, social, etc.).
- **Inputs:** scheduled spider runs.
- **Evidence:** **14,832 scraped items (7 days)**; 45 spiders active in last 2h window.
- **Risk level:** Low-Medium (cost + potential licensing/ToS + noise).

## 3D) Stock Intelligence
- **Purpose:** briefs, alerts, predictions, SEC filings.
- **Inputs:** market spiders + SEC filing spider/analyzer.
- **Outputs:** dashboards/alerts and boardroom items.
- **Schedules:** `autonomous-sec-filing-analyzer`, earnings predictor, movement monitors.
- **Risk:** Medium (decision quality, financial advice constraints).

## 3E) Sports Betting Intelligence
- **Purpose:** predictions, arbitrage, sharp action, wager tracking.
- **Inputs:** odds spiders (e.g., theodds, kalshi) + models.
- **Outputs:** predictions, briefs, wagers.
- **Risk:** Medium-High (financial risk, compliance).

## 3F) Content Studio (Blogs/Podcast/Surgical Moves)
- **Purpose:** generate content, revise via deliberation, approve/publish.
- **Outputs:** blog drafts, podcast episodes, revised content.
- **Evidence:** `auto-enhance-blogs`, `auto-generate-podcast-episode`, surgical move sessions in last 24h.
- **Risk:** Medium (brand risk, hallucinations, plagiarism if not grounded).

## 3G) Image / Video Studios + Rendering
- **Purpose:** generate/edit media; render via Resolve node.
- **Inputs:** user jobs or agent jobs.
- **Outputs:** media assets; Resolve render outputs.
- **Evidence:** `poll_processing_videos` task; `davinci_tool` exists; media agent rotation exists.
- **Risk:** Medium (cost, storage).

## 3H) "Body / Organism" orchestration (system health metaphors)
- **Purpose:** internal health checks and coordination loops.
- **Evidence:** tasks like `coordinate_body`, `check_brain`, `immune_scan`, etc. executing frequently.
- **Risk:** Low (internal only).

## 3I) US Bills RAG
- **Purpose:** track and answer questions about legislation.
- **Tool:** `legislation_tool` (overview/trending/search/status/summary/ask)
- **Risk:** Low-Medium (accuracy/grounding).

## 3J) Voice subsystem
- **Current evidence:** Router shows **AudioAgent is blocked**; no direct "voice studio" tool in my current tool catalog.
- **Status:** **present in DB, not fully operational** (blocked).
- **Risk:** Medium (PII).

## 3K) Discord / External integrations
- **Current evidence:** Not directly observable via tools provided in this session.
- **Status:** **unknown/unverified wiring** until we add a UI manifest or a module registry endpoint.

---

# 4) Tooling Map (tools available + failure points)

This is the actual "operator tool catalog" I can use and agents can call (as exposed to me).

## 4A) Tool catalog (by category)
**Governance / HITL**
- `boardroom_tool` (list/approve/ignore/promote/reject + triage batch + classify suggest)
- `human_decisions_tool` (list/decide)
- `gates_tool` (list/details)
- `feedback_tool` (submit/list/stats/update)

**Pipeline**
- `initiative_tool` (list/stats/details/action items/stage docs/promote/start/complete)
- `pipeline_orchestrator_tool` (status)

**Content**
- `content_review_tool` (list/details/approve/reject/search/recent/stats)
- `generate_blog_tool` (generate via deliberation pipeline)
- `deliverables_tool` (full CRUD library)

**Studios / Media**
- `media_tool` (list/detail/delete)
- `davinci_tool` (health/render/status/result/jobs/grades)
- `run_agent` (image/video/audio/3D/character/talking character + strategy agents)

**Intelligence**
- `stock_intelligence_tool`
- `sports_betting_tool`
- `legislation_tool`
- `spider_data_tool`
- `web_search` / `research_and_create_tool`

**Ops / Observability**
- `system_health_tool`, `recent_activity_tool`, `error_summary_tool`
- `execution_history_tool`, `learning_patterns_tool`
- `task_breakdown_tool`, `cost_telemetry_tool`, `check_resource_budget`
- `scheduled_tasks_tool`, `workspace_tool`, `get_system_alerts`, `status_snapshot_tool`

## 4B) Typical failure modes (evidence + known patterns)
From the last 7 days error summary (real examples):

### 1) Tool-level failures (direct tool invocation)
**Observed in last 7 days (real incidents):**
- **TOOL_TIMEOUT (60s hard timeout)**
  - Example: `workflow_orchestration_agent` timed out twice when I tried to assign agents.
  - Impact: makes "operator actions" look like they failed even when the backend might be fine.
  - Mitigation: raise timeout for long tools; add async job pattern (start -> poll).

- **TOOL_EXCEPTION: unknown agent / wrong mapping**
  - Example: `strategic_review` failed because it referenced `StrategyAgent` which is not in the available agent list.
  - Mitigation: central registry of agent names + validation in the tool wrapper.

- **Infra connectivity**
  - Mitigation: Redis DNS/service discovery; health-gate tool execution on Redis availability.

- **Upstream vendor/API errors (HTTP 400)**
  - Example: `VideoAgent` video generation failed multiple times with HTTP 400.
  - Mitigation: capture request payloads + provider error bodies; add "payload validator" before submit.

### 2) Celery task failures (async background jobs)
**Observed in last 7 days:**
- **`core.tasks.generate_initiative_stage_document`: 157 failures**
  This is the single biggest reliability hotspot in your system right now.
  - Likely failure classes (need logs to confirm): prompt payload too large, missing context, DB object missing, serialization mismatch.
  - Mitigation: add structured context validation + fallbacks; cap context size; store a "failure_reason" field on StageDocument generation runs.

- **`core.tasks.execute_approved_artifacts`: 4 failures**
  - Risk: execution of things humans thought they approved; needs gate + rollback semantics.

### 3) Agent execution failures/timeouts
**Observed (timeouts dominate):**
- TrendAnalysisAgent (36 timeouts)
- ContentWriterAgent (33)
- WorkflowAgent (23)
- CompetitorAnalysisAgent (17)
...and others.

**Interpretation:** agents are being asked to do too much per call or are hitting model/provider latency.
**Mitigation:** enforce max-output tokens, stepwise decomposition, and "partial deliverable saves."

---

## 4C) Where logs live + how to replay/debug (practical operator map)

### Logs / traces you should consider "authoritative"
- **Tool call logs:** (you have tool call stats aggregated nightly)
  Use these to correlate "UI clicked X" -> "tool call Y" -> "result ok/error."
- **Celery task logs:** for `core.tasks.*` and `autonomous.*`
  These are the ground truth for background execution.
- **Agent execution history:** via `execution_history_tool` (and/or DB tables behind it)
- **Error summary:** `error_summary_tool` provides clustered failure modes.

### Minimum replay recipe (what Claude Code should support)
For every mutation (approval, publish, render), store:
- `request_id`
- `actor` (user/agent)
- `input_payload_hash`
- `tool_name` or `task_name`
- `state_object_id` (initiative_id, gate_id, attention_id, media_id, etc.)
Then expose: `POST /internal/replay/{request_id}` (or a tool) to re-run with the same inputs in a sandbox.

---

# 5) Data + Storage Map (where everything is stored; what is the "truth")

## 5A) Core stores

### 1) Postgres (primary system of record)
**What lives here (confirmed by tool surfaces):**
- **Boardroom**
  - Attention items
  - Decisions
- **Gates**
  - Gate objects (status: waived/not_started/etc.)
- **Initiatives**
  - Initiative objects
  - Stage documents
  - Action items
- **Content**
  - Blog drafts / review queue entries
  - Deliverables library entries
- **Ops/Observability**
  - Tool call stats aggregates
  - Execution history

**Why Postgres is the "truth":**
- All operator-facing control plane objects (approve/ignore/promote/reject) are persisted there.

### 2) Redis (confirmed dependency)
Redis is used at least for:
- Celery broker and/or result backend
- Some tool execution paths (we saw a Redis DNS/connectivity error bubble up)

**Truth note:** Redis is **not** the truth source; it's transient. If Redis is down, you can see failures that look like "the tool is broken" even though Postgres is fine.

### 3) Object storage (S3 or equivalent) -- for media + files
**Implied by:**
- `media_tool` (assets must be stored somewhere durable)
- DaVinci "result" artifacts and render outputs

**Truth note:** metadata in Postgres; binary objects in object storage.

### 4) Vector store / embeddings
**Not directly verifiable in this session** (I can't see your schema/tables from tools), but you explicitly operate RAG-like modules (US Bills RAG, SEC filings analysis).
Most likely it's:
- **pgvector inside Postgres**, or
- a separate vector DB.

**Action to make this non-ambiguous:** add a `vector_store_tool.info` (or manifest) listing:
- embedding models used
- tables/columns
- chunking policy
- retention

### 5) Logs / analytics store
We know you have:
- aggregated tool call stats
- error summaries
- execution history

But I can't see retention windows and exact tables without a "data dictionary tool." See 5D.

---

## 5B) "Truth sources" (what table/object decides the official status of X)

This is the most common operator confusion: "which status is real?"

### 1) Boardroom items
- **Truth source for "needs attention":** Boardroom AttentionItem state
- **Truth source for "pending decision":** Boardroom DecisionItem state
- **Truth source for "gated":** Gate status (waived/not_started/in_progress/complete)

**Rule of thumb:**
If something is in Boardroom, that's the human control plane; if it's in Gates, that's the policy layer; if it's in Initiatives, that's the execution plan.

### 2) Initiative execution
- **Truth source for "where is it in the process":** Initiative status + stage + action item statuses
- **Truth source for "deliverable done":** Deliverables library entry + content review approval state (if publishing)

### 3) Media (Image/Video)
- **Truth source for "render complete":** DaVinci job status + MediaAsset existence
- **Truth source for "published":** publish target record (CMS/post id/etc.) -- not verifiable from tools in this session

---

## 5C) Data lineage (what to store so you can answer "how did it get here?")
For every artifact that lands in Boardroom or Review Queue, store:
- `origin_type` (spider / initiative / studio / manual)
- `origin_id` (spider_item_id, initiative_id, job_id)
- `transform_chain[]` (task names + agent names)
- `gate_chain[]` (gate ids + outcomes)
- `evidence_refs[]` (spider item ids, citations)

You already have pieces of this; the map is telling you what must be *standardized*.

---

## 5D) What's missing to make the data map complete (and how Claude Code can fix it)
Add a **Data Dictionary endpoint/tool**:
- Lists tables/models relevant to the platform objects (Boardroom, Initiative, Gate, Deliverable, MediaAsset, ExecutionHistory, ToolCallLog)
- Includes retention policies
- Includes foreign key relationships for lineage

Without this, any "complete map" will always be partially inferred.

---

# 6) Safety / Policy Gates Map (operator manual)

## 6A) Gate types (what exists today)
From `gates_tool.list` we can confirm:
- Gate objects exist with:
  - `risk_level` (observed: many `low`)
  - `status` (observed: `waived`, `not_started`)
  - `topic/summary` tied to discussions like "actionable recommendations..." and "buyer personas..."

**Observation:** Right now, gates are being created frequently and then **waived**. That means:
- either the risk classifier is overly permissive, or
- low-risk items are intentionally grandfathered to avoid blocking throughput.

## 6B) What requires human classification (recommended canonical policy)

### Policy Map: "Action type -> required gate(s) -> human required?"
| Action type (what the system might do) | Gate needed | Human required? | Why |
|---|---|---:|---|
| Publish to public website / social | **Editorial + Brand safety + Citation/grounding** | **Yes** (unless whitelisted autopost) | Reputation risk + compliance |
| Execute real-money betting action (place wager) | **Financial risk + jurisdiction + bankroll limits** | **Yes** (always, unless you explicitly enable autopilot with hard caps) | Direct monetary risk |
| Trade/portfolio execution (if any) | **Financial + suitability** | **Yes** | Direct monetary risk |
| Generate video using paid provider / GPU-heavy job | **Cost gate** | Often yes (or budget-capped autopilot) | Cost spikes |
| Ingest PII sources (Slack/Email/HRIS) | **PII/compliance gate** | **Yes** | Privacy + legal |
| Run spiders with ToS-sensitive sources | **Compliance/licensing gate** | Usually yes for new sources | Legal/ToS |
| Create internal drafts (blog drafts, outlines, reports) | Low-risk gate | No (safe autopilot) | Non-public |
| Summarize public data / produce research memo | Low-risk gate | No | Low impact |

**Key point:** Gates should be keyed to *actions*, not topics. "Actionable recommendations" can be low-risk if it's just a memo; it becomes high-risk if it triggers publishing, spend, outreach, or execution.

---

## 6C) What is grandfathered (safe-by-default autopilot)

### Safe autopilot candidates (recommended)
- Any **read-only** analysis: summaries, rankings, research digests
- Creating **drafts** that land in a review queue (content review / boardroom)
- Spider ingestion into internal storage (as long as sources are allowlisted)
- Updating internal dashboards/aggregations
- Creating initiatives in **TRIAGE** status (not ACTIVE) without starting execution

### What should *not* be grandfathered
- Anything that:
  - posts publicly,
  - spends money above a threshold (LLM/GPU/render),
  - triggers emails/DM outreach,
  - touches PII,
  - triggers betting/trading execution,
  - deletes data/assets.

---

## 6D) What actions are blocked without classification (hard stops)

1) **Publish blocked** unless:
   - Editorial review passed (content review approval OR boardroom publish approve)
   - Sources/citations present if claims made
2) **Studio render blocked** unless:
   - Cost gate approved OR job within a daily budget cap
3) **PII ingestion blocked** unless:
   - compliance gate approved (and data minimization set)
4) **Wager execution blocked** unless:
   - manual approval *or* autopilot enabled with tight bankroll+jurisdiction policy

---

## 6E) "Always manual" list (operator guarantee)
- Enable/disable feature flags or agents (especially blocked agents)
- Connect new external accounts (OAuth tokens, API keys)
- Delete media assets or deliverables
- Change risk thresholds / budget thresholds
- Betting/trading execution (unless you explicitly flip to autopilot mode)

---

## 6F) Gate health metrics (so you can detect the next "stuck gate" fast)
- # gates created/day, by risk_level
- % waived vs % completed vs % stuck-in-progress > 24h
- average time-to-resolution by gate type
- "false critical" rate (critical severity items that are informational)

---

# Addendum A: Agent inventory (what exists + how to make it fully browsable)

## A1) Verified global counts
- **218 total agents** in DB
- **82 router-routable**
  - **72 fully enabled**
  - **8 rerouted**: `COOAgent, CTOAgent, CodeReviewAgent, ContentDistributionAgent, DevOpsAgent, FullStackDeveloperAgent, VideoAgent, WorkflowAgent`
  - **2 blocked**: `AudioAgent, CodeGeneratorAgent`

## A2) Agent groups (as currently categorized)
The platform categorizes agents by type (counts from the registry):
- core (76), income (20), career (15), content (15), job_search (12),
- finance (12), ai_ml (11), business (14), marketing (10), creative (10),
- analytics (7), research (5), automation (4), consulting (3), clean_architecture (2),
- plus small "investment/routable" categories.

## A3) How to produce the "everything about every agent" sheet (what's missing)
Right now I can list agents with: name, type, specialization, effectiveness score, and routing status.
To make this complete, Claude Code should expose for each agent:
- description/purpose
- tool permissions (which tools it can call)
- default prompts / system instructions (or a hashed/versioned reference)
- cost profile (avg tokens, typical latency)
- safety constraints (PII allowed? publishing allowed?)
- failure rate + top failure reasons

That becomes your "Agent Catalog" page and can power policy gates.

---

# Addendum B: What I need from you to make layer (1) fully complete

> **UPDATE (Session 1071):** Both items below have been implemented:
> 1. `platform_awareness_tool` with `get_manifest` action returns all 30 routes, 3 studios, 8 capabilities
> 2. `run_ui_smoke` Playwright management command for UI verification
>
> The PA can now regenerate Section 1 with exhaustive route data.

To finish the **UI Surface Inventory** with zero ambiguity, I need one of these:

1) **Frontend manifest endpoint** (`/__manifest.json`) listing routes/nav/flags/roles/API deps
or
2) **Playwright UI runner tool** so I can crawl the app and extract surfaces.

Once either exists, I'll regenerate Section 1 with an exhaustive table:
- every route
- nav label + section
- roles/feature flags
- primary API calls + mutations
- and "called by agents" crosslinks.
