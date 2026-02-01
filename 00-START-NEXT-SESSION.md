# Session 891 - Start Here

**Previous Session:** 890 (Podcast Quality Improvements)
**Date:** January 31, 2026
**Status:** 76 Agents | 77 Spiders | 25 Advisors | 139 Personas | **103 Active Initiatives** | **CONTENT FEEDBACK LOOP ACTIVE** | **PODCAST QUALITY SYSTEM ACTIVE**

---

## What Was Accomplished in Session 890

### Podcast Quality Improvements (PR #632)

Based on ChatGPT quality feedback, implemented comprehensive improvements to raise podcast scripts from 7.5/10 to 9.5/10 potential.

#### 1. Anti-Cliché Enforcement (VoiceCriticAgent)
- Added 25+ podcast-specific generic phrases to `GENERIC_PHRASES` list
- New phrases detected: "fascinating world", "exciting episode", "eye-opening", "vibrant and evolving", "brilliant minds", "groundbreaking", etc.

#### 2. PodcastStyleProfile Model
- New Django model for tracking podcast quality metrics
- **Voice scores**: distinctiveness, specificity, opinion strength (0-100)
- **Podcast metrics**: humor_percent, technical_depth, story_density, authority_score
- **Quality flags**: generic_flag, has_concrete_examples, host_has_pov
- **War stories tracking**: platform_mentions, war_stories_count
- Weighted `overall_quality_score` calculation with bonuses/penalties

#### 3. PodcastCoordinatorAgent Improvements
- **BANNED PHRASES** section in system prompt
- **REQUIRE SPECIFICITY** guidelines (timestamps, real numbers, named systems)
- **PLATFORM ANCHORING** instructions (reference Donkey Betz features naturally)
- New `get_system_war_stories` tool that fetches real system incidents

#### 4. ModeratorAgent Personality Upgrade
- Host now has **opinions and takes stances**
- No longer "neutral pleasant narrator" - has a builder's mindset
- **Direct challenging questions** instead of generic validation
- Removed generic phrases from intro/outro templates

**Handoff:** `SESSION_890_PODCAST_QUALITY.md`

---

## What Was Accomplished in Session 889

### Fixes Completed
| PR | Issue | Fix |
|----|-------|-----|
| #625, #627 | Podcast endpoints empty | Token auth added to 6 endpoints |
| #629 | SKIN health 25% | Workspace permissions management command |
| #630 | Live Monitor empty | Real agent activity data source |
| #631 | Session documentation | Handoff docs prepared |

**Handoff:** `SESSION_889_COMPLETE.md`

---

## Current Celery Architecture

```
celery-worker: -Q default,agents,sports,ml (4 concurrency)
celery-content: -Q content (4 concurrency)        # Workspace writing tasks
celery-long-running: -Q long_running (2 concurrency)
celery-beat: scheduler
celery-broadcast: -Q broadcast (2 concurrency)
```

---

## TOP PRIORITY for Session 891

### 1. Run Podcast Migration on Production
```bash
railway run python manage.py migrate core
```

### 2. Test Podcast Quality Improvements
Generate a test podcast and verify:
- No generic phrases in output
- Specific examples with timestamps
- Host takes stances/pushes back
- Platform features mentioned naturally

### 3. Monitor Body Health
```bash
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/body/health/"
```

### 4. Consider Phase 2: Human Feedback
Add thumbs up/down UI for published blogs to gather explicit human feedback.

---

## Quick Commands

```bash
# Start platform
make start && make celery

# Run podcast migration (production)
railway run python manage.py migrate core

# Check podcast quality profile
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/podcasts/list/"

# Check body health
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/body/health/"

# Check agent executions
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/v1/agents/monitoring/dashboard/"

# Manually trigger podcast generation
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{"topic":"AI Agent Orchestration"}' \
  "https://donkey-betz-platform-production.up.railway.app/api/podcasts/create/"
```

---

## Recent PRs

| PR | Description |
|----|-------------|
| #632 | Podcast quality improvements (anti-cliché, war stories, host POV) |
| #631 | Session 889 documentation |
| #630 | Live Monitor shows real agent activity |
| #629 | Workspace permissions management command |
| #627 | Add Token auth to podcast status, script, delete, generate-audio |
| #625 | Add Token auth to podcast_list and podcast_stats endpoints |

---

## Recent Session History

| Session | Focus | Handoff |
|---------|-------|---------|
| **890** | Podcast Quality Improvements (anti-cliché, war stories, host POV) | `SESSION_890_PODCAST_QUALITY.md` |
| **889** | Podcast Token Auth + SKIN Health Fix + Live Monitor Fix | `SESSION_889_COMPLETE.md` |
| **887** | Operations Tab Fix + Content Improvements + Boardroom Auth | `SESSION_887_OPERATIONS_TAB_FIX.md` |
| **886** | Content Feedback Loop - BlogPerformanceContextBuilder Phase 1 | `SESSION_886_CONTENT_FEEDBACK_LOOP.md` |
| **885** | Celery Content Pipeline + Operations Tab Fix | `SESSION_885_CELERY_CONTENT_PIPELINE.md` |

---

## System Stats

| Component | Count |
|-----------|-------|
| Agents | 76 |
| Spiders | 77 |
| Advisors | 25 |
| Personas | 139 |
| Database Models | 379+ (added PodcastStyleProfile) |
| Celery Tasks | 281 |
| Services | 125 |

---

## Podcast Quality System Status

| Component | Status |
|-----------|--------|
| Anti-Cliché Detection | Active (50+ phrases) |
| PodcastStyleProfile Model | Created (needs migration) |
| System War Stories Tool | Implemented |
| Host POV Upgrade | Active |
| Quality Scoring | Ready |

---

## Content Feedback Loop Status

| Component | Status |
|-----------|--------|
| BlogPerformanceContextBuilder | Active |
| Context Injection | Enabled in ContentWriterAgent |
| Research Pre-Step | Enabled (Session 887) |
| Human Feedback UI | Phase 2 (not implemented) |

---

## Podcast API Status

| Endpoint | Token Auth | Status |
|----------|------------|--------|
| GET /api/podcasts/list/ | ✅ | Working |
| GET /api/podcasts/{id}/script/ | ✅ | Working |
| POST /api/podcasts/create/ | ✅ | Working |
| Auto-generate task | ✅ | Every 12 hours |

---

## Initiative Pipeline Status

| Metric | Count |
|--------|-------|
| Total Active | 103 |
| Stage 1 (Research) | 11 |
| Stage 2 (Analysis) | 49 |
| Stage 3 (Synthesis) | 40 |
| Stage 4 (Validation) | 2 |
| Stage 5 (Delivery) | 1 |

---

**All systems operational. Podcast quality system implemented. Run migration on production to activate PodcastStyleProfile.**
