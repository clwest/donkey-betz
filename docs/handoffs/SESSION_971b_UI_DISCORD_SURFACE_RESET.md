# Session 971b — UI + Discord Surface Reset (Hard Scope)

**Date:** February 8, 2026
**Type:** System Review + Redesign Blueprint

---

## Artifact 1: Top 10 User Journeys (Ranked)

### J1. "What should I pay attention to right now?"
- **Intent:** Triage — surface the most important items across the entire system
- **Current entry points:**
  - **Web:** Command Center (`/`) — PA chat + activity cards; Boardroom tab (`/workspace?tab=boardroom`) — pending decisions; Governance tab (`/workspace?tab=governance`) — policies; Command tab (`/workspace?tab=command`) — conversations
  - **Discord:** `/status`, `/digest`, `/ask "what needs attention?"`
- **Pain points:** 3 overlapping triage surfaces (Command Center, Boardroom, Command tab). User must check all three to get a full picture. Boardroom has 1,586+ items with no prioritized view. Command Center activity cards are static.
- **Ideal UX:** Single "Now" view — prioritized feed merging boardroom items, initiative action items, system alerts, and recent agent outputs. Badge on sidebar shows count.
- **Required endpoints:** `GET /api/boardroom/attention/` (exists), `GET /api/initiatives/action-items/` (exists), system_health PA tool (exists)

### J2. "Check on my initiatives and their progress"
- **Intent:** Project management — see what's moving, what's stalled, what needs action
- **Current entry points:**
  - **Web:** Initiatives tab (`/workspace?tab=initiatives`) — stages/list/cards views with modal details, action items
  - **Discord:** `/ask "show my initiatives"`
- **Pain points:** No sub-tabs but the modal is overloaded (origin, action items, signals, conversations, agent activity). No way to see all action items across initiatives in one view. 52 active initiatives means lots of scrolling.
- **Ideal UX:** Kanban board default (stages view is close), plus a cross-initiative action item dashboard. Discord `/initiatives` command would be useful.
- **Required endpoints:** All exist. Could add `GET /api/initiatives/action-items/all/` for cross-initiative view.

### J3. "Read, approve, and publish content"
- **Intent:** Content pipeline — review blog quality, approve/publish, manage distribution
- **Current entry points:**
  - **Web:** Content Studio tab (`/workspace?tab=content`) with 6 sub-tabs (gallery, channels, blogs, documents, podcast, distribution); standalone `/blogs` page; standalone `/blog/:id` viewer
  - **Discord:** `/create-content`, `/content-status`, `/showroom`
- **Pain points:** Content Studio has 6 sub-tabs but blogs also has a standalone page — duplicated surface. Blog viewer is well-built (approve/publish/delete + related posts) but you navigate away from workspace. Gallery sub-tab shows deliverables but not blog drafts ready for review.
- **Ideal UX:** Single content pipeline: drafts queue → review → approve → publish → distribute. The blog viewer is good — it should be the detail view accessed from a unified content list.
- **Required endpoints:** All exist. `/api/v1/research/self-blog/` list + detail + approve + publish + related.

### J4. "See what the system is doing right now"
- **Intent:** Operational awareness — agent activity, task status, system health
- **Current entry points:**
  - **Web:** Orchestration tab (`/workspace?tab=orchestration`) — 4 sub-tabs (monitor, workflows, automation, hivemind); Infrastructure tab (`/workspace?tab=infrastructure`) — 6 sub-tabs (health, integration, services, LLM, analytics, billing); standalone `/agent-monitor`, `/body-health`, `/integration-health`
  - **Discord:** `/status`, `/agents`, `/blockchain-status`
- **Pain points:** System health is spread across 10+ sub-tabs in 2 workspace tabs plus 3 standalone pages. Orchestration and Infrastructure heavily overlap (both show agent/service status). Infrastructure's "health" sub-tab = Body Health = 9 body systems — this is the same as the standalone `/body-health` page.
- **Ideal UX:** Single "System" dashboard with health score at top, active tasks, recent failures. Drill into body systems, LLM routing, or agent monitor from there.
- **Required endpoints:** All exist. system_health PA tool, body system APIs, agent monitor APIs.

