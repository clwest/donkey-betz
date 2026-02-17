# Session 1023 - Start Here

**Previous Session:** 1022 (Cost Optimization Audit — Deliverable Dedup, Remediation Pause, Conversation Dedup)
**Date:** February 16, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,488 SIGNAL CLUSTERS** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **DELIVERABLE DEDUP: LIVE** | **CONVERSATION DEDUP: LIVE** | **REMEDIATION SYSTEM: PAUSED** | **COST SAVINGS: ~$14/day**

---

## Session 1022 Summary (Just Completed)

### Cost Optimization Audit (PRs #1253-#1258)

**Agent Execution 500 fix (PR #1255):** `views_agent_execution.py` accessed `execution.agent.display_name` but `core.models_unified_system.Agent` only has `name`. Fixed in 3 locations.

**Deliverable dedup (PR #1256):** `_save_to_deliverable()` always created new rows — intelligence desk agents (ArbitrageDetector, StockAnalystAgent, etc.) running every 5-15 min produced 1,500+ identical deliverables/day. Added 4-hour dedup window. Cleaned up 5,850 duplicate rows (9,577 → 3,737).

**Remediation system paused (PR #1257):** CodeGeneratorAgent burned $7.10/day (54% of total cost) on 86 remediation tasks it can't complete — runs in empty sandbox with no real codebase access. Cancelled 26 stuck tasks, paused all 5 remediation Celery Beat schedules.

**Conversation dedup (PR #1258):** `run_agent_conversation` and `run_multi_agent_conversation` had zero dedup — same topics repeated 41x/day. 293 conversations/24h, only 121 unique (59% dupes), wasting ~$7/day. Added 6-hour dedup window on both `related_knowledge` FK and topic string.

**Initiative cleanup:** Deleted 32 ARCHIVED initiatives (zero activity), promoted 4 TRIAGE → ACTIVE. Current: 3 ACTIVE (Stage 2), 1 TRIAGE.

### PRs: #1253, #1254, #1255, #1256, #1257, #1258

---

## Session 1021 Summary

### Initiative Pipeline Integrity (PRs #1250, #1251, #1252)

- DRAFT stage approval fix, no stage skip-ahead, real data gathering for stage documents
- See `docs/handoffs/SESSION_1021_INITIATIVE_PIPELINE_INTEGRITY.md`

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 396+ |
| Services | 134 |
| Celery Tasks | 268 (5 remediation schedules paused) |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 27 |
| Agents Persisting Output | 43 (via `_save_to_deliverable()` with 4h dedup) |
| PA Tools | 97 |
| PA Intents | 39 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | 3 (Stage 2, IN_REVIEW) + 1 TRIAGE |
| Blogs | 497 |
| Signal Clusters | 1,488 |
| Deliverables | ~3,737 (cleaned from 9,577) |
| Daily LLM Cost | ~$13/day → expected ~$6/day after fixes |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Verify Before Starting

### 1. Cost Reduction (Session 1022 — CRITICAL)
- Verify deliverable count stabilized (should NOT grow by 1,500/day anymore):
  ```
  railway run python manage.py shell -c "
  from core.models_deliverables import Deliverable
  from django.utils import timezone; from datetime import timedelta
  last_24h = Deliverable.objects.filter(created_at__gte=timezone.now()-timedelta(hours=24)).count()
  total = Deliverable.objects.count()
  print(f'New deliverables (24h): {last_24h}')
  print(f'Total deliverables: {total}')
  "
  ```
- Expect ~150-300 new/day (down from 1,500+)

### 2. Conversation Dedup (Session 1022)
- Verify conversation count dropped:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentConversation
  from django.utils import timezone; from datetime import timedelta
  from collections import Counter
  cutoff = timezone.now() - timedelta(hours=24)
  topics = list(AgentConversation.objects.filter(started_at__gte=cutoff).values_list('topic', flat=True))
  unique = len(set(topics))
  print(f'Conversations (24h): {len(topics)}, Unique: {unique}, Dupe rate: {1 - unique/max(len(topics),1):.0%}')
  "
  ```
- Expect <150 total, <20% dupe rate (down from 293 / 59%)

### 3. CodeGeneratorAgent Cost (Session 1022)
- Verify CodeGeneratorAgent executions dropped to near-zero:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentExecution
  from django.utils import timezone; from datetime import timedelta
  cutoff = timezone.now() - timedelta(hours=24)
  cg = AgentExecution.objects.filter(agent__name='CodeGeneratorAgent', created_at__gte=cutoff)
  print(f'CodeGeneratorAgent executions (24h): {cg.count()}')
  cost = sum(float(e.cost or 0) for e in cg)
  print(f'Cost: \${cost:.2f}')
  "
  ```
- Expect near $0 (down from $7.10/day)

### 4. Real Data Gathering in Stage Documents (Session 1021)
- Check if new stage documents contain real spider data:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import SelfBlog
  from django.utils import timezone; from datetime import timedelta
  recent = SelfBlog.objects.filter(
      category='initiative_stage',
      created_at__gte=timezone.now()-timedelta(hours=24)
  ).order_by('-created_at')[:3]
  for b in recent:
      print(f'{b.created_at.strftime(\"%H:%M\")} | {b.title[:60]}')
      has_data = 'Spider Intelligence' in b.full_text or 'Signal Clusters' in b.full_text or 'No data available' in b.full_text
      print(f'  Has real data markers: {has_data}')
      print(f'  First 200 chars: {b.full_text[:200]}')
  "
  ```

---

## Known Issues / Open Items

### Rubber-Stamped Initiatives — NEEDS AUDIT
Initiatives that reached Stage 5 via the skip-ahead bug (PR #1251) have Stage 3-5 docs generated out of order with no real data. May need doc regeneration.

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remediation System — PAUSED (Session 1022)
All 5 Celery Beat schedules commented out. 86 tasks in DB contain some valuable findings:
- `_calculate_error_rate()` always returns 0.0
- Multiple `AgentExecution` models across modules
- `core/tasks.py` is 12,000+ lines
- 1,200+ endpoints without docs
Re-enable when agents have real workspace access. Consider surfacing valuable findings via HumanAttentionItem/Boardroom.

### Dream Pipeline — NO-OP
Zero approved dreams, zero DreamImplementations. Only $0.54/day so not urgent, but the entire dream→implementation pipeline is non-functional.

### Remaining Agent Failures — REDUCED
- `.metadata` crashes: **0** (PR #1236)
- False-positive timeouts: **0** (PR #1237)
- Conversation junk: **0** (PR #1239)
- Initiative stall: **FIXED** (PRs #1247, #1250)
- Initiative duplicates: **FIXED** (PR #1247)
- Initiative skip-ahead: **FIXED** (PR #1251)
- Initiative garbage docs: **FIXED** (PR #1252)
- Conversation date hallucination: **FIXED** (PR #1248)
- Deliverable spam: **FIXED** (PR #1256)
- Conversation duplication: **FIXED** (PR #1258)
- Remediation waste: **FIXED** (PR #1257)
- Remaining: AudioAgent (ElevenLabs quota, ~7/day), assorted others (~18/day)

### CodeArtifact v2 — DEFERRED
- PatchApplier service, frontend review panel, initiative FK wiring
- 35 artifacts pending review

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland. PR #1141 strengthens novelty scoring.

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). Monitor by sport/model.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

**Agent model confusion (Session 1022):**
- `core.models_unified_system.Agent` — has `name`, used by `AgentExecution` FK
- `core.models.agents_registry.Agent` — has `display_name`, used by agent registry
- Always use `.name` for `AgentExecution.agent` — NOT `.display_name`

**Deliverable dedup (Session 1022):**
- `_save_to_deliverable()` checks 4-hour window by `title` + `agent_name`
- If match found, updates existing row instead of creating new

**Conversation dedup (Session 1022):**
- Both `run_agent_conversation` and `run_multi_agent_conversation` check 6-hour window
- Dedup on both `related_knowledge` FK and topic string
- Only applies to `trigger_type='scheduled'` conversations

**Initiative pipeline (Session 1021):**
- `advance_initiative_pipeline` only processes `init.current_stage` — never scans ahead
- Prior stage must be `APPROVED` before current stage is processed
- `_gather_initiative_research()` queries SpiderData, SignalClusters, AgentConversations, Deliverables
- `TechnicalDocumentAgent` has NO tools — only works with data provided in prompt/context

**Initiative 6 creation paths (Session 1020):**
- All have circuit breaker + similarity dedup

**Agent timeout limits (Session 1017, tuned Session 1020):**
- `execute_agent_task`: `soft_time_limit=2700` (45 min), `time_limit=3000` (50 min)
- OpenAI client timeout: 60s
- `cleanup_stale_agent_executions`: threshold 45min, runs every 15min

**AgentResult fields (Session 1017):**
- `.content` is @property alias for `.message`
- `.metadata` is @property alias for `.data`

**Railway multi-service deployment:**
- Each Procfile process is a SEPARATE Railway service
- GitHub push auto-deploys ALL services
- Celery workers can take up to 30 min to go live after push

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`).

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
