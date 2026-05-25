# UI Inventory & Documentation

**Last Updated:** January 18, 2026 - Session 775
**Frontend Stack:** React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
**Total Lines:** 51,512 (all frontend source)

---

## Summary Stats

| Metric | Count |
|--------|-------|
| **Total Pages** | 43 |
| **Total Tabs** | ~85 |
| **Total Modals/Dialogs** | ~65 |
| **Total Components** | 11 |
| **Lines of TSX (pages)** | 45,678 |
| **Lines of TS (lib/stores/hooks)** | 5,834 |
| **Total Frontend Source** | 51,512 |
| **API Endpoints Used** | 55+ |

### Non-Page Source Files

| File | Lines | Purpose |
|------|-------|---------|
| `lib/api.ts` | 2,251 | API client (55+ endpoints) |
| `stores/unifiedStore.ts` | 426 | Unified state store |
| `components/HeartWidget.tsx` | 420 | Body systems widget |
| `hooks/useWebSocket.ts` | 416 | WebSocket hook |
| `components/DiagnosticPanel.tsx` | 376 | Diagnostic display |
| `components/EntityLink.tsx` | 349 | Entity navigation links |
| `stores/bodyStore.ts` | 318 | Body systems state |
| `components/Breadcrumb.tsx` | 223 | Navigation breadcrumbs |
| `components/GlobalAlertBanner.tsx` | 209 | Alert notifications |
| `services/bodyGovernance.ts` | 191 | Body governance service |
| `components/layout/Sidebar.tsx` | 183 | Navigation sidebar |
| `stores/navigationStore.ts` | 144 | Navigation state |
| `App.tsx` | 119 | App root component |
| Other files | ~200 | Various utilities |

---

## Pages (43 Total)

### Core Dashboard & Navigation

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `DashboardPage` | ~500 | 0 | 0 | Main landing dashboard with widgets |
| `HumanPage` | 1,926 | 6 | 2 | Human-in-the-loop control center |
| `ProfilePage` | ~300 | 0 | 0 | User profile management |
| `SettingsPage` | ~400 | 0 | 3 | Application settings |
| `LoginPage` | ~200 | 0 | 0 | Authentication |

### AI Agents & Orchestration

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `AgentsPage` | 4,910 | 8 | 11 | Agent management, activity, dreams, conversations |
| `OrchestrationPage` | 2,948 | 4 | 7 | Multi-agent workflow orchestration |
| `NeuralOrchestraPage` | 1,116 | 0 | 1 | Real-time agent activity visualization |
| `AdvisorsPage` | ~600 | 0 | 1 | 25 legendary advisors (Buffett, etc.) |
| `HiveMindPage` | 688 | 0 | 2 | Collective agent decision-making |

### Intelligence & Memory

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `IntelligencePage` | 3,546 | 4 | 6 | Gates, pilots, opportunities, predictions |
| `MemoryPalacePage` | 2,964 | 4 | 5 | Agent memories, clusters, connections |
| `CollectiveIntelligencePage` | ~800 | 5 | 1 | Team insights, knowledge network |
| `ReasoningEnginePage` | ~600 | 4 | 1 | ThinkingAgent visualization |

### Content Creation

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `ContentPage` | ~700 | 4 | 1 | Gallery, calendar, projects, templates |
| `PodcastPage` | ~900 | 4 | 0 | Podcast generation and management |
| `BlogViewerPage` | ~400 | 0 | 0 | View generated blog content |
| `ContentChannelsPage` | ~500 | 0 | 1 | Autonomous content channels (3 channels, 91 episodes) |
| `VoiceMarketplacePage` | ~600 | 4 | 0 | Trained voice marketplace |

