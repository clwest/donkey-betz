# Session 989 - Production Verification & Field Name Fixes

**Date:** February 11, 2026
**Previous Session:** 988 (Stale Data, Modal Overflow, PA Routing Fixes)
**Focus:** Verify Session 988 fixes on Railway production, fix additional field name bugs discovered during verification

---

## Changes Made

### 1. SpiderData Field Name Fix (from Session 989 first fix)
**Files:** `core/services/tool_dispatcher.py`, `core/services/unified_pa_entrypoint.py`

- `_handle_spider_data` handler referenced non-existent SpiderData fields: `title`, `url`, `category`, `content`
- Fixed to use actual fields: `spider_name`, `source_url`, `data_type`, `embedding_text`
- All actions fixed: `recent`, `by_spider`, `by_category`, `search`, `stats`
- Search action: `Q(title__icontains=keyword)` -> `Q(embedding_text__icontains=keyword)`
- Formatter updated to match

### 2. Execution History Payload Fix
**Files:** `core/services/unified_pa_entrypoint.py`

- `_build_tool_payload()` had no `elif intent == 'execution_history':` block
- Default payload sent `action='list'` which is invalid (valid: recent, by_agent, stats, failures)
- Added payload builder with action detection from message keywords

### 3. AgentExecution Field Name Fix
**Files:** `core/services/tool_dispatcher.py`, `core/services/unified_pa_entrypoint.py`

- `AgentExecution.agent` is a ForeignKey to `Agent`, not a CharField
- Handler used `agent_name` (doesn't exist) — changed to `agent__name`
- Handler used `success=True` (field doesn't exist) — changed to `status='completed'`
- All `agent_name__icontains` filters changed to `agent__name__icontains`
- All `.values('agent_name', ...)` changed to `.values('agent__name', ...)`
- Formatter updated with fallback: `ex.get('agent__name', ex.get('agent_name', 'Unknown'))`

### 4. DeliberationSession Participants Formatter Fix
**Files:** `core/services/unified_pa_entrypoint.py`

- `DeliberationSession.participants` is a JSONField containing dicts, not strings
- `', '.join(participants[:3])` threw `TypeError: sequence item 0: expected str instance, dict found`
- Fixed to extract `name` key from dict participants before joining

---

## Verification Results

### Item 1: Content Reviewers Producing Real Verdicts - VERIFIED
- Triggered v2 blog generation via `POST /api/v1/research/self-blog/generate-v2/`
- Task `6615d2be` completed in 544s with `decision=REVISE`
- **SkepticReviewer: REVISE** with real substantive feedback about claims
- **FactCheckReviewer** ran successfully
- 14 claims used, 14 sources, 1 revision pass
- Blog `721d5f78` created as draft
- **Conclusion:** Import fix from Session 988 is working. Reviewers no longer return synthetic FAILs.

### Item 2: DeliberationSession in Execution History - VERIFIED
- "What have agents been doing?" returns:
  - 20 agent executions (ResearchAgent, all completed)
  - 20 agent conversations (DeliberationSessions)
  - Agent names resolved correctly via FK (agent__name: 'ResearchAgent')
  - Status icons and execution times displaying correctly
- Required 3 fixes: payload builder, agent__name fields, participants formatter

### Item 3: Crypto Price Intent Routes to CoinGecko - VERIFIED
- "How much is BTC today?" correctly routes to `crypto_price` intent -> `spider_data_tool`
- Tool executes successfully with `action='search'`, `keyword='bitcoin'`
- Returns 0 items (CoinGecko spider hasn't crawled recently — expected)
- No field errors — handler uses correct SpiderData fields
- "How much is ETH?" also works (maps ethereum correctly)

### Item 4: Celery Prefork Child Recycling - INCONCLUSIVE (Config Correct)
- Workers redeployed multiple times during verification
- Only 15 tasks processed since latest deploy — well under 50-task threshold
- `--max-tasks-per-child=50` and `--max-memory-per-child=200000` correctly set in Procfile
- Recycling will kick in naturally with more traffic
- Cannot observe recycling in a single session

### Item 5: Muscular System Score - VERIFIED (Better Than Expected)
- Verified earlier in session: status is "fit" (not 60.5% as noted)
- Import path: `from core.services.muscular import get_muscular_system`
- Some groups show "paralyzed" (markets, narrative, persona) due to low execution volume

---

## Railway Deployment Gotchas Discovered

1. **Each Procfile process is a SEPARATE Railway service.** `railway up` only deploys to the currently linked service (e.g., `donkey-betz-platform` = web). Celery workers (`celery-pa`, `celery-worker`, `celery-content`, etc.) are separate services that deploy independently.

2. **`railway redeploy` during a build CANCELS the build** and re-deploys the LAST successful build (old code). This caused us to deploy old code and wonder why fixes weren't working.

3. **GitHub push auto-deploys ALL services.** But builds take 8-12 minutes per service, and they build in parallel. `celery-pa` consistently takes longer than the web service.

4. **To verify code is live on a specific worker**, link to that service first: `railway service link celery-pa` then `railway logs`.

5. **Auth token for production API:** `Token <redacted-0cdc1c72-2026-04-20>` (User: Donkeyking)

---

## Additional Issues Found (Not Fixed)

### chat_conversations.platform Column Missing
```
WARNING: Failed to persist PA conversation: column chat_conversations.platform does not exist
```
The `ChatConversation` model has a `platform` field but it hasn't been migrated to the database yet.

### Profile Loading in Async Context
```
WARNING: Failed to load profile: You cannot call this from an async context - use a thread or sync_to_async
```
Profile loading and completeness score both fail in the Celery async context.

### docs/USER_FEEDBACK_QUEUE.md Missing
```
WARNING: Critical doc not found: docs/USER_FEEDBACK_QUEUE.md
```
Referenced by `docs_context_builder` but doesn't exist.

---

## Commits

1. `6f023010` — fix: spider_data tool uses wrong field names + execution_history missing payload
2. `22ca7681` — fix: execution_history handler uses agent__name (FK) not agent_name
3. `bf79a4d1` — fix: handle dict participants in execution_history formatter