### J5. "Research a topic using spider data and agents"
- **Intent:** Deep research — find what spiders have collected, start conversations with relevant agents
- **Current entry points:**
  - **Web:** DataSources tab (`/workspace?tab=datasources`) — 3 sub-tabs (spiders, feed, learning); standalone `/spiders`, `/spider-feed`; Command tab to start conversations; Intelligence tab (`/workspace?tab=intelligence`) — 3 sub-tabs (reasoning, safety, collective)
  - **Discord:** `/research [topic]`, `/trending`, `/spiders`, `/ask [question]`
- **Pain points:** Spider data, feed, and intelligence are in separate tabs. User has to: check spider feed for data → go to Intelligence for reasoning → go to Command to start conversation → back to Initiatives to track. 4 tab switches for one workflow.
- **Ideal UX:** Start from spider feed or a search → see relevant data → one-click "start conversation with agents about this" → tracks as initiative.
- **Required endpoints:** All exist. Spider data, HiveMind, initiative creation.

### J6. "Manage decisions that need human input"
- **Intent:** Decision-making — act on boardroom items, review gates, approve experiments
- **Current entry points:**
  - **Web:** Boardroom tab (`/workspace?tab=boardroom`); Governance tab (`/workspace?tab=governance`); Command Center (`/`)
  - **Discord:** `/ask "show boardroom"`, `/decide`
- **Pain points:** Boardroom and Governance overlap significantly — both deal with decisions and policies. Boardroom had 1,586 pending items (now being cleaned up). No way to filter by urgency in the UI.
- **Ideal UX:** Single decision queue sorted by urgency, with quick-action buttons (approve/reject/defer). Governance policies become a settings sub-page, not a tab.
- **Required endpoints:** All exist. `GET /api/boardroom/attention/`, approve/reject actions.

### J7. "Use voice/audio features"
- **Intent:** Listen to agent outputs, manage AI voices, TTS
- **Current entry points:**
  - **Web:** Voices tab (`/workspace?tab=voices`) — 3 sub-tabs (browse, my-voices, earnings); standalone `/voice-marketplace`; ListenButton throughout platform
  - **Discord:** `/voice`, `/speak`, `/ask-voice`, `/voice-chat`, `/voice-market`, `/voice-buy`, `/voice-clone`
- **Pain points:** Voices tab is a marketplace concept that doesn't match current usage (mainly TTS via ListenButton). Discord has 7 voice commands — more voice features than web. Standalone `/voice-marketplace` duplicates the workspace tab.
- **Ideal UX:** Voice is a utility, not a destination. ListenButton is good — the marketplace can be an admin/settings page. Discord voice commands are the real power feature.
- **Required endpoints:** TTS API exists. Voice marketplace APIs exist.

### J8. "See agent details and capabilities"
- **Intent:** Agent management — browse agents, check status, run tasks
- **Current entry points:**
  - **Web:** Sidebar → Agents (`/agents`); AI Consciousness tab (`/workspace?tab=consciousness`) — 8 sub-tabs (memory, orchestra, mood, evolution, relationships, social, capsules, time-travel)
  - **Discord:** `/agents`, `/agent [name]`, `/agent-list`, `/agent-task`
- **Pain points:** AI Consciousness has 8 sub-tabs — the most of any tab — but most are novelty features (mood, social, capsules, time-travel). `/agents` page is the real working surface. Memory Palace is the only high-value sub-tab in consciousness.
- **Ideal UX:** `/agents` page stays as-is. Memory Palace promoted to a standalone tab or merged into Knowledge. Other consciousness sub-tabs demoted to a "Lab" section.
- **Required endpoints:** All exist.

### J9. "Generate and manage creative assets"
- **Intent:** Image/video/audio generation, content channels, ConceptForge dossiers
- **Current entry points:**
  - **Web:** Content Studio → Gallery; Dossiers tab (`/workspace?tab=conceptforge`); Career tab (`/workspace?tab=career`); standalone `/content`, `/content-channels`, `/distribution`
  - **Discord:** `/create`, `/create-content`, `/gallery`, `/series-create`, `/studio-create`
- **Pain points:** Creative assets are spread across Content Studio (gallery), Dossiers (ConceptForge), and 3 standalone pages. Career tab is isolated and unrelated to content. ConceptForge dossiers could logically be inside Content Studio.
- **Ideal UX:** Content Studio absorbs ConceptForge as "Dossiers" sub-tab (already there). Career stays separate but could be a sub-tab under a "Tools" grouping. Remove standalone duplicate pages.
- **Required endpoints:** All exist.

