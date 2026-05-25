---
originating_session: 985
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 985 -- PA Boardroom Response Improvement

**Date:** February 10, 2026
**Previous Session:** 984 (Boardroom Feeder Fix + Celery Worker OOM)

---

## Problem: PA Boardroom Response Too Generic

When asking the PA "What needs my attention?", the response was:
1. **Stats-only data** -- the `boardroom_tool` stats action returned aggregate counts (585 attention, 282 decisions) but zero actual items. The LLM had to analyze counts, not items.
2. **Verbose LLM analysis** -- no conciseness constraints meant the LLM produced 500+ word responses restating counts and giving vague advice.
3. **No actionable items** -- critical/high urgency items existed but weren't shown inline. Users had to separately say "list critical" to discover them.

## Investigation Findings

### Boardroom Data Verified on Railway Production
- 593 pending attention items (all under user `Donkeyking` UUID)
- 269 draft decisions (264 product, 4 architecture, 1 experiment)
- 6 CRITICAL items (3 StockAuditCoordinator alerts, 3 ContentWriterAgent reviews)
- 0 high urgency items, 589 medium, 3 low
- Auto-approve IS working correctly (24h age gate from Session 984)
- Inflow rate ~579 items/day from spider_pipeline creates steady-state of ~500+ pending

### PA Code Path Traced
Full pipeline for "What needs my attention?":
1. `_build_context` -- user profile, docs, system stats (every request)
2. `_detect_intent_and_route` -- `'attention'` keyword -> `('boardroom', 'boardroom_tool')`
3. `_build_tool_payload` -- no action keywords match -> defaults to `action='stats'`
4. `_handle_boardroom` stats -- returns counts only, no items
5. `_enrich_tool_result` -- fires `intelligence_enricher` + `strategic_memory` (15s timeout)
6. `_format_tool_result` -- renders counts by urgency and type
7. `_build_analytical_prompt` -- boardroom directive was vague: "Summarize the decision landscape"
8. `_generate_response_from_tool` -- LLM analysis appended after structured output

## Solution: 3 Changes

### Change 1: Fetch Top Items in Stats Action

**File:** `core/services/tool_dispatcher.py` -- `_handle_boardroom()` (line ~1107)

Added query for top 10 critical/high urgency attention items ordered by `priority_score` desc, `created_at` desc. Returns `title`, `urgency`, `item_type`, `source_agent`, `priority_score`, `created_at`, `id` as `top_items` in the stats response dict.

### Change 2: Show Items Inline in Formatter

**File:** `core/services/unified_pa_entrypoint.py` -- `_format_tool_result()` (line ~1514)

Added "Needs your attention now" section after urgency counts. Shows up to 8 top items with:
- Agent prefix stripped from title (avoids redundant "StockAuditCoordinator: StockAuditCoordinator...")
- Word-boundary truncation at 70 chars
- Urgency tag, source agent, short ID for action commands
- Updated CTA: `Say 'list critical' or 'list high' to see more, or 'approve item [id]' to act.`

Removed the `by_type` breakdown from stats view (was noise for quick triage).

### Change 3: Concise Boardroom Analytical Directive

**File:** `core/services/unified_pa_entrypoint.py` -- `_build_analytical_prompt()` (line ~1331)

Replaced vague directive:
```
"FOCUS: Summarize the decision landscape. Highlight urgency levels.
Recommend triage order. Note any items linked to active initiatives."
```

With structured constraints:
```
"FOCUS: The user's pending items are already listed above.
- Max 3-5 bullets of INSIGHT only -- do NOT restate counts or item lists
- Lead with critical/high items: what they are and why they matter
- Identify patterns (e.g., most items from one source, or a spike)
- Recommend a triage strategy (what to handle first, what to bulk-dismiss)
- If item volume is high, suggest bulk actions to reduce noise"
```

---

## Testing

Tested on Railway production database via `railway run`:
- Stats handler returns 6 critical items with correct data
- Formatter produces clean output with stripped agent prefixes
- Analytical prompt gives LLM actual items to reference