### Sci-Fi Features (14 Total)

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `EvolutionPage` | ~500 | 0 | 1 | Agent evolution and adaptation |
| `TimeTravelPage` | ~700 | 0 | 2 | Decision replay and what-if analysis |
| `TimeCapsulePage` | ~600 | 0 | 3 | Future message capsules |
| `AgentMoodPage` | ~500 | 2 | 2 | Agent emotional states |
| `AgentSocialPage` | ~600 | 0 | 2 | Agent social interactions |
| `RelationshipsPage` | ~500 | 0 | 2 | Agent relationship mapping |
| `MythologyLabPage` | ~700 | 4 | 0 | Hallucination detection |
| `ConversationContractPage` | ~500 | 0 | 1 | Conversation quality contracts |
| `SpiderIntegrationPage` | ~450 | 0 | 0 | Spider network visualization |

### Body Systems

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `BodyHealthPage` | ~800 | 0 | 2 | 9 body systems health monitoring |

### Analytics & Monitoring

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `AnalyticsDashboardPage` | ~1,200 | 8 | 0 | Charts, insights, reports |
| `IntegrationHealthPage` | ~600 | 0 | 0 | System integration status |
| `AdminPage` | ~900 | 5 | 0 | Heart, health, celery, spiders, agents |

### Betting & Finance

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `BettingPage` | ~1,500 | 7 | 2 | Sports betting analytics |
| `PortfolioPage` | ~700 | 5 | 1 | Content portfolio management |

### System & Configuration

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `LLMRoutingPage` | ~800 | 7 | 0 | LLM provider/model configuration |
| `AutonomousSystemsPage` | ~700 | 5 | 0 | Situation triggers and automation |
| `WorkspacePage` | ~900 | 6 | 4 | Project workspace management |

### Legal & Documents

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `LegalPage` | ~600 | 5 | 0 | Legal document management |
| `DocumentsPage` | ~400 | 0 | 0 | Document browser |

### Commerce & Billing

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `BillingPage` | ~500 | 4 | 1 | Subscription and payment |
| `DistributionPage` | ~700 | 6 | 0 | Content distribution |
| `LearningJourneyPage` | ~600 | 4 | 1 | Learning paths and achievements |

### Assistant

| Page | Lines | Tabs | Modals | Description |
|------|-------|------|--------|-------------|
| `AssistantPage` | ~800 | 1 | 0 | Personal AI assistant chat |

---

## Tabs by Page (~85 Total)

### High Tab Count Pages

| Page | Tab Count | Tab Names |
|------|-----------|-----------|
| **AnalyticsDashboardPage** | 8 | overview, charts, insights, reports, agent-activity, revenue, content, system-health |
| **AgentsPage** | 8 | overview, activity, dreams, conversations, decisions, experiments, tools, monitoring |
| **BettingPage** | 7 | overview, arbitrage, watching, markets, odds, bankroll, wagers |
| **LLMRoutingPage** | 7 | overview, providers, models, agents, logs, analytics |
| **HumanPage** | 6 | attention, control, pending, verified, watching, preferences |
| **WorkspacePage** | 6 | overview, files, git, operations, reviews |
| **DistributionPage** | 5 | overview, platforms, content, revenue, scheduled |
| **AdminPage** | 5 | heart, health, celery, spiders, agents |
| **AutonomousSystemsPage** | 5 | overview, situations, triggers, analytics |
| **CollectiveIntelligencePage** | 5 | insights, teams, knowledge, network, messages |
| **LegalPage** | 5 | overview, documents, cases, litigation |
| **PortfolioPage** | 5 | overview, platforms, content, revenue |

### Medium Tab Count Pages

| Page | Tab Count | Tab Names |
|------|-----------|-----------|
| **OrchestrationPage** | 4 | workflows, executions, create, agents |
| **ContentPage** | 4 | gallery, calendar, projects, templates |
| **LearningJourneyPage** | 4 | active, templates, completed, achievements |
| **PodcastPage** | 4 | overview, episodes, generate |
| **VoiceMarketplacePage** | 4 | browse, my-voices, purchases, earnings |
| **BillingPage** | 4 | subscription, payment-methods, invoices, usage |
| **ReasoningEnginePage** | 4 | dashboard, thoughts, actions, concerns |
| **MythologyLabPage** | 4 | (various) |
| **MemoryPalacePage** | 4 | memories, clusters, connections, analytics |
| **IntelligencePage** | 4 | gates, pilots, opportunities, predictions |

---