### J10. "Set up Discord server and manage integrations"
- **Intent:** Platform administration — Discord setup, billing, user management
- **Current entry points:**
  - **Web:** Sidebar → Admin (`/admin`); Sidebar → Settings (`/settings`); Infrastructure → Billing sub-tab; standalone `/billing`
  - **Discord:** `/setup`, `/link`, `/unlink`, `/subscribe`, `/tier`, `/cancel`, `/billing`
- **Pain points:** Admin and Settings are separate sidebar items but could be one. Billing is in Infrastructure tab AND as a standalone page. Discord has robust subscription management that web doesn't match.
- **Ideal UX:** Single Admin/Settings page with sub-sections: account, billing, integrations, Discord. Remove standalone `/billing`.
- **Required endpoints:** All exist.

---

## Artifact 2: Surface Map

### Web Surfaces (47 routes)

| # | Route | Feature Area | Tab/Component | Key API Deps | Status | Owner |
|---|-------|-------------|---------------|-------------|--------|-------|
| 1 | `/` | Command Center | `CommandCenterPage` | PA entrypoint, activity, initiatives | CORE | Session 931 |
| 2 | `/workspace` | Modular Hub | `WorkspacePageNew` | Multiple (per tab) | CORE | Session 825 |
| 3 | `/workspace?tab=command` | Conversations | `CommandTab` | HiveMind, conversations | CORE | Session 825 |
| 4 | `/workspace?tab=initiatives` | Project Pipeline | `InitiativesTab` | Initiatives, action items | CORE | Session 847 |
| 5 | `/workspace?tab=boardroom` | Decision Queue | `BoardroomTab` | Boardroom attention API | CORE | Session 927 |
| 6 | `/workspace?tab=content` | Content Studio | `ContentStudioTab` (6 sub-tabs) | Blogs, deliverables, podcast, channels | CORE | Session 825 |
| 7 | `/workspace?tab=governance` | Policies | `GovernanceTab` | Governance API | OVERLAP w/Boardroom | Session 825 |
| 8 | `/workspace?tab=operations` | Agent Output History | `OperationsTab` | Operations API, PDF export | USEFUL | Session 825 |
| 9 | `/workspace?tab=infrastructure` | System Health | `InfrastructureTab` (6 sub-tabs) | Body health, LLM, analytics, billing | OVERLAP w/standalones | Session 825 |
| 10 | `/workspace?tab=orchestration` | Agent Monitoring | `OrchestrationTab` (4 sub-tabs) | Agent monitor, HiveMind, workflows | OVERLAP w/Infra | Session 825 |
| 11 | `/workspace?tab=datasources` | Spider Data | `DataSourcesTab` (3 sub-tabs) | Spiders, spider feed, learning | USEFUL | Session 825 |
| 12 | `/workspace?tab=intelligence` | Reasoning Engine | `IntelligenceTab` (3 sub-tabs) | Reasoning, safety, collective | NICHE | Session 825 |
| 13 | `/workspace?tab=knowledge` | Knowledge Base | `KnowledgeTab` | Knowledge API | USEFUL | Session 825 |
| 14 | `/workspace?tab=files` | File Browser | `FilesTab` | Files API | LOW-VALUE | Session 825 |
| 15 | `/workspace?tab=consciousness` | AI Consciousness | `AIConsciousnessTab` (8 sub-tabs) | Memory, mood, evolution, social | NICHE (except Memory) | Session 825 |
| 16 | `/workspace?tab=triggers` | Autopilot Queue | `TriggersTab` | Triggers API | USEFUL | Session 861B |
| 17 | `/workspace?tab=conceptforge` | ConceptForge Dossiers | `ConceptForgeTab` | Dossier API | USEFUL | Session 865 |
| 18 | `/workspace?tab=career` | ATS Resume Optimizer | `CareerTab` | Career API | NICHE | Session 866 |
| 19 | `/workspace?tab=voices` | Voice Marketplace | `VoiceMarketplaceTab` (3 sub-tabs) | Voice API | NICHE | Session 869 |
| 20 | `/workspace?tab=learning` | Learning Journey | `LearningJourneyTab` (4 sub-tabs) | Learning API | USEFUL | Session 870 |
| 21 | `/agents` | Agent Browser | `AgentsPage` | Agents API | CORE | Sidebar |
| 22 | `/blogs` | Blog List | `BlogsPage` | Self-blog list API | DUPLICATE of Content→Blogs | Session 814 |
| 23 | `/blog/:blogId` | Blog Viewer | `BlogViewerPage` | Self-blog detail + related | CORE (detail) | Session 742 |
| 24 | `/docs-index` | Documentation | `DocsIndexPage` | Docs index API | USEFUL | Sidebar |
| 25 | `/mythology-lab` | Mythology Lab | `MythologyLabPage` | Mythology API | NICHE | Sidebar |
| 26 | `/admin` | Admin Panel | `AdminPage` | Admin APIs | USEFUL | Sidebar |
| 27 | `/settings` | User Settings | `SettingsPage` | Settings API | CORE | Sidebar |
| 28 | `/profile` | User Profile | `ProfilePage` | Profile API | CORE | Sidebar user |
| 29 | `/dashboard` | Legacy Dashboard | `DashboardPage` | Mixed | LEGACY | Pre-825 |
| 30 | `/betting` | Betting | `BettingPage` | Betting API | DORMANT | Commented out |
| 31 | `/legal` | Legal Tools | `LegalPage` | Legal API | DORMANT | Commented out |
| 32 | `/portfolio` | Portfolio | `PortfolioPage` | Portfolio API | DORMANT | Commented out |
| 33 | `/content` | Legacy Content | `ContentPage` | Deliverables | LEGACY duplicate |  |
| 34 | `/podcast` | Legacy Podcast | `PodcastPage` | Podcast API | LEGACY → Content Studio |  |
| 35 | `/content-channels` | Legacy Channels | `ContentChannelsPage` | Channels API | LEGACY → Content Studio |  |
| 36 | `/distribution` | Legacy Distribution | `DistributionPage` | Distribution API | LEGACY → Content Studio |  |
| 37 | `/llm-routing` | LLM Config | `LLMRoutingPage` | LLM routing API | LEGACY → Infra tab |  |
| 38 | `/body-health` | Body Systems | `BodyHealthPage` | Body health API | LEGACY → Infra tab |  |
| 39 | `/hive-mind` | HiveMind | `HiveMindPage` | HiveMind API | LEGACY → Orch tab |  |
| 40 | `/memory-palace` | Memory Palace | `MemoryPalacePage` | Memory API | LEGACY → AI Mind tab |  |
| 41 | `/evolution` | Agent Evolution | `EvolutionPage` | Evolution API | LEGACY → AI Mind tab |  |
| 42 | `/agent-mood` | Agent Mood | `AgentMoodPage` | Mood API | LEGACY → AI Mind tab |  |
| 43 | `/time-capsules` | Time Capsules | `TimeCapsulePage` | Capsules API | LEGACY → AI Mind tab |  |
| 44 | `/time-travel` | Time Travel | `TimeTravelPage` | Time travel API | LEGACY → AI Mind tab |  |
| 45 | `/agent-social` | Agent Social | `AgentSocialPage` | Social API | LEGACY → AI Mind tab |  |
| 46 | `/advisors` | Advisor Browser | `AdvisorsPage` | Advisors API | LEGACY → Command tab |  |
| 47 | `/relationships` | Agent Relationships | `RelationshipsPage` | Relationships API | LEGACY → AI Mind tab |  |
| 48 | `/neural-orchestra` | Neural Orchestra Viz | `NeuralOrchestraPage` | Orchestra API | LEGACY → AI Mind tab |  |
| 49 | `/conversation-contract` | Contracts | `ConversationContractPage` | Contract API | LEGACY → Governance |  |
| 50 | `/spiders` | Spider Browser | `SpiderIntegrationPage` | Spider API | LEGACY → Data tab |  |
| 51 | `/documents` | Document Browser | `DocumentsPage` | Documents API | LEGACY → Content Studio |  |
| 52 | `/voice-marketplace` | Voice Market | `VoiceMarketplacePage` | Voice API | LEGACY → Voices tab |  |
| 53 | `/billing` | Billing Page | `BillingPage` | Billing API | LEGACY → Infra tab |  |
| 54 | `/learning-journey` | Learning Journey | `LearningJourneyPage` | Learning API | LEGACY → Learning tab |  |
| 55 | `/collective` | Collective Intel | `CollectiveIntelligencePage` | Collective API | LEGACY → Intel tab |  |
| 56 | `/analytics` | Analytics Dashboard | `AnalyticsDashboardPage` | Analytics API | LEGACY → Infra tab |  |
| 57 | `/integration-health` | Integration Status | `IntegrationHealthPage` | Integration API | LEGACY → Infra tab |  |
| 58 | `/orchestration` | Orchestration View | `OrchestrationPage` | Orchestration API | LEGACY → Orch tab |  |
| 59 | `/spider-feed` | Spider Feed | `SpiderFeedPage` | Spider feed API | LEGACY → Data tab |  |
| 60 | `/agent-monitor` | Agent Monitor | `AgentMonitorPage` | Agent monitor API | LEGACY → Orch tab |  |
| 61 | `/autonomous` | Autonomous Systems | `AutonomousSystemsPage` | Autonomous API | LEGACY → Orch tab |  |
| 62 | `/reasoning` | Reasoning Engine | `ReasoningEnginePage` | Reasoning API | LEGACY → Intel tab |  |

