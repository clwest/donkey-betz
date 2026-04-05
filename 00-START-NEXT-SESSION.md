# Next Session — Start Here

**Date:** April 5, 2026
**Previous Session:** UI Overhaul + PA Identity Fix + Data Flow Hardening
**PA Conversation:** pa-09efe1c2b63f
**Status:** 218 Agents | 80 Spiders | 25 Advisors | PA function calling LIVE (GPT-5.2) | 9 standalone apps + RTS game

---

## What Was Done This Session

### UI Overhaul — Cockpit Consolidated into Workspace (3 phases)
1. **Phase 1: Hide Cockpit** — removed from sidebar, all `/cockpit/*` routes redirect to Workspace tabs
2. **Phase 2: Migrate 8 features** — 7 new System sub-tabs (Incidents, Alerts, Autopilot, Cost, Queues, Config, Audit Log) + Inbox on Home tab
3. **Phase 3: Fix links** — inline Incident Detail view, AlertsPage routes updated, Inbox CTA rewriter
4. All cockpit code preserved in `pages/cockpit/` — not deleted

### PA Identity Consolidation
1. **Found 6 identity variants** — PersonalAssistant, PersonalAssistantAgent, UnifiedPA, personal_assistant, PA, human_pa
2. **Created `core/services/pa_identity.py`** with `PA_IDENTITY` constant
3. **Updated 12 code locations** across 8 service files to use the constant
4. **Built `migrate_pa_identity` management command** — audits and normalizes all DB records
5. **Run on Railway pending** — `railway run python manage.py migrate_pa_identity --apply`

### Data Flow Hardening
1. **16 agents fixed** — `create_deliverable_on_schedule` flipped from False to True. Scheduled agent outputs now create Deliverables instead of vanishing.
2. **ConversationActionDispatcher** — now stores dispatched task references in conversation metadata
3. **DeliverableFactory created** — `core/services/deliverable_factory.py` for centralized Deliverable creation
4. **Orphan model audit** — SkillGapAnalysis (1,466 rows) and ViralContentPrediction (5,351 rows) contain real data never shown to users

### Audit Documents Created
- `docs/audits/PA_IDENTITY_FRAGMENTATION_AUDIT.md`
- `docs/audits/DATA_FLOW_DEAD_ENDS_AUDIT.md`

### Initiatives Created (tracked by Rigby)
- **PA Identity Consolidation** (c7b6088f) — High priority
- **Data Flow Hardening** (42079067) — Critical priority

## Accounts

- `donkeyking` (Chris) — superuser/owner (Railway username: `admin`)
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer

## PRIORITY 1: Run PA Identity Migration on Railway

```bash
# Dry run first
railway run python manage.py migrate_pa_identity --verbose

# Then apply
railway run python manage.py migrate_pa_identity --apply
```

## PRIORITY 2: Remaining Data Flow Work

### DeliverableFactory Migration (Next Sprint)
- Factory exists at `core/services/deliverable_factory.py`
- 23 existing `Deliverable.objects.create()` call sites need to migrate
- Start with highest-traffic paths: base_agent.py, tool_dispatcher handlers, tasks_conversations.py

### Orphan Models — Surface or Remove
| Model | Rows | Action |
|---|---|---|
| ViralContentPrediction | 5,351 | Surface in Intelligence tab |
| SkillGapAnalysis | 1,466 | Surface in Intelligence tab |
| CaseLawUpdate | 0 | Remove model |
| RegulatoryChange | 0 | Remove model |
| EarningsPrediction | 0 | Remove model |
| ThumbnailVariant | 77 | Low priority |

### Spider Pipeline Documentation
- SpiderData → bridges → connectors → final tables flow is undocumented
- Complex multi-hop pipeline could silently lose data

## PRIORITY 3: Ironwood Protocol Polish
- Playtest campaign missions 2-6
- AI balance tuning
- Resize sprites for production (WebP variants)

## PRIORITY 4: Platform Carryover
- Content Packets UI — packet detail page
- Duplicate dispatch rate limiting
- Evidence Cards monitoring

## Known Issues

### Workspace System
- `unique_active_workspace_per_user` DB constraint: only 1 workspace can be `is_active=True` per user
- ProjectWorkspace.save() deactivates all others when activating one

### Cockpit Migration
- Internal links in dormant cockpit pages still reference `/cockpit/*` (not rendered, no runtime risk)
- Cockpit backend API endpoints (`/cockpit/*`) still live — needed by migrated workspace tabs
- CreateFlow/CreateHub and ObsPage skipped (zero usage in 90 days)

### Apps — Deployment
- All 9 apps run locally only — no Railway/Vercel deploys yet
- App Tab URLs in `AppTab.tsx` are localhost

## How to Start

```bash
# Platform
make start && make celery

# Access AI Studio
open http://localhost:8000/ai-studio/
```

## How to Work with Rigby

```bash
python tools/pa_chat.py "your message" --tools --conversation pa-09efe1c2b63f
```

## Troubleshooting

```bash
# Kill all app servers
pkill -f uvicorn; pkill -f vite

# Full platform restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery
```