## Modals & Dialogs (~65 Total)

### Pages with Most Modals

| Page | Modal Count | Modal Types |
|------|-------------|-------------|
| **AgentsPage** | 11 | Agent detail, execution history, dream detail, conversation view, decision detail, experiment config, tool detail, activity detail |
| **OrchestrationPage** | 7 | Workflow create, workflow edit, step config, execution detail, step intelligence, approval gate, output viewer |
| **IntelligencePage** | 6 | Gate detail, pilot review, opportunity detail, prediction detail, implementation review, gate checklist |
| **MemoryPalacePage** | 5 | Memory detail, cluster view, connection explorer, evolution timeline, memory search |
| **WorkspacePage** | 4 | File preview, git diff, operation detail, review modal |
| **SettingsPage** | 3 | API key config, preference editor, confirmation dialogs |
| **TimeCapsulePage** | 3 | Create capsule, view capsule, unlock capsule |

### Common Modal Patterns

| Pattern | Used In | Description |
|---------|---------|-------------|
| **Detail View** | Most pages | Click item to see full details |
| **Create/Edit Form** | OrchestrationPage, ContentPage | Multi-step forms |
| **Confirmation** | SettingsPage, WorkspacePage | Destructive action confirmation |
| **Intelligence Panel** | OrchestrationPage, IntelligencePage | Step-by-step execution details |

---

## Components (11 Total)

### Layout Components (3)

| Component | Purpose |
|-----------|---------|
| `Layout.tsx` | Main app layout wrapper |
| `Header.tsx` | Top navigation bar |
| `Sidebar.tsx` | Left navigation sidebar |

### Custom Components (5)

| Component | Purpose |
|-----------|---------|
| `HeartWidget.tsx` | Body system health indicator (used on multiple pages) |
| `Breadcrumb.tsx` | Navigation breadcrumbs |
| `DiagnosticPanel.tsx` | System diagnostic display |
| `EntityLink.tsx` | Clickable links to entities (agents, workflows, etc.) |
| `GlobalAlertBanner.tsx` | System-wide alert notifications |

### UI Library (shadcn/ui)

The project uses shadcn/ui components imported as needed:
- Button, Card, Dialog, Tabs, Input, Select, Badge, Avatar, Tooltip, etc.

---

## Frontend Architecture

```
frontend/src/
├── App.tsx                 # Router and app structure (6,770 lines)
├── main.tsx               # Entry point
├── index.css              # Global styles (Tailwind)
├── pages/                 # 43 page components (45,678 lines)
│   ├── AgentsPage.tsx     # Largest (4,910 lines)
│   ├── IntelligencePage.tsx
│   ├── MemoryPalacePage.tsx
│   └── ...
├── components/            # Reusable components
│   ├── layout/           # Layout components
│   │   ├── Header.tsx
│   │   ├── Layout.tsx
│   │   └── Sidebar.tsx
│   ├── ui/               # shadcn/ui components
│   ├── HeartWidget.tsx
│   ├── Breadcrumb.tsx
│   └── ...
├── lib/
│   └── api.ts            # API client (6,800+ lines, 55+ endpoints)
├── stores/               # Zustand state stores
│   ├── authStore.ts
│   ├── settingsStore.ts
│   └── ...
├── hooks/                # Custom React hooks
│   └── useWebSocket.ts
└── services/             # Service utilities
```

---

## API Integration

### API Client (`lib/api.ts`)

The API client provides typed access to 55+ backend endpoints:

| Category | Endpoints | Example |
|----------|-----------|---------|
| **Agents** | 15+ | `agentsApi.list()`, `agentsApi.execute()` |
| **Orchestration** | 10+ | `orchestrationApi.getWorkflows()`, `orchestrationApi.execute()` |
| **Intelligence** | 8+ | `intelligenceApi.getGates()`, `intelligenceApi.getPilots()` |
| **Memory** | 6+ | `memoryApi.getMemories()`, `memoryApi.getClusters()` |
| **Analytics** | 14+ | `analyticsApi.getCharts()`, `analyticsApi.getInsights()` |
| **Body Systems** | 9+ | `bodyApi.getHeartStatus()`, `bodyApi.getLungsStatus()` |
| **Dashboard** | 4+ | `dashboardApi.getSummary()`, `dashboardApi.getStats()` |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend                                   │
├─────────────────────────────────────────────────────────────────────┤
│  Pages (43)                                                          │
│  └── Use React Query for data fetching                              │
│      └── Call api.ts typed endpoints                                │
│          └── HTTP requests to Django backend                        │
├─────────────────────────────────────────────────────────────────────┤
│  State Management                                                    │
│  ├── React Query (server state, caching)                            │
│  ├── Zustand stores (client state)                                  │
│  └── URL params (navigation state)                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Real-time Updates                                                   │
│  └── WebSocket connection to /system-events                         │
│      └── Invalidates React Query cache on events                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Page Categories

### By Complexity

| Tier | Pages | Characteristics |
|------|-------|-----------------|
| **Complex** (2,000+ lines) | AgentsPage, IntelligencePage, MemoryPalacePage, OrchestrationPage | Multiple tabs, many modals, complex state |
| **Medium** (800-2,000 lines) | HumanPage, BettingPage, AnalyticsDashboardPage, NeuralOrchestraPage | Some tabs, few modals |
| **Simple** (<800 lines) | Most other pages | Single view or few tabs |

### By Feature Area

| Area | Pages | Purpose |
|------|-------|---------|
| **Agent Management** | AgentsPage, AdvisorsPage, NeuralOrchestraPage | Manage and monitor AI agents |
| **Workflow** | OrchestrationPage, HiveMindPage, WorkspacePage | Multi-agent workflows |
| **Intelligence** | IntelligencePage, MemoryPalacePage, CollectiveIntelligencePage | Knowledge and decision systems |
| **Content** | ContentPage, PodcastPage, BlogViewerPage, ContentChannelsPage | Content creation and management |
| **Sci-Fi** | 9 pages | Advanced AI features |
| **System** | AdminPage, AnalyticsDashboardPage, BodyHealthPage | System monitoring |
| **Commerce** | BillingPage, VoiceMarketplacePage, DistributionPage | Monetization |

---

## Design Patterns

### Common UI Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| **Tab Navigation** | 17 pages | `useState<TabType>` with tab array |
| **Detail Modal** | 26 pages | Click row/card to open detail view |
| **Data Grid** | Most pages | Paginated tables with sorting |
| **Stats Cards** | Dashboard, Analytics | KPI display with icons |
| **Timeline** | OrchestrationPage, EvolutionPage | Chronological event display |
| **Tree View** | MemoryPalacePage, WorkspacePage | Hierarchical data |

### State Patterns

```typescript
// Tab state
const [activeTab, setActiveTab] = useState<TabType>('overview')

// Modal state
const [selectedItem, setSelectedItem] = useState<Item | null>(null)

// React Query for data
const { data, isLoading } = useQuery({
  queryKey: ['items'],
  queryFn: () => api.getItems()
})

// Mutations
const mutation = useMutation({
  mutationFn: api.createItem,
  onSuccess: () => queryClient.invalidateQueries(['items'])
})
```

---

## File Locations

| Type | Path |
|------|------|
| Pages | `frontend/src/pages/*.tsx` |
| Components | `frontend/src/components/*.tsx` |
| Layout | `frontend/src/components/layout/*.tsx` |
| API Client | `frontend/src/lib/api.ts` |
| Stores | `frontend/src/stores/*.ts` |
| Hooks | `frontend/src/hooks/*.ts` |
| Types | `frontend/src/types/*.ts` |
| Styles | `frontend/src/index.css` |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| `docs/UI_COMPREHENSIVE_AUDIT.md` | Deep audit of all pages and API connections |
| `docs/ARCHITECTURE.md` | System architecture overview |
| `docs/AGENTS.md` | Agent documentation (72 agents) |
| `docs/SCIFI_FEATURES.md` | 14 Sci-Fi feature documentation |
| `CLAUDE.md` | Session entry point with quick reference |

---

*Generated: Session 775 - January 18, 2026*