**Summary:** 62 total routes. ~20 are LEGACY duplicates that already exist as workspace sub-tabs. 7 sidebar items. 18 workspace tabs with 37 sub-tabs = 55 workspace views.

### Discord Surfaces (112 slash commands)

| Group | Commands | Channel | Status |
|-------|----------|---------|--------|
| **System** (3) | `/status`, `/help`, `/setup` | #system-status | ACTIVE |
| **PA/AI** (4) | `/ask`, `/clear`, `/sessions`, `/consult` | DM/thread | ACTIVE |
| **Agents** (4) | `/agents`, `/agent`, `/agent-list`, `/agent-task` | #agent-conversations | ACTIVE |
| **Advisors** (2) | `/consult`, `/advisors` | #agent-conversations | ACTIVE |
| **Research** (3) | `/research`, `/trending`, `/spiders` | #system-status | ACTIVE |
| **Account** (3) | `/link`, `/unlink`, `/profile` | DM | ACTIVE |
| **Betting** (7) | `/odds`, `/arb`, `/bankroll`, `/bet`, `/resolve`, `/futures`, `/slip` | #opportunities | ACTIVE |
| **Predictions** (1) | `/predictions` | #opportunities | ACTIVE |
| **Image** (3) | `/create`, `/gallery`, `/publish-gumroad` | #gallery | ACTIVE |
| **Content Factory** (3) | `/create-content`, `/content-status`, `/showroom` | thread | ACTIVE |
| **Series** (4) | `/series-create`, `/series-status`, `/series-list`, `/series-view` | thread | ACTIVE |
| **Studio Channels** (7) | `/studio-create/list/status/pause/resume/performance/episode` | thread | ACTIVE |
| **Voice** (9) | `/voice`, `/speak`, `/ask-voice`, `/voice-chat`, `/voice-ask`, `/voice-market`, `/voice-buy`, `/voice-clone`, Marketplace browse | voice channel | ACTIVE |
| **Subscription** (4) | `/subscribe`, `/tier`, `/cancel`, `/billing` | DM | ACTIVE |
| **Opportunities** (3) | `/opportunities`, `/apply`, `/track` | #opportunities | ACTIVE |
| **Digest** (2) | `/digest`, `/alerts` | DM | ACTIVE |
| **Blockchain** (3) | `/audit-contract`, `/blockchain-status`, ML scoring | #blockchain-alerts | ACTIVE |
| **Narratives** (10) | `/narratives`, `/narrative-shifts/scan/seed/status/evidence/domains/watch/trending` + list | #system-status | ACTIVE |
| **ROI** (5) | `/roi-summary/dashboard/brief/funnel/attribution` | thread | ACTIVE |
| **Render/Video** (6) | `/resolve-render`, `/color-grade`, `/render-status/download`, `/trending-grades`, `/videos-list` | thread | ACTIVE |
| **Situations** (4) | `/situation-list/status/run/alerts` | thread | ACTIVE |
| **Podcast** (4) | `/podcast-create/list/status/script` | #podcast-library | ACTIVE |
| **Legal** (3) | `/legal-draft/analyze/case` | DM | ACTIVE |
| **Code** (2) | `/code-generate`, `/code-review` | thread | ACTIVE |
| **Reviews** (5) | `/review`, `/review-list`, `/ask-pro`, `/ask-con`, `/decide` | thread | ACTIVE |
| **Clients** (4) | `/client-add/list/deliver/invite` | client channels | ACTIVE |
| **Workflows** (2) | `/workflow-list`, `/workflow-run` | thread | ACTIVE |
| **Learning** (3) | `/rate-series`, `/learning-stats`, `/style-recommend/leaderboard` | thread | ACTIVE |
| **Gumroad** (1) | `/gumroad-status` | DM | ACTIVE |
| **ML Scoring** (1) | `/ml-scoring` | thread | ACTIVE |

