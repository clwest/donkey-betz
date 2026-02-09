# Session 972 - Start Here

**Previous Session:** 971b (UI + Discord Surface Reset)
**Date:** February 8, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** | **Workspace: 9 TABS** (down from 18) | **Bundle: 2,253 KB** (-26.4%) | **26 Legacy Routes → Redirects** | **Command Center "Now" Hub: ACTIVE** | **Page Telemetry: ACTIVE** | **Discord Docs: 112 COMMANDS** | **Risk-Aware RAG: COMPLETE** | **Unified PA: ANALYTICAL ADVISOR** | **Phase 0-4 Deliberation: COMPLETE** | **Content Deliberation Pipeline: ACTIVE** | **PA Live Telemetry: ACTIVE** | **Surgical Moves Verification: ACTIVE** | **ToolCallRecord: LIVE** | **Attention Coverage: 7 SECTIONS**

---

## Session 971b Summary (Just Completed)

### UI + Discord Surface Reset — 7 PRs (#985-#990)

Consolidated the platform's navigation surface from 18 workspace tabs + 62 routes down to 9 tabs + 36 routes. Bundle reduced 26.4%.

**PR A+E — Telemetry + Discord Docs (#985)**
- Fire-and-forget page-view tracking to Redis counters (debounced 500ms, never blocks UI)
- `docs/DISCORD_INTEGRATION.md` — complete 112-command reference with ACTIVE/DORMANT status

**PR B1 — Workspace Shell Reset (#986)**
- 18 tabs → 9 tabs: Command, Initiatives, Boardroom, Content, System, Ops, Data & Intel, Knowledge, Learn
- `normalizeWorkspaceTab()` maps legacy `?tab=` params for backwards compat
- `legacyTabToSubTab()` preserves sub-tab context during redirects
- SystemTab (Infra + Orch + Triggers) and DataIntelTab (DataSources + Intelligence) adapters

**PR B2 — Content Consolidation (#987)**
- Content Studio: 6 → 9 sub-tabs (+Dossiers, Voices, Files via delegate pattern)

**PR B3 — Double Nav Fix (#988)**
- `controlledSubTab` prop on 4 original tabs suppresses inner nav when parent drives

**PR C — Legacy Route Cleanup (#989)**
- 26 standalone routes → `<Navigate replace>` to workspace tabs
- 22 page imports removed → **-813 KB bundle** from tree-shaking

**PR D — Command Center "Now" Hub (#990)**
- Three-panel strip on `/`: Attention Queue, Active Work, System Pulse
- Each panel clickable → navigates to relevant workspace tab

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 76 (49 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 77 (72 working, 5 need API keys) |
| Advisors | 25 |
| Active Initiatives | 52 (cleaned from 568 in Session 961c) |
| Database Models | 386+ |
| Services | 134 |
| Celery Tasks | 261 |
| Workspace Tabs | 9 (down from 18) |
| Frontend Bundle | 2,253 KB (down from 3,062 KB) |
| Frontend Routes | 36 (14 standalone + 22 redirects) |
| PA Tools | 90 |
| Attention Sections | 7 |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

### 9-Tab Model

| Group | Tabs | Sub-tabs |
|-------|------|----------|
| Core | Command, Initiatives, Boardroom | — |
| Content | Content Studio | gallery, channels, blogs, documents, podcast, distribution, dossiers, voices, files |
| System | System, Ops | health, services, llm, integration, monitor, workflows, hivemind, triggers |
| Data | Data & Intel, Knowledge, Learn | spiders, feed, learning, reasoning, safety, collective |

---

## Known Issues / Open Items

### Legacy Routes Expire in ~2-4 Weeks
26 legacy routes redirect to workspace tabs. Telemetry counters track which routes still get traffic. After transition period, remove redirect routes entirely.

### Billing + Analytics Orphaned
`/billing` and `/analytics` are standalone pages with no home in the 9-tab model. Need an Admin tab or should be absorbed into an existing tab.

### Content Studio Has 9 Sub-tabs
Pushing visual limits — consider "More" dropdown or grouping if adding more.

### ToolCallRecord Now Populating
Data is flowing but no analytics dashboard exists yet.

### FailureSignature Table Empty
The diagnostic pipeline (Session 856) has 0 records in production. May need activation.

---

## What Could Come Next

### Admin Tab
Create a dedicated workspace tab for Billing, Analytics, and system configuration pages.

### Code-Splitting
`React.lazy()` for workspace tabs — currently all 9 tabs are in the main bundle. Lazy-loading could cut initial load significantly.

### Deep Sub-tab URLs
Support `?tab=system&sub=monitor` for direct deep-linking to specific sub-tabs.

### Sidebar Cleanup
Sidebar still shows `/mythology-lab` (now in DataIntel > Safety) and `/agents` (agents list accessible via workspace). Consolidate to match 9-tab model.

### Discord Command Pruning
Use the ACTIVE/DORMANT audit in `DISCORD_INTEGRATION.md` to remove or fix non-functional commands.

### ToolCallRecord Analytics
Build dashboards: tool usage by agent, latency percentiles, error rates.

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop automatically instead of requiring manual re-trigger.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`). Always use `DJANGO_SETTINGS_MODULE=core.settings`.

**Workspace tab mapping (`types.ts`):**
- `normalizeWorkspaceTab(tab)` — maps any of the 18 legacy tab IDs to 9 canonical IDs
- `legacyTabToSubTab(tab)` — returns the sub-tab to pre-select (e.g., `orchestration → monitor`)
- Both functions are in `frontend/src/pages/workspace/types.ts`

**controlledSubTab pattern:**
- When a parent tab (SystemTab, DataIntelTab) passes `controlledSubTab` to a child (InfrastructureTab, etc.), the child hides its own sub-tab nav and uses the parent's value
- Without the prop, children work standalone with their own nav (backwards compatible)

**PA entrypoint (`unified_pa_entrypoint.py`):**
- Intent routing: `_detect_intent_and_route(message)` returns `(intent, tool_name)` tuple
- Order matters: new intent blocks must go BEFORE existing ones that share keywords
- Tool results: `ToolResult` dataclass with `.ok`, `.result`, `.trace_id`

**BaseAgent `__init_subclass__` (Session 970):**
- Auto-wraps `_execute_tool_call` in subclasses with ToolCallRecord recording
- Recording in `finally` with bare `except: pass` — can never break agent execution

**Model field gotchas:**
- `SignalCluster`: in `core.models_signal_intelligence`, use `detected_at` (NOT `updated_at`)
- `AgentDecisionSummary`: does NOT have a `confidence` field
