---
originating_session: 994
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 994 — Fix Stock Prediction Pipeline + Podcast User Context

**Date:** February 12, 2026
**Previous:** Session 993 (PA Capability Gaps: Write Actions + Blog Triage + V2 Generation)

## Summary

Fixed two broken subsystem pipelines identified via PA conversations on Railway production:

1. **Stock prediction pipeline** — predictions were silently failing, leaving 0.0 predicted_move on all PredictionOutcome records. Root cause: GPT returns numeric types but `_parse_target_move()` assumed strings, and one TypeError killed the entire batch.
2. **Podcast pipeline** — `PodcastCoordinatorAgent` was instantiated without user context, breaking all user-scoped operations (learning, memory, feedback attribution).

## Changes

### 1. Stock Prediction Type Safety (`market_intelligence_coordinator.py`)

**Root cause:** GPT-5-mini returns `target_upside`/`target_downside` as numeric types (e.g., `25` instead of `"25%+"`) in JSON responses. `_parse_target_move()` called `re.sub()` on these numbers, throwing `TypeError`. The outer try/except around the entire loop caught it and aborted, leaving ALL predictions for that brief at `predicted_move=0.0`.

**Fix 1 — `_parse_target_move()` (line ~1108):**
- Added early return for `int`/`float` inputs — returns the number directly
- Added `str()` coercion as safety net before regex operations
- Preserved all existing string parsing behavior (ranges, percentages, suffixes)

**Fix 2 — `_record_predictions_for_learning()` (line ~1164):**
- Wrapped each bull/bear iteration in its own `try/except`
- One bad ticker now logs a warning and continues instead of killing predictions for all tickers in the batch
- Logging includes the failing ticker for debugging

### 2. Podcast User Context (`tasks.py`)

**Root cause:** `PodcastCoordinatorAgent()` at line ~19870 was instantiated without user, despite `episode.user` being available from the loaded PodcastEpisode. Without `user`, all BaseAgent user-scoped operations (learning hooks, AgentMemory creation, ToolCallRecord attribution, feedback recording) run as anonymous.

**Fix:** `PodcastCoordinatorAgent()` -> `PodcastCoordinatorAgent(user=episode.user)`

## Diagnosis Path

Started from two PA conversations on Railway production:
- "Have there been any Podcasts created by the Agents?" -> PA reported stalling at ideation
- "What's going on with the Stock Agents?" -> PA showed 0 predictions, None accuracy

Traced both issues through code to identify root causes:
- Stock: BullCaseAgent/BearCaseAgent DO produce `target_upside`/`target_downside` (with proper fallbacks). The bug was in the coordinator's parsing/recording, not in the sub-agents.
- Podcast: The coordinator agent works fine when given user context. The Celery task just wasn't passing it.

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/stocks/market_intelligence_coordinator.py` | `_parse_target_move()`: type safety for numeric inputs. `_record_predictions_for_learning()`: per-iteration error handling. |
| `core/tasks.py` | `generate_podcast_episode`: pass `episode.user` to `PodcastCoordinatorAgent` |

## What We Did NOT Change

- No new models, migrations, or Celery tasks
- No frontend changes
- No changes to sub-agents (BullCaseAgent, BearCaseAgent, DebateAdvocateAgent, etc.)
- No changes to PodcastCoordinatorAgent itself (only how it's instantiated)
- Existing PredictionOutcome records with `predicted_move=0.0` are NOT backfilled (new briefs will record correctly going forward)

## Testing

**Stock predictions:** Next scheduled MarketIntelligenceCoordinator run will:
- Parse GPT numeric responses without crashing
- Record predictions for each ticker independently
- Log warnings for any individual failures instead of silent batch abort

**Podcast:** Next podcast generation will:
- Have user context for learning hooks and memory attribution
- Show up in agent execution history with proper user association

## Verification Queries (Railway)

```python
# Check if new predictions are recording with non-zero moves
from core.models_unified_system import PredictionOutcome
recent = PredictionOutcome.objects.order_by('-prediction_date')[:20]
for p in recent:
    print(f"{p.ticker} {p.prediction_type} move={p.predicted_move} date={p.prediction_date}")

# Check podcast episodes for user attribution
from core.models_podcast_studio import PodcastEpisode
for ep in PodcastEpisode.objects.order_by('-created_at')[:5]:
    print(f"{ep.id} user={ep.user} status={ep.status}")
```