### Sample Output (Before)
```
Hi Donkeyking, your Boardroom has 865 pending items:
**Attention Items:** 584
  - 6 CRITICAL urgency
  - 14 high urgency
  ...
  **By type:**
    - spider_action: 470
    - insight: 74
    ...
[500+ word LLM analysis restating the same counts]
```

### Sample Output (After)
```
Hi Donkeyking, your Boardroom has 867 pending items:
**Attention Items:** 598
  - 6 CRITICAL urgency
  - 589 medium urgency
  - 3 low urgency

**Needs your attention now:**
  - Run comprehensive stock market audit [CRITICAL] from StockAuditCoordinator
  - Assess risks and anomalies for watchlist [CRITICAL] from StockAuditCoordinator
  - Produce a prototype article... [CRITICAL] from ContentWriterAgent
  ...

**Draft Decisions:** 269
  - 264 product, 4 architecture, 1 experiment

Say 'list critical' or 'list high' to see more, or 'approve item [id]' to act.

---
[3-5 bullet concise LLM insight with pattern analysis and triage recommendation]
```

---

## Files Changed

| File | Lines | Change |
|------|-------|--------|
| `core/services/tool_dispatcher.py` | ~1107-1116 | Added `top_items` query to stats action |
| `core/services/unified_pa_entrypoint.py` | ~1331-1338 | Rewrote boardroom analytical directive |
| `core/services/unified_pa_entrypoint.py` | ~1514-1531 | Added inline top items in stats formatter |

No migrations. No frontend changes. No new dependencies.

---

## Celery Worker OOM Deep Fix

### Problem
celery-worker crashed with OOM on Railway after Session 984's prefork migration. Root cause: heavy ML libraries loaded at module level into the Celery parent process (~800MB).

### Import Chain Traced
1. `core/assistant/__init__.py` -> `base.py` -> `core/personal_ai_assistant.py` line 19: bare `from ml.core.ml_engine import MLEngine`
2. `ml/core/ml_engine.py` lines 20-25: `import torch` (~500MB) + `from sklearn.ensemble import ...` (~100MB) + `from transformers import pipeline` (~200MB)
3. These load into the parent process at Django init, inherited by ALL child processes

### Fixes (6 files)

| File | Change |
|------|--------|
| `Procfile` | All workers: `-c 1`, `--max-memory-per-child=200000` (was `-c 2`, 300000) |
| `ml/core/ml_engine.py` | Moved `import torch`, `from sklearn`, `from transformers` to inside methods. `MLConfig.device` now uses `_detect_device()` helper with lazy torch import |
| `core/personal_ai_assistant.py` | Wrapped `from ml.core.ml_engine import MLEngine` in `try/except ImportError` |
| `intelligence/orchestration/agent_advisor_bridge.py` | Wrapped `from ml.core.ml_engine import PatternPrediction` and `MLService` in `try/except ImportError` |
| `self_awareness/embeddings.py` | Moved `from sklearn.metrics.pairwise import cosine_similarity` inside the one method that uses it |
| `core/tasks.py` | Added `.iterator()` to 3 unbounded `.objects.all()` loops (lines 12529, 12758, 25704) |

### Expected Impact
- Parent process memory: ~800MB -> ~200MB (torch/sklearn/transformers no longer loaded at init)
- Child process recycling: max 200MB per child, recycled after 50 tasks
- Peak memory: ~400MB (parent + 1 child) vs ~800MB+ (parent + 2 children with ML loaded)

---

## Patterns for Future Sessions

**PA response quality improvements follow this pattern:**
1. Trace the code path: intent detection -> tool handler -> enrichment -> formatter -> LLM prompt
2. Identify what data the tool handler actually returns vs what the LLM needs
3. Enrich the tool response with actionable data (items, not just counts)
4. Constrain the LLM directive with max bullets, "do NOT restate", lead-with-X rules
5. Test on Railway production data before deploying

**Celery memory management:**
- NEVER import torch/sklearn/transformers at module level -- use lazy imports inside methods
- Module-level imports in files reachable from `core/assistant/__init__.py` load into Celery parent process
- Check import chains: `core/assistant/` -> `personal_ai_assistant.py` -> `ml/core/ml_engine.py`
- Use `.iterator()` on queryset loops to avoid loading entire tables into memory
