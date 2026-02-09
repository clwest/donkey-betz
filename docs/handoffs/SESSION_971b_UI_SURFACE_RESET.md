# Session 971b — UI + Discord Surface Reset

**Date:** February 8, 2026
**PRs:** #985 (Telemetry + Discord docs), #986 (Workspace shell 18→9), #987 (Content consolidation), #988 (Double nav fix), #989 (Legacy route cleanup), #990 (Command Center "Now" hub)
**Status:** COMPLETE — All 7 PRs merged. Bundle reduced 26.5%. 18 workspace tabs → 9. 26 legacy routes → redirects.

---

## What Was Done

Session 971b executed a 7-PR plan to consolidate the platform's navigation surface. The workspace went from 18 tabs in 5 groups to 9 tabs in 4 groups. 26 standalone page routes were converted to workspace tab redirects, dropping the frontend bundle from 3,062 KB to 2,253 KB. A "Now" hub was added to the Command Center homepage.

### PR A — Page-View Telemetry (#985)

**New files:** `frontend/src/hooks/usePageTracking.ts`, `core/views_telemetry.py`
**Modified:** `frontend/src/components/layout/Layout.tsx`, `frontend/src/App.tsx`, `core/urls.py`

- `usePageTracking()` hook tracks route changes via `useLocation()`, debounced 500ms
- `useWorkspaceTabTracking(tab, subtab?)` tracks workspace tab switches
- Fire-and-forget `POST /api/v1/telemetry/page-view/` — never blocks UI, never throws
- Backend writes Redis counters: `page_views:{date}:{route}` and `page_tabs:{date}:{tab}:{subtab}`
- 90-day TTL, `@csrf_exempt`, always returns 204

### PR E — Discord Integration Docs (#985)

**New file:** `docs/DISCORD_INTEGRATION.md`

- Complete reference for all 112 Discord slash commands across 20 categories
- ACTIVE/DORMANT status annotations (many commands registered but not functional)
- 12 notification channels documented with trigger conditions
- Development guidelines for adding new commands
- Voice capabilities, error patterns, and known issues

### PR B1 — Workspace Shell Reset: 18→9 Tabs (#986)

**New files:** `frontend/src/pages/workspace/tabs/SystemTab.tsx`, `frontend/src/pages/workspace/tabs/DataIntelTab.tsx`
**Modified:** `frontend/src/pages/workspace/types.ts`, `frontend/src/pages/workspace/tabs/index.ts`, `frontend/src/pages/WorkspacePageNew.tsx`

The 9-tab model:

| Group | Tabs |
|-------|------|
| Core | Command, Initiatives, Boardroom |
| Content | Content Studio |
| System | System, Ops |
| Data | Data & Intel, Knowledge, Learn |

Merges:
- **System** = Infrastructure + Orchestration + Triggers (8 sub-tabs: health, services, llm, integration, monitor, workflows, hivemind, triggers)
- **Data & Intel** = DataSources + Intelligence (6 sub-tabs: spiders, feed, learning, reasoning, safety, collective)
- **Boardroom** absorbs Governance
- **Content** absorbs ConceptForge, Voices, Files (in B2)
- **Knowledge** absorbs AI Consciousness

Key architecture:
- `normalizeWorkspaceTab(tab: string): WorkspaceTab` — maps 18 legacy tab IDs to 9 canonical IDs
- `legacyTabToSubTab(tab: string): string | undefined` — preserves sub-tab context during redirect (e.g., `?tab=orchestration` → System tab, Monitor sub-tab)
- URL auto-normalization via `useEffect` — old `?tab=infrastructure` rewrites to `?tab=system`
- WorkspaceTab union type includes both new and legacy IDs for type compatibility
- 9 unused tab imports removed from WorkspacePageNew → -117 KB tree-shaking

### PR B2 — Content Consolidation (#987)

