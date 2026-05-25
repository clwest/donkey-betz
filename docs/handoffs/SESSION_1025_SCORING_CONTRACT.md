---
originating_session: 1025
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1025 — Scoring Contract: Reach, Intent & Replicability

**Date:** February 17, 2026
**PRs:** #1267, #1268

## Problem

SignalClusters had `strength`, `confidence`, `novelty`, and `urgency` scores, but no way to distinguish between signals that drive **attention** (trending topics for content) vs **intent** (actionable opportunities for micro-products). All signals were treated the same, so content agents and opportunity agents fought over the same queue.

## Solution

Added a rule-based scoring contract with 3 new dimensions + source confidence + track assignment to every SignalCluster. This enables a two-track pipeline:
- **Attention track**: High reach signals -> content generation (blogs, reports)
- **Intent track**: High intent signals -> micro-product creation (courses, tools, guides)

### Evidence Pipeline Maturity Roadmap

| Step | What | Status |
|------|------|--------|
| 1 | Semantic spider search | DONE (Session 1024, PR #1265) |
| 2 | Evidence gates (4 layers) | DONE (Session 1023, PRs #1262-1264) |
| 3 | **Scoring contract** | **DONE (this session)** |
| 4 | Auto-experiment generator | FUTURE |

## Files Changed

| File | Change |
|------|--------|
| `core/models_signal_intelligence.py` | 5 new fields on `SignalCluster` |
| `core/services/content_scoring_service.py` | **NEW** — Rule-based scoring engine (~150 lines) |
| `core/services/signal_aggregation_service.py` | Hooks scoring into `_create_signal_clusters()` |
| `core/tasks.py` | `backfill_signal_scores` task |
| `core/migrations/0248_signalcluster_scoring_fields.py` | Adds 5 fields |

## New Fields on SignalCluster

```python
reach_score = FloatField(default=0.0)        # 0-1: viral/audience potential
intent_score = FloatField(default=0.0)       # 0-1: commercial/actionable potential
replicability_score = FloatField(default=0.0) # 0-1: can we act on this repeatedly
source_confidence = FloatField(default=0.0)  # 0-1: trustworthiness of sources
track = CharField(max_length=20, default='unclassified',
    choices=[('attention', ...), ('intent', ...), ('unclassified', ...)])
```

## ContentScoringService

Pure rule-based scoring — **no LLM calls**. Uses keyword sets, source tiers, and simple heuristics.

### Scoring Formulas (all 0-1)

**reach_score:** `0.4 * source_diversity + 0.3 * keyword_reach + 0.3 * strength`
- `source_diversity` = `min(len(sources) / 5, 1.0)`
- `keyword_reach` = proportion of keywords matching REACH_KEYWORDS

**intent_score:** `0.5 * keyword_intent + 0.3 * data_type_intent + 0.2 * urgency`
- `keyword_intent` = proportion of keywords matching INTENT_KEYWORDS
- `data_type_intent` = 1.0 if pattern_type in {`opportunity_window`, `skill_demand`}, 0.5 if `demand_spike`, else 0.0

**replicability_score:** `0.5 * is_evergreen + 0.3 * has_multiple_sources + 0.2 * is_recurring`
- `is_evergreen` = 1.0 if keywords contain tutorial/guide/how-to terms
- `is_recurring` = 0.5 (placeholder — needs historical comparison)

**source_confidence:** Weighted average of source tiers (tier1=1.0, tier2=0.6, tier3=0.2, unknown=0.3)

### Track Assignment

```
intent >= 0.6           -> 'intent'
reach >= 0.6            -> 'attention'
intent >= 0.4 and > reach -> 'intent'
reach >= 0.4 and > intent -> 'attention'
else                    -> 'unclassified'
```

## Integration Points

Scoring hooks into `SignalAggregationService._create_signal_clusters()` at two points:
1. After `SignalCluster.objects.create()` — new clusters scored immediately
2. After `existing.save()` — updated clusters re-scored

Both wrapped in try/except so scoring failures don't break aggregation.

## Backfill Results (Railway)

```
Scored 1,573 clusters

Track distribution:
  attention:    604 (38%)
  intent:       169 (11%)
  unclassified: 800 (51%)
```

The 51% unclassified is expected — those are clusters where neither reach nor intent scored above the 0.4 threshold (weaker signals that don't clearly fit either track).

## What This Does NOT Include (Intentionally Deferred)

- **Auto-experiment generator** (Step 4 of maturity roadmap)
- **Track-based routing** — consuming the `track` field to route signals differently is a separate PR
- **UI changes** — no frontend changes
- **LLM-based scoring** — intentionally rule-based for cost and speed

## Verification

```bash
# Check track distribution
railway run python manage.py shell -c "
from core.models import SignalCluster
for track in ['attention', 'intent', 'unclassified']:
    print(f'{track}: {SignalCluster.objects.filter(track=track).count()}')
"

# Check new clusters get scored automatically (after next aggregation cycle)
railway run python manage.py shell -c "
from core.models import SignalCluster
from django.utils import timezone
from datetime import timedelta
recent = SignalCluster.objects.filter(detected_at__gte=timezone.now()-timedelta(hours=1))
for c in recent:
    print(f'track={c.track} reach={c.reach_score:.2f} intent={c.intent_score:.2f} {c.name[:50]}')
"
```
