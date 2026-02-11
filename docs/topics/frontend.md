# Frontend & UI

React + TypeScript single-page application with 9 workspace tabs, collapsible sidebar, Command Center hub, and PA chat integration. Bundle: 2,253 KB.

## Workspace Architecture

`WorkspacePageNew.tsx` orchestrates 9 modular tabs:

| Tab | Sub-tabs | Purpose |
|-----|----------|---------|
| **Command Center** | "Now" hub + PA chat | 3-panel strip: Attention Queue, Active Work, System Pulse |
| **Content Studio** | Content, Blogs, Podcasts, Calendar, Dossiers, Voices, Files | Content creation and management |
| **Orchestration** | Monitor, Sessions, Execution | Agent orchestration and HiveMind sessions |
| **Intelligence** | Data Sources, Intelligence | Spider data and signal clusters |
| **Markets** | Predictions, Odds, Arbitrage | Market analysis and predictions |
| **Memory** | Palace, Learning, Evolution | Memory system and learning patterns |
| **Operations** | Reports, Audits, Experiments | Operational reports and audit results |
| **System** | Infrastructure, Orchestration, Triggers | Body systems health and Celery tasks |
| **Stocks** | Overview, Briefs, Alerts, SEC, Predictions | Stock intelligence dashboard |

## Tab Normalization

`normalizeWorkspaceTab()` maps 18 legacy tab IDs to 9 canonical ones. `legacyTabToSubTab()` preserves sub-tab context during the mapping. Adapter components (SystemTab, DataIntelTab) handle merged tab logic.

## Route Structure

36 active routes (down from 62). 26 legacy standalone routes redirect via `<Navigate replace>` to workspace tabs. Key routes:
- `/` — AI OS Boot (home page)
- `/ai-studio/` — Main workspace
- `/stocks/` — Stock Intelligence dashboard
- `/command-center/` — Command Center with PA

## Command Center "Now" Hub

3-panel strip between header and PA chat:
- **Attention Queue** — HumanAttentionItems needing review
- **Active Work** — Currently running agent tasks
- **System Pulse** — Body system health summary

Each panel is clickable → navigates to relevant workspace tab.

## PA Integration

**GlobalPADock:** Floating PA chat overlay, accessible from any page. Includes PAConversationSidebar overlay for conversation history.

**CommandCenterPage:** Full-width PA chat with sidebar for conversation list.

**AssistantPage:** Dedicated PA page.

All three use the same async flow: dispatch task → poll status → display response.

## Page Telemetry

`usePageTracking()` hook fires fire-and-forget Redis counters via `POST /api/v1/telemetry/page-view/` on every page navigation.

## Key Frontend Patterns

- **Zustand stores:** paStore (conversations, sidebar state), workspaceStore (active tab/sub-tab)
- **Delegate pattern:** Content Studio sub-tabs use delegate components for Dossiers, Voices, Files
- **controlledSubTab prop:** 4 original tabs suppress inner navigation when parent drives sub-tab selection
- **Bundle optimization:** 2,253 KB (down from 3,062 KB, -26.5%)