### Discord Notification Channels (12)

| Channel | Purpose | Notifications |
|---------|---------|---------------|
| #agent-dreams | Agent dream outputs | `send_dream` |
| #agent-conversations | HiveMind completions | `send_conversation` |
| #system-status | Health, spider summaries | `send_status`, `send_spider_summary` |
| #agent-learning | Learning events | `send_knowledge` |
| #boardroom | Decision notifications | `send_boardroom_decision` |
| #opportunities | High-value signals, market alerts | `send_opportunity`, `send_market_intelligence_brief` |
| #gallery | Generated images | `send_image_to_gallery` |
| #user-profiles | Profile updates | `send_image_dm` (DM) |
| #stock-alerts | Stock audit alerts | `send_stock_alert`, `send_stock_audit_summary` |
| #blockchain-alerts | Chain monitoring | `send_blockchain_alert`, `send_whale_alert`, `send_exploit_alert` |
| #podcast-library | Completed episodes | `send_podcast` |
| DMs | Personal notifications | Link/unlink, subscription, digest |

### PA Tools (90 tools, 17+ intents)

| PA Intent | Maps to UI | Overlap Level |
|-----------|-----------|---------------|
| `boardroom` | Boardroom tab | 90% — PA can do everything the tab does |
| `system_health` | Infrastructure → Health | 80% — PA provides better summary |
| `initiatives` | Initiatives tab | 60% — tab has richer UI (stages, modals) |
| `content_review` | Content Studio → Blogs | 50% — PA lists, UI browses |
| `recent_activity` | Command Center cards | 40% — PA gives real-time, UI is static |
| `error_summary` | (no UI surface) | PA-only |
| `spider_data` | DataSources tab | 40% |
| `agent_operations` | Operations tab, Agents page | 30% |
| `conversations` | Command tab | 30% |
| `surgical_moves` | Orchestration → Monitor | PA-only (status check) |
| `memory_palace` | AI Mind → Memory | 30% |

