# Half-Built Features Audit

**Date:** April 8, 2026
**Trigger:** During legacy PA cleanup, discovered `get_coleadership_opinion()` was called but never defined (always silently failed). This audit checks for similar issues across the entire platform.

---

## Executive Summary

| Category | Count | Severity |
|----------|-------|----------|
| Silent method failures (called but undefined) | 2 critical, 10+ high | CRITICAL |
| Dead API endpoints (backend exists, frontend never calls) | ~75 | MEDIUM |
| Orphaned Celery tasks | 3 dead + 4 blocked | LOW |
| Frontend stubs / "Coming Soon" | 6+ actions | MEDIUM |
| Hidden pages (routed but not in nav) | 14 pages | LOW |
| Frontend mock data / stale hardcoded values | 2 pages | MEDIUM |

---

## 1. CRITICAL: Silent Method Failures

Methods called on objects but never defined on the class. Always fail silently inside try/except blocks. Nobody notices.

### 1a. Image/Video Tracking (BROKEN)

**Files:** `core/views_video.py:761`, `core/views_image_gallery.py:492`

```
assistant.track_generated_image()   # NOT defined on PersonalAIAssistant
assistant.track_generated_video()   # NOT defined on PersonalAIAssistant
```

These methods exist on `EPAUtilityMixin` but NOT on `PersonalAIAssistant`. The cached `assistant_{user.id}` object may be the wrong type. Both wrapped in `try/except Exception` that swallows the `AttributeError`.

**Impact:** Image/video tracking for intelligent chaining never works. Features depending on tracking history operate without data.

**Fix:** Move `track_generated_image()` and `track_generated_video()` to a standalone utility, or call the ImageHistory/VideoHistory models directly.

### 1b. Broad `except: pass` in Critical Services

100+ instances across `core/services/`. Worst offenders:

| File | Line | What's Swallowed |
|------|------|-----------------|
| `agent_llm_router.py` | 237, 252, 270, 285, 471, 496 | Provider health, category lookup, tool support, budget check, tracking, config save |
| `agent_monitoring.py` | 239, 358 | Execution metrics lost, agent stats incomplete |
| `initiative_integration_service.py` | 603 | Health check silently skipped — blocked initiatives appear healthy |
| `knowledge_first_router.py` | 223 | Search freshness scoring defaults to 24h old on any error |
| `experiment_learning_enhancer.py` | 319 | Risk calculation excludes experiments with bad data |

**Fix:** Replace `except: pass` with specific exception types + `logger.warning()`.

---

## 2. Dead API Endpoints (~75 endpoints)

Backend endpoints wired in `urls.py` that the frontend NEVER calls:

### Verification/Testing System (7 endpoints)
- `api/verify/start/`, `api/verify/baseline/`, `api/verify/expose/`, `api/verify/post-learning/`, `api/verify/status/`, `api/verify/sessions/`, `api/verify/demo/`
- Full verification testing framework built but never connected to UI

### Monitoring/Health System (11 endpoints)
- `api/monitoring/health/`, `api/monitoring/content-studio/`, `api/monitoring/narrative-drift/`, `api/monitoring/market-intelligence/`, `api/monitoring/roi/`, `api/monitoring/provenance/`, `api/monitoring/activity/`, `api/monitoring/schedules/`, `api/monitoring/ml-scoring/` (+ train + explanation)
- Complete monitoring dashboard backend with no frontend

### A/B Testing System (8 endpoints)
- `api/ab-testing/tests/` (list, create, detail, start, pause, complete, results, variants)
- Full experiment management API — zero frontend

### Body Systems Status (10 endpoints)
- `api/heart/status/`, `api/lungs/status/`, `api/circulatory/status/`, `api/spine/status/`, `api/immune/status/`, `api/digestive/status/`, `api/muscular/status/`, `api/brain/status/`, `api/skin/status/`, `api/nervous/status/`
- Individual body system endpoints — frontend uses unified `api/body/vitals/` instead

### Legacy Unified Assistant (6 endpoints)
- `api/unified/chat/`, `api/unified/context/`, `api/unified/execute-agent/`, `api/unified/recommendations/`, `api/unified/rate/`
- Replaced by Rigby (`api/pa/chat/`)