**Modified:** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx`, `frontend/src/pages/workspace/types.ts`, `frontend/src/pages/WorkspacePageNew.tsx`

Content Studio grew from 6 → 9 sub-tabs:
- Existing: Gallery, Channels, Blogs, Documents, Podcast, Distribution
- Added: **Dossiers** (ConceptForgeTab), **Voices** (VoiceMarketplaceTab), **Files** (FilesTab)

Adapter/delegate pattern — existing components render as-is inside ContentStudioTab. ContentStudioTab now accepts `initialSubTab` and `activeWorkspaceId` props. `legacyTabToSubTab()` updated: `conceptforge→dossiers`, `voices→voices`, `files→files`.

### PR B3 — Eliminate Double Sub-Tab Nav (#988)

**Modified:** `InfrastructureTab.tsx`, `OrchestrationTab.tsx`, `DataSourcesTab.tsx`, `IntelligenceTab.tsx`, `SystemTab.tsx`, `DataIntelTab.tsx`

**Problem:** SystemTab and DataIntelTab delegated to full original components which rendered their own sub-tab nav, creating double navigation.

**Solution:** Added `controlledSubTab?: string` prop to 4 original tabs. When provided:
1. Uses the prop value instead of internal `useState`
2. Hides the internal sub-tab nav bar

SystemTab and DataIntelTab now pass `activeSubTab` as `controlledSubTab` — single unified nav level. Original tabs still work standalone (without the prop) for backwards compatibility.

### PR C — Legacy Route Cleanup (#989)

**Modified:** `frontend/src/App.tsx`

26 standalone page routes replaced with `<Navigate replace>` redirects:

| Target | Legacy routes |
|--------|---------------|
| `/workspace?tab=system` | body-health, llm-routing, integration-health, orchestration, agent-monitor, autonomous, hive-mind |
| `/workspace?tab=dataintel` | spiders, spider-feed, reasoning, collective |
| `/workspace?tab=content` | podcast, content-channels, distribution, documents, voice-marketplace, blogs |
| `/workspace?tab=knowledge` | memory-palace, evolution, agent-mood, time-capsules, time-travel, agent-social, relationships |
| `/workspace?tab=learning` | learning-journey |

22 page imports removed. **Bundle: 3,062 KB → 2,249 KB (-813 KB, -26.5%).** Modules: 3,290 → 2,236 (-1,054).

8 pages kept standalone: advisors, neural-orchestra, conversation-contract, mythology-lab, billing, analytics, docs-index, blog/:blogId.

### PR D — Command Center "Now" Hub (#990)

**Modified:** `frontend/src/pages/CommandCenterPage.tsx` (+154 lines)

Three-panel strip between header and PA chat on `/`:

1. **Attention Queue** — urgent/high pending decisions from `humanApi.attentionStream`. Red badge, top 2 items with urgency dots. Click → `/workspace?tab=boardroom`.
2. **Active Work** — running orchestration executions from `orchestrationApi.listExecutions({ status: 'running' })`. Blue badge, spinner per execution, step progress. Polls 15s. Click → `/workspace?tab=system`.
3. **System Pulse** — body health %, active agent count, system status. Uses already-fetched `bootData` and `bodyVitals` (zero extra API calls). Click → `/workspace?tab=system`.

---

## Architecture Decisions

1. **Adapter pattern over refactor** — SystemTab/DataIntelTab/ContentStudioTab wrap existing components rather than extracting their internals. Minimizes blast radius. B3 added `controlledSubTab` to suppress inner navs without restructuring files.

2. **Legacy compatibility for 2-4 weeks** — `normalizeWorkspaceTab()` and redirect routes ensure old bookmarks, Discord links, and browser history entries keep working. Can remove after transition period.

3. **Billing + Analytics kept standalone** — These were in InfrastructureTab's nav but intentionally excluded from SystemTab's 8 sub-tabs. They remain at `/billing` and `/analytics` as standalone pages until a proper Admin tab is created.

4. **Fire-and-forget telemetry** — Page view tracking never blocks UI, never throws. Redis counters with 90-day TTL. Data will inform which legacy routes can be fully removed.

---

## Bundle Size Progression

| State | Size | Delta |
|-------|------|-------|
| Pre-session | ~3,062 KB | — |
| After B1 (18→9 tabs) | ~2,945 KB | -117 KB |
| After C (route cleanup) | 2,249 KB | -813 KB |
| After D (Now hub) | 2,253 KB | +4 KB |
| **Net** | **2,253 KB** | **-809 KB (-26.4%)** |

---

## Files Created (4)

| File | Purpose |
|------|---------|
| `frontend/src/hooks/usePageTracking.ts` | Route + tab telemetry hooks |
| `frontend/src/pages/workspace/tabs/SystemTab.tsx` | Merged System tab adapter |
| `frontend/src/pages/workspace/tabs/DataIntelTab.tsx` | Merged Data & Intel tab adapter |
| `docs/DISCORD_INTEGRATION.md` | 112-command Discord reference |

## Files Modified (12)

| File | Changes |
|------|---------|
| `frontend/src/App.tsx` | 26 routes → redirects, 22 imports removed |
| `frontend/src/pages/WorkspacePageNew.tsx` | 18→9 tabs, normalizeWorkspaceTab, legacySubTab |
| `frontend/src/pages/CommandCenterPage.tsx` | NowHub component, running executions query |
| `frontend/src/pages/workspace/types.ts` | SystemSubTab, DataIntelSubTab, ContentStudioSubTab extended, normalizeWorkspaceTab(), legacyTabToSubTab() |
| `frontend/src/pages/workspace/tabs/index.ts` | Added SystemTab, DataIntelTab exports |
| `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx` | +3 sub-tabs (dossiers, voices, files), initialSubTab/activeWorkspaceId props |
| `frontend/src/pages/workspace/tabs/InfrastructureTab.tsx` | controlledSubTab prop |
| `frontend/src/pages/workspace/tabs/OrchestrationTab.tsx` | controlledSubTab prop |
| `frontend/src/pages/workspace/tabs/DataSourcesTab.tsx` | controlledSubTab prop |
| `frontend/src/pages/workspace/tabs/IntelligenceTab.tsx` | controlledSubTab prop |
| `frontend/src/components/layout/Layout.tsx` | usePageTracking() call |
| `core/urls.py` | Telemetry route |

## Backend Files Created (1)

| File | Purpose |
|------|---------|
| `core/views_telemetry.py` | Redis page-view counter endpoint |

---

## What's Next

### Immediate follow-ups
- **Remove legacy redirect routes** after 2-4 weeks of telemetry data confirming no traffic
- **Admin tab** — Create a dedicated Admin area for Billing, Analytics, and system config (currently standalone pages)
- **Content Studio overflow** — 9 sub-tabs may benefit from a "More" dropdown or grouped sections

### Potential future work
- **Code-splitting** — `React.lazy()` for workspace tabs to further reduce initial bundle
- **Sidebar update** — Remove `/mythology-lab` from sidebar (now in DataIntel > Safety), consolidate sidebar to match 9-tab model
- **Discord command cleanup** — Use the ACTIVE/DORMANT audit in `DISCORD_INTEGRATION.md` to prune non-functional commands
- **Deep sub-tab URLs** — Support `?tab=system&sub=monitor` for direct deep-linking to sub-tabs