---

## Artifact 3: Redesign Blueprint

### Design Principles
1. **One place per concern.** If something has a tab AND a standalone page, keep the better one.
2. **3-click max.** Sidebar → tab/page → detail. Never deeper.
3. **PA is the power-user shortcut.** Don't build UI for things the PA handles well.
4. **Discord is notification + quick-action.** Don't try to replicate full UI in Discord.

---

### Phase 0: Instrumentation + Truth Layer (1 PR)

**Goal:** Before reshuffling anything, add telemetry so we can measure what's actually used.

#### PR #A — Tab/Route Telemetry

**File: `frontend/src/hooks/usePageTracking.ts`** (NEW, ~40 lines)
```
- Custom hook wrapping useLocation()
- On every route change: POST /api/v1/telemetry/page-view/
  { route, tab (if workspace), timestamp, session_id }
- Debounce 500ms to avoid rapid tab switching noise
```

**File: `frontend/src/pages/WorkspacePageNew.tsx`**
```
- Import and call usePageTracking() in WorkspacePage component
- Log tab changes via the hook
```

**File: `core/views_telemetry.py`** (NEW, ~30 lines)
```
- Simple view: page_view_api(request)
- Writes to Django cache (Redis) as a lightweight counter
- No new model needed — use Redis hash: page_views:{date}:{route}
```

**File: `core/urls.py`**
```
- Add: path('api/v1/telemetry/page-view/', views_telemetry.page_view_api)
```

**Verification:** Check Redis for page view counts after 24h of usage.

---

### Phase 1: Navigation Reset (2 PRs)

**Goal:** Reduce 18 workspace tabs to 8. Remove 20+ legacy standalone routes. Clean sidebar.

#### PR #B — Consolidate Workspace Tabs (18 → 8)

**Current 18 tabs → Target 8 tabs:**