### Other Dead Endpoints (~33)
- Agent testing/debugging, spider diagnostics, partnership health, session status, dashboard health, learning status (various), interview status, LLM routing status, etc.

---

## 3. Orphaned Celery Tasks

### Truly Dead (3 tasks)
All in `core/tasks_preview.py`:
- `cleanup_expired_preview_environments` — never dispatched, not in Beat schedule
- `destroy_preview_provider_resources` — never dispatched
- `vip_exchange_smoke_test` — never dispatched

### Intentionally Blocked (4 tasks)
In `core/tasks.py` — disabled Session 1031 (audit parsing was burning $9/day):
- `discover_and_import_audits`
- `assign_open_findings_to_agents`
- `execute_remediation_tasks`
- `run_autonomous_remediation_cycle`

---

## 4. Frontend Stubs and "Coming Soon"

### ContentPage Actions That Don't Work
**File:** `frontend/src/pages/ContentPage.tsx:376`

Buttons render and appear clickable but show "Coming soon!" toast:
- Edit (image)
- Upscale (image)
- Voice Clone (audio)
- Music Generate (audio)
- Text to 3D
- Image to 3D

### Dream Reactions Don't Persist
**File:** `frontend/src/pages/AgentsPage.tsx:3220`

Comment: `// TODO: Call dreamsApi.react when implemented`
Emoji reaction buttons render but only log to console.

### Governance Redirect Points to Wrong Tab
`/governance` redirects to `/workspace?tab=boardroom` — should be `?tab=system`

---

## 5. Hidden Pages (14 routed but not in sidebar)

These pages are fully functional but not accessible from the sidebar navigation:

| Route | Page | Notes |
|-------|------|-------|
| `/dashboard` | DashboardPage | Hidden from nav |
| `/intelligence` | IntelligencePage | Hidden from nav |
| `/content` | ContentPage | Hidden from nav |
| `/legal` | LegalPage | Hidden from nav |
| `/portfolio` | PortfolioPage | Hidden from nav |
| `/advisors` | AdvisorsPage | Fully functional, not in sidebar |
| `/neural-orchestra` | NeuralOrchestraPage | Fully functional, not in sidebar |
| `/conversation-contract` | ConversationContractPage | Not in sidebar |
| `/mythology-lab` | MythologyLabPage | Not in sidebar |
| `/analytics` | AnalyticsDashboardPage | Not in sidebar |
| `/docs-index` | DocsIndexPage | Not in sidebar |
| `/projects` | ProjectsPage | Not in sidebar |
| `/how-it-works` | HowItWorksPage | Not in sidebar |
| `/deliverables` | DeliverablesPage | 12-line stub wrapper |

**Note:** Some of these may be intentionally hidden (consolidated into workspace tabs). But Advisors, Neural Orchestra, and Analytics being hidden seems like an oversight.

---

## 6. Frontend Mock/Stale Data

### Neural Orchestra Mock Data Badge
**File:** `frontend/src/pages/NeuralOrchestraPage.tsx:881-886`
- Page displays yellow "Mock Data" badge when backend returns `mock_data: true`
- Indicates backend sometimes serves fake data

### How It Works Page — Hardcoded Stats
**File:** `frontend/src/pages/HowItWorksPage.tsx:56-62`
- Static values: "218 Agents", "79 Spiders", "25 Advisors"
- Never fetched from API — will be permanently stale

### 25 Legacy Cockpit Pages
**Directory:** `frontend/src/pages/cockpit/`
- All redirected to workspace tabs — code still exists but routes are dead
- ~25 .tsx files of dead code

---

## Recommended Priority

### Do Now (breaks user experience)
1. Fix `track_generated_image()` / `track_generated_video()` — image/video chaining is silently broken
2. Fix governance redirect (`boardroom` → correct tab)
3. Remove or disable "Coming Soon" content actions that confuse users

### Do Soon (tech debt / reliability)
4. Add `logger.warning()` to the worst `except: pass` blocks (agent_llm_router, agent_monitoring, initiative_integration)
5. Delete the 3 orphaned preview tasks
6. Delete the 25 cockpit page files
7. Make HowItWorksPage stats dynamic

### Do Later (cleanup)
8. Audit all ~75 dead endpoints — delete or document which are intentionally for internal/ops use
9. Decide which hidden pages should be in sidebar nav
10. Replace broad `except:` with specific exception types across services
