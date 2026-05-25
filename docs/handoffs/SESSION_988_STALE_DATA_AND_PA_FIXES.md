---
originating_session: 988
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 988 - Stale Agent Data, Modal Overflow, PA Routing Fixes

**Date:** February 11, 2026
**Previous Session:** 987 (PA Wiring Completion)
**Focus:** Production bugs — modal overflow, broken content reviewers, PA intent routing, stale agent knowledge, execution history visibility

---

## Changes Made

### 1. InitiativeDetailModal Overflow Fix (PR merged to main)
**Files:** `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`

- `InitiativeDetailModal`: Added `line-clamp-2` on description, `truncate` on title, `shrink-0` on close button, `min-h-0` on scrollable body, status badge, collapsible "Full Description" toggle with `descriptionExpanded` state
- `ComprehensiveInitiativeModal` (the one actually used for "View Details"): Same fixes — `line-clamp-2`, `truncate`, `min-w-0`, `shrink-0`, collapsible description using existing `expandedSections` state

**Root cause:** `initiative.description` (thousands of characters of draft content + reviewer feedback) rendered untruncated inside the fixed header (`shrink-0` div), expanding the header to fill the viewport and pushing the scrollable body off-screen.

### 2. Content Reviewer Broken Import Fix
**Files:** `core/services/content_review_panel_v2.py`

- Fixed `_call_llm_reviewer()`: Changed `from core.llm_providers import get_llm_provider` (module doesn't exist) to `from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest`
- Updated to use `registry.complete(provider='openai', model_id='gpt-4.1-mini', request=LLMRequest(...))` pattern

**Impact:** SkepticReviewer and FactCheckReviewer were returning FAIL for every blog because the import error was caught and converted to a synthetic FAIL verdict.

### 3. PA Initiative Intent Routing Fix
**Files:** `core/services/unified_pa_entrypoint.py`

- Moved initiative/project pattern check BEFORE boardroom catch-all in `_detect_intent()`
- "What initiatives need attention?" was matching `attention` keyword → boardroom intent (1,462 items) instead of initiative intent

**Fix order:** Initiative patterns (line 602) now run before boardroom patterns, so "initiative" + "attention" routes correctly.

### 4. Agent Stale Data Grounding Fix
**Files:** `core/conversation_orchestrator.py`

- `_get_agent_knowledge()`: Added 14-day freshness cutoff to both `AgentKnowledgeSource` and `AgentMemory` queries
- `_build_turn_prompt()`: Strengthened DATA GROUNDING REQUIREMENT:
  - Bans "Notion spider", "Notion data", data collection dates, dataset sizes
  - Bans citing dates older than 30 days as evidence
  - Injects current month/year dynamically (e.g., "February 2026")
  - Explicitly states any 2023/2024 data reference is STALE

**Root cause:** `AgentKnowledgeSource` records had no date filter — agents grounded on stale records referencing "Oct 23, 2023 Notion data" across all 4 agents in multi-agent conversations.

### 5. Execution History Intent Routing + Formatter Fix
**Files:** `core/services/unified_pa_entrypoint.py`, `core/services/tool_dispatcher.py`

**Intent routing:** Added natural language patterns: `agents been doing`, `agents doing`, `what are agents`, `what have agents`, `agents been up to`, `agent work`, `agent conversations`, `deliberations`

**Field name mismatches fixed (handler → formatter):**
- `items` → `executions` (formatter expected wrong key)
- `hours_back` → `period_hours` (formatter expected wrong key)
- `successes` → `successful` (formatter expected wrong key)
- `items` (failures) → `failures` (formatter expected wrong key)

**DeliberationSession data added:** The `execution_history_tool` now also queries `DeliberationSession` (agent conversations), which is the primary agent activity but was previously invisible. Both `recent` and `stats` actions include conversation counts.

### 6. Crypto Price Intent
**Files:** `core/services/unified_pa_entrypoint.py`

- New `crypto_price` intent with patterns: `btc`, `bitcoin`, `ethereum`, `eth`, `crypto`, `solana`, `coin price`, `how much is`, etc.
- Smart payload builder with ticker-to-name mapping (btc→bitcoin, eth→ethereum, sol→solana, etc.)
- Routes to `spider_data_tool` with `action='search'`, `spider_name='coingecko'`
- Added enrichment mapping, LLM directive, formatter, and skip list entry

**Root cause:** "How much is BTC today?" fell through to generic LLM, which told user to check CoinGecko manually — despite the platform having a CoinGecko spider.

### 7. Capabilities Intent Pattern Narrowing
**Files:** `core/services/unified_pa_entrypoint.py`

- Removed `'have access to'` from capabilities intent patterns (too broad)
- Removed `'what do you have'` (too broad)
- Narrowed `'what tools'` to `'what tools do you'`
- Updated `_generate_capabilities_response()` to lead with "Web & Internet Access" (77 spiders) and "Crypto & Market Prices" sections
- Removed misleading "access external services not wired in" from can't-do list

**Root cause:** "Don't you have access to the internet?" matched `'have access to'` → capabilities dump instead of answering the question.

---

## Gotchas Discovered

1. **Two InitiativeDetailModals:** `InitiativeDetailModal` exists but ALL "View Details" clicks use `ComprehensiveInitiativeModal` (via `setComprehensiveInitiativeId`). Must fix both.
2. **`core.llm_providers` doesn't exist:** The correct import path is `core.services.llm_provider_registry` with `get_llm_provider_registry()` → `registry.complete()` API.
3. **PA intent routing order:** More specific patterns (initiative + attention) must come BEFORE generic catch-alls (boardroom matches "attention").
4. **AgentExecution vs DeliberationSession:** `AgentExecution` only records direct agent dispatches. Multi-agent conversations write to `DeliberationSession` — the execution_history tool was missing this entirely.
5. **Formatter-handler field mismatch:** The execution_history formatter was written with different field names than the handler returns, causing empty results even when data exists.
6. **Broad capabilities patterns hijack questions:** `'have access to'` matched "Don't you have access to the internet?" — always test new intent patterns against likely user questions that contain the same words.
7. **CoinGecko spider existed but wasn't routed:** The platform had a working crypto spider but no PA intent to use it — users were told to check CoinGecko manually.

---

## Production Verification

- PA "What initiatives need attention?" → Correctly returns 428 initiatives (not 1,462 boardroom items)
- PA "What needs my attention?" → Correctly returns boardroom with 1,488 items
- Both tested with curl against Railway production API with token auth
- Initiative modals now show 2-line clamped description with collapsible full text
- Content reviewers should now produce real PASS/FAIL verdicts instead of import-error FAILs

---

## Commits

1. `57128943` — fix: initiative modal overflow + content reviewer broken import
2. `0f3be5e0` — fix: clamp description overflow in ComprehensiveInitiativeModal
3. `f65c9a18` — fix: route initiative queries before boardroom catch-all in PA
4. `157194ae` — fix: prevent agents from grounding on stale 2023/2024 data
5. `9698b30d` — fix: execution history intent routing + formatter field mismatches
6. `865b6f0f` — feat: add crypto price intent for PA with coingecko spider routing
7. `5d406d68` — fix: narrow capabilities intent patterns to avoid hijacking internet questions