| Current Tab | Action | Destination |
|-------------|--------|-------------|
| Command | KEEP | Core group |
| Initiatives | KEEP | Core group |
| Boardroom | KEEP (absorb Governance) | Core group |
| Content (6 sub-tabs) | KEEP (absorb ConceptForge as sub-tab) | Content group |
| Governance | MERGE → Boardroom (becomes "Policies" sub-section) | — |
| Operations | KEEP | System group |
| Infrastructure (6 sub-tabs) | MERGE with Orchestration → "System" tab (keep: health, services, LLM, monitor, hivemind, triggers) | — |
| Orchestration (4 sub-tabs) | MERGE → into "System" tab | — |
| Triggers | MERGE → into "System" tab (sub-tab) | — |
| DataSources (3 sub-tabs) | KEEP | Data group |
| Intelligence (3 sub-tabs) | MERGE → DataSources (add "reasoning" sub-tab) | — |
| Knowledge | MERGE → DataSources (add "knowledge" sub-tab) | — |
| Files | MERGE → Content Studio (add "files" sub-tab) | — |
| AI Consciousness (8 sub-tabs) | SHRINK → "Memory" standalone. Rest → Mythology Lab or remove | — |
| ConceptForge | MERGE → Content Studio (already a sub-tab called "Dossiers") | — |
| Career | KEEP as standalone `/career` route, remove from workspace | — |
| Voices | MERGE → Content Studio (add "voices" sub-tab) | — |
| Learning | KEEP | AI group (only tab) |

**Result: 8 tabs in 4 groups:**

```
Core:    [Command] [Initiatives] [Boardroom]
Content: [Content Studio]  (8 sub-tabs: gallery, channels, blogs, docs, podcast, distribution, dossiers, voices)
System:  [Operations] [System]  (System = merged Infra+Orch+Triggers: health, services, LLM, monitor, hivemind, triggers)
Data:    [Data & Intel]  [Learning]  (Data = merged DataSources+Intelligence+Knowledge: spiders, feed, learning, reasoning, collective, knowledge)
```

**File changes:**

**`frontend/src/pages/WorkspacePageNew.tsx`:**
- Update `tabGroups` from 5 groups / 18 tabs to 4 groups / 8 tabs
- Remove imports for: GovernanceTab, IntelligenceTab, KnowledgeTab, FilesTab, AIConsciousnessTab, TriggersTab, ConceptForgeTab, CareerTab, VoiceMarketplaceTab
- Update `WorkspaceTab` type

**`frontend/src/pages/workspace/tabs/BoardroomTab.tsx`:**
- Add governance sub-section (copy policy list from GovernanceTab)

**`frontend/src/pages/workspace/tabs/ContentStudioTab.tsx`:**
- Add sub-tabs: 'dossiers' (from ConceptForgeTab), 'voices' (from VoiceMarketplaceTab), 'files' (from FilesTab)
- Update `ContentSubTab` type

**`frontend/src/pages/workspace/tabs/InfrastructureTab.tsx`** → rename to **`SystemTab.tsx`:**
- Absorb OrchestrationTab sub-tabs (monitor, workflows, automation, hivemind)
- Absorb TriggersTab as sub-tab
- Remove billing and analytics (move to Admin)

**`frontend/src/pages/workspace/tabs/DataSourcesTab.tsx`** → rename to **`DataIntelTab.tsx`:**
- Absorb IntelligenceTab sub-tabs (reasoning, safety, collective)
- Absorb KnowledgeTab content

**`frontend/src/pages/workspace/types.ts`:**
- Update `WorkspaceTab` union type

#### PR #C — Remove Legacy Standalone Routes

**File: `frontend/src/App.tsx`:**
- Remove routes and redirect to workspace equivalents:
  - `/body-health` → `/workspace?tab=system` (sub-tab: health)
  - `/hive-mind` → `/workspace?tab=system` (sub-tab: hivemind)
  - `/memory-palace` → `/workspace?tab=system` (or new Memory page)
  - `/evolution`, `/agent-mood`, `/time-capsules`, `/time-travel`, `/agent-social`, `/relationships`, `/neural-orchestra` → `/mythology-lab`
  - `/conversation-contract` → `/workspace?tab=boardroom`
  - `/spiders`, `/spider-feed` → `/workspace?tab=data`
  - `/documents` → `/workspace?tab=content` (sub-tab: documents)
  - `/content`, `/content-channels`, `/podcast`, `/distribution` → `/workspace?tab=content`
  - `/voice-marketplace` → `/workspace?tab=content` (sub-tab: voices)
  - `/billing` → `/admin`
  - `/llm-routing` → `/workspace?tab=system` (sub-tab: llm)
  - `/integration-health` → `/workspace?tab=system`
  - `/orchestration`, `/agent-monitor`, `/autonomous` → `/workspace?tab=system`
  - `/learning-journey` → `/workspace?tab=learning`
  - `/collective`, `/reasoning` → `/workspace?tab=data`
  - `/analytics` → `/admin`
  - `/dashboard` → `/`
