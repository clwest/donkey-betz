# Dossier #11: Frontend + Workspace System

**Audited:** April 6, 2026
**Status:** WORKING — React 18 + Vite, 23 workspace tabs, 9 embedded apps

---

## 1. Purpose

The frontend is a React single-page application that provides the workspace-based UI for all platform features. Workspaces are the organizational unit — each represents a project, business unit, or app with its own deliverables, content, agents, and operations. Nine standalone apps embed inside workspaces via iframe.

## 2. Tech Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| React | 18.2.0 | UI framework |
| Vite | 5.0.0 | Build tooling |
| Tailwind CSS | 3.4.0 | Styling |
| Zustand | 4.4.0 | State management (6 stores) |
| TanStack React Query | 5.0.0 | Data fetching + caching |
| Axios | 1.6.0 | HTTP client |
| React Router | 6.20.0 | Routing (35+ routes) |
| Lucide React | — | Icon library |
| react-markdown | 10.1.0 | Markdown rendering |
| jsPDF | 4.0.0 | PDF export |

## 3. Workspace Architecture

### ProjectWorkspace Model (`core/models_skin_layer.py`)

**4 workspace types:** local, git_remote, sandbox, container

**Key fields:**
- Identity: id(UUID), user(FK), name, description
- Location: workspace_type, root_path, git_remote_url
- Tech: tech_stack(JSON), entry_points(JSON)
- Permissions: allow_file_write, allow_file_delete, allow_command_execution, allow_git_operations, protected_paths, require_human_review
- State: is_active (unique constraint per user), current_branch
- Stats: total_operations, total_files_written, total_commits

### WorkspaceContext Model (Scanned Project Understanding)

Populated by scanning the actual project directory:
- file_tree, key_files (main_entry, routes, api_client, models)
- coding_patterns (component naming, hooks, API patterns, tests)
- dependencies (frontend + backend with versions)
- import_aliases (@/components → src/components)
- directory_purposes (what each dir contains)
- total_files, total_directories, total_lines_of_code, file_type_counts
- last_scanned_at, scan_depth, scan_duration_ms

### WorkspaceOperation Model (Agent Output Tracking)

13 operation types: file_create, file_modify, file_delete, file_rename, command_exec, git_commit, git_branch, git_checkout, git_merge, build_run, test_run, lint_run, deploy

Before/after state stored per operation — enables rollback and learning.

## 4. Tab Structure (23 Total)

| Primary Tab | Sub-tabs |
|---|---|
| **Home** | (none — dashboard with pulse cards, attention queue, initiatives) |
| **Work** (3) | Queue, Deliverables, Initiatives |
| **Build** (4) | Content Studio (6 internal tabs), Campaigns, Voices, ConceptForge |
| **Intelligence** (3) | Data & Intel, Knowledge, AI Mind |
| **System** (13) | Operations, Incidents, Alerts, Governance, Autopilot, Cost, Queues, Config, Audit Log, Automations, Quality, Files, Git |

Plus: **Launch App** tab appears for workspaces with embedded apps.

## 5. Embedded Apps (9 via iframe)

| App | Frontend Port | Backend Port | Description |
|-----|--------------|-------------|-------------|
| SellerPilot | 5177 | 8005 | E-commerce listing optimizer |
| MentorForge | 5174 | 8002 | AI mentoring (12 personas) |
| SignalStudio | 5173 | 8003 | Market trend intelligence |
| Contract Concierge | 5175 | 8010 | Contract drafting/review |
| PitchDeckForge | 5176 | 8004 | Investor pitch decks |
| DealFlowTracker | 5178 | 8006 | Deal pipeline CRM |
| ScoutPlays | 5179 | 8007 | Sports player scouting |
| ComplianceSentinel | 5180 | 8008 | Regulatory monitoring |
| Ironwood Protocol | 5181 | 8009 | Sci-fi RTS game |

Each has refresh, fullscreen toggle, and external link controls. App detection via workspace name matching in `AppTab.tsx`.

## 6. State Management (6 Zustand Stores)

- **authStore** — user auth state, login/logout
- **paStore** — PA conversations, dock open/close
- **workspaceStore** — active workspace context (id, name, type)
- **navigationStore** — current route state
- **assistantContextStore** — focused entity for PA context
- **bodyStore** — legacy body system state

## 7. Current Status: WORKING

**Operational:** Full workspace UI with 23 tabs, 9 embedded apps, PA integration, deliverable library, initiative tracking, content studio.

**Fixed this session:** Home tab workspace scoping, Build tab empty states, Content Studio sub-tab dedup, TypeScript errors cleaned up.

## 8. Truth Gaps

- ~~Bundle size~~: **RESOLVED** — 5.6MB total JS (2 main chunks ~2.6MB each + html2canvas 200KB). Needs code splitting.
- ~~WebSocket usage~~: **RESOLVED** — 110 WebSocket paths defined in routing.py. Many are duplicates or legacy. Significant cleanup needed.
- **Tab completeness**: CONFIRMED — several tabs show empty/mock data (verified in today's Build tab audit)
- **Mobile responsiveness**: DESIGN QUESTION — not audited, would need device testing
- **Offline capability**: CONFIRMED — none, fully server-dependent (by design)
