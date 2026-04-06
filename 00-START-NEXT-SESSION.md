# Next Session — Start Here

**Date:** April 6, 2026
**Previous Session:** Platform Audit + Founder Toolkit Launch
**PA Conversation:** pa-d19c1674b936
**Status:** 218 Agents | 80 Spiders | 25 Advisors | PA function calling LIVE (GPT-5.2) | 4 Founder Toolkit apps LIVE with Stripe

---

## What Was Done This Session

### Founder Toolkit — 4 Apps Deployed to Production (FREE hosting)

| App | URL | Stripe | Templates/Features |
|-----|-----|--------|-------------------|
| **PitchDeckForge** | pitchdeckforge.vercel.app | $29/mo Pro, $79/mo Team | 4 deck templates, PDF export, bonus slides, share links, slide delete |
| **MentorForge** | mentorforge.vercel.app | $19/mo Pro, $49/mo Enterprise | 12 AI mentor personas (8 tech + 4 fundraising) |
| **DealFlowTracker** | dealflowtracker.vercel.app | $39/mo Pro, $99/mo Fund | Kanban pipeline, scorecards, AI investment memos, contacts |
| **Contract Concierge** | contract-concierge on Render/Vercel | $29/mo Pro, $79/mo Business | 12 contract templates (NDA, LOI, Advisor, ToS, Privacy, Invoice, etc.) |

**Infrastructure:** Render (backend, free tier) + Vercel (frontend, free) + shared PostgreSQL + shared Stripe + SSO across all 4 apps

### 12-Dossier Platform Reality Audit (`docs/audit-2026/`)

Complete ground-up audit of every subsystem for patent lawyer and investors:

| # | Subsystem | Status | Key Finding |
|---|-----------|--------|-------------|
| 1 | Celery Orchestration | WORKING | 413 tasks, 48 scheduled, 9 queues |
| 2 | Agent System | WORKING | 84 code + 139 DB agents, 11-source context injection |
| 3 | Spider Network | WORKING | 86 spiders, 40+ web sources, 30-min cycle |
| 4 | Content Pipeline | WORKING | 7-stage deliberation + publish gate |
| 5 | Prompt Assembly | WORKING | 11 injection layers, mood/evolution modifiers |
| 6 | Embeddings + RAG | WORKING | 7 embedding stores, pgvector HNSW |
| 7 | Learning Loops | WORKING | Loop IS closed — 454+ pattern applications, 96.5% effectiveness |
| 8 | Personal Assistant | WORKING | 103 tools, 162 handlers, GPT-5.2 |
| 9 | Signals + Initiatives | WORKING | Full spider→signal→initiative chain |
| 10 | ConceptForge | WORKING | 6-stage pipeline, 18 advisors, gate relaxed |
| 11 | Frontend + Workspaces | WORKING | 23 tabs, 9 embedded apps |
| 12 | Infrastructure | WORKING | Django 5, PostgreSQL+pgvector, 11 LLM providers |

### Learning Loop Improvements
- XP bonuses now applied during execution (speed_bonus → more tokens, quality_bonus → more time)
- Weekly pattern decay task (stale patterns lose confidence)
- Deprecated dead code in LearningLoopOrchestrator

### Platform Fixes (7 PRs merged)
- Deliverable ownership: all deliverables auto-assigned to user
- Agent dedup guard: 10-min cache lock prevents duplicate dispatch
- Superuser workspace access: Jessica/Jeremy can now activate any workspace
- Build tab UX: empty states with CTAs, duplicate sub-tabs removed
- TypeScript errors: 38→0 in Build tab files
- Home tab: workspace-scoped data
- Initiative populate: rewritten to work with real data
- Workspace config: auto-create default config
- Shared knowledge endpoint: /api/v1/collective/shared-knowledge/
- ConceptForge gate: relaxed to quality-only (tags optional)

### Truth Gaps Audit Results

| Gap | Finding |
|-----|---------|
| Spider embeddings | 20.1% coverage (22K of 109K) |
| Memory embeddings | 97.6% coverage (good) |
| Agent effectiveness | Real data, not defaults (4.5% at default 85) |
| LLM providers | 99.2% OpenAI, also Anthropic + Together tested |
| Spider success rate | 67.7% (32% return 0 items) |
| Tool call tracking | 100% success but only 48 records |
| Initiatives | 0 completed of 248 (218 stuck at stage 1) |

---

## Accounts

- `donkeyking` (Chris) — superuser/owner (Railway: `admin`, Local: `admin`)
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer

## Local Development Setup

```bash
# Main platform
make start && make celery

# PA worker (separate terminal)
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l info --pool=threads -c 2 -Q pa

# All 9 apps (separate terminal)
for app in pitchdeckforge dealflowtracker mentorforge sellerpilot signal-studio scoutplays compliancesentinel contract-concierge ironwood-protocol; do
  (cd /Users/donkeyking/development/$app/backend && uvicorn app.main:app --port $(grep port /Users/donkeyking/development/$app/start.sh | grep -o '[0-9]*' | head -1) --host 0.0.0.0 --reload &)
  (cd /Users/donkeyking/development/$app/frontend && npx vite &)
done

# Talk to Rigby locally
PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 python tools/pa_chat.py "message" --tools --conversation pa-d19c1674b936
```

## PRIORITY 1: Revenue (This Week)

Rigby's GTM strategy — sell "Fundraising Sprint Stack" not 4 individual apps:
1. **Outbound DMs** (50-100/day) to founders actively raising on LinkedIn/AngelList
2. **Partner intros** to fractional CFOs, startup lawyers, accelerator mentors
3. **Community posts** on r/startups, Indie Hackers, LinkedIn (outcome-first, not feature-first)
4. **Bundle pricing**: "Raise Ready in 72 Hours" trial at $9-19

## PRIORITY 2: Platform Stabilization

- Spider embedding backlog (20% coverage → needs batch backfill)
- Initiative pipeline stall (0 completed — need auto-approve or batch-approve)
- Re-enable agent scheduled runs (token conservation mode too aggressive)
- Audit broken spiders (32% failure rate)

## PRIORITY 3: Remaining Platform Work

- Workspace tabs: Work, Intelligence, System tabs need same audit as Build
- Content Packets UI: packet detail page
- Stripe webhooks: subscription status tracking
- All 9 standalone apps need Stripe integration (4 done, 5 remaining)

## Known Issues

### Founder Toolkit Apps
- All 4 share one free Render PostgreSQL database
- Shared SECRET_KEY for SSO (founder-toolkit-shared-secret-2026)
- Seed scripts check app-specific tables (not users) to avoid skip on shared DB
- Contract Concierge needs FRONTEND_URL env var for Stripe redirect

### Platform
- `unique_active_workspace_per_user` DB constraint: only 1 active per user
- CeleryTaskEvent table had to be manually created on shared DB
- Token conservation mode: most agent/content scheduled tasks disabled

## How to Work with Rigby

```bash
# Production
python tools/pa_chat.py "message" --tools --conversation pa-d19c1674b936

# Local
PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 python tools/pa_chat.py "message" --tools --conversation pa-d19c1674b936

# Or use the shortcut
bash tools/pa_local.sh "message"
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