- Keep: `/`, `/workspace`, `/agents`, `/blogs`, `/blog/:id`, `/docs-index`, `/mythology-lab`, `/admin`, `/settings`, `/profile`, `/login`
- All removed routes get `<Navigate to="..." replace />` redirects

**Result:** 62 routes → ~15 active routes + redirects.

**File: `frontend/src/components/layout/Sidebar.tsx`:**
- Simplify to 6 items:
  1. Command Center (`/`)
  2. Workspace (`/workspace`)
  3. Agents (`/agents`)
  4. Docs Index (`/docs-index`)
  5. Admin (`/admin`)
  6. Settings (`/settings`)
- Remove: Mythology Lab (→ AI Mind sub-tab or hide)

---

### Phase 2: Command Center as Default Home (1 PR)

**Goal:** Make `/` the actionable hub — the first thing you see shows what needs attention.

#### PR #D — Enhanced Command Center

**File: `frontend/src/pages/CommandCenterPage.tsx`:**

Add 3 new sections above the existing PA chat:

1. **Attention Queue** (top) — merge boardroom critical items + initiative action items with status=pending
   - Fetch: `GET /api/boardroom/attention/?urgency=critical,high&limit=5` + `GET /api/initiatives/action-items/?status=pending&limit=5`
   - Quick actions: approve/defer/dismiss inline
   - Badge count propagated to sidebar

2. **Active Work** (middle) — currently running conversations, recent blog drafts needing review, triggered situations
   - Fetch: `GET /api/conversations/?status=active&limit=3` + `GET /api/v1/research/self-blog/?status=draft&limit=3`

3. **System Pulse** (compact bar) — health score, active agents, spiders running, recent errors
   - Fetch: single call to a new `GET /api/v1/command-center/pulse/` endpoint

**File: `core/views_command_center.py`** (NEW, ~50 lines):
- `command_center_pulse_api(request)` — aggregates system health, active task count, spider freshness, error count into one response

**File: `core/urls.py`:**
- Add pulse endpoint

---

### Phase 3: Discord Integration Rules (1 PR)

**Goal:** Establish clear rules for what Discord does vs. what the web does. No new Discord commands — just organizational clarity.

#### PR #E — Discord Channel Cleanup + Rules Doc

**File: `docs/DISCORD_INTEGRATION.md`** (NEW):

Document the rules:
1. **Discord IS for:** notifications, quick lookups (`/status`, `/ask`), voice features, mobile-friendly actions (`/bet`, `/apply`)
2. **Discord is NOT for:** complex workflows, content review, initiative management, system configuration
3. **Channel mapping:** document which channels get which notifications and why
4. **Command categories:** mark which commands are ACTIVE, DORMANT, or DEPRECATED

**File: `core/services/discord_bot.py`:**
- Add `@app_commands.command` descriptions that include category tags (no functional changes)
- Group the help command output by category for discoverability

**No functional changes to Discord bot.** The 112 commands stay — they work. The issue isn't Discord bloat, it's web bloat. Discord is actually well-organized with slash command autocomplete.

---

### Implementation Priority

| PR | Name | Effort | Impact | Dependencies |
|----|------|--------|--------|-------------|
| A | Tab Telemetry | Small (4 files) | Foundation | None |
| B | Consolidate Tabs (18→8) | Large (10+ files) | HIGH — fixes the core UX issue | None |
| C | Remove Legacy Routes | Medium (2 files) | HIGH — eliminates confusion | After B |
| D | Enhanced Command Center | Medium (3 files) | HIGH — makes home useful | After B |
| E | Discord Rules Doc | Small (2 files) | LOW — documentation only | None |

**Recommended order:** A → B → C → D → E

A and E can be done in parallel. B is the critical path. C and D depend on B.

---

### What This Does NOT Change
- **Backend APIs** — zero endpoint changes (except telemetry + pulse, both new)
- **PA tools** — unchanged, PA is already well-organized
- **Discord bot** — 112 commands stay, just documented
- **Agent system** — untouched
- **Celery tasks** — untouched
- **Database** — zero migrations

### Expected Outcomes
- **Workspace tabs:** 18 → 8 (56% reduction)
- **Total routes:** 62 → ~15 active + redirects (76% reduction in discoverable routes)
- **Sub-tab depth:** worst case drops from 8 (AI Consciousness) to 6 (Content Studio or System)
- **Navigation depth:** sidebar (6 items) → workspace (8 tabs) → sub-tab → detail = still 3 levels max
- **User confusion:** eliminated — one place per concern, no duplicate surfaces
