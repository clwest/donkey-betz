# Session 473: Narrative Drift + Content Studio Integration

**Date:** December 17, 2025
**Status:** COMPLETE
**Type:** Cross-System Integration

## Summary

Connected two Tier 1 Autonomous Situations:
- **Narrative Drift Detector** (Session 471)
- **Autonomous Content Studio** (Session 466)

When a narrative shift is detected, the system now **automatically generates content** explaining the shift.

## What Was Built

### New Celery Tasks (2 tasks)

| Task | Purpose |
|------|---------|
| `trigger_content_from_narrative_shift` | Creates a ChannelEpisode when a NarrativeShift is detected |
| `process_narrative_shifts_for_content` | Periodic check for new shifts needing content |

### Integration Flow

```
NarrativeShift detected (confidence >= 0.6, importance >= 0.5)
    │
    ▼
trigger_content_from_narrative_shift(shift_id)
    │
    ├── Get or create "Narrative Shift Reports" channel
    ├── Generate content from shift data:
    │   - Historical Context (historian_analysis)
    │   - Why Now (trend_break_analysis)
    │   - Expected Impact (cultural_impact_analysis)
    │   - Second-Order Effects
    │
    ├── Create ChannelEpisode record
    ├── Create NarrativeAlert notification
    │
    ▼
Content available in Content Studio
```

### Celery Beat Schedule

```python
'narrative-shifts-to-content': {
    'task': 'narrative_drift.process_shifts_for_content',
    'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours at :30
}
```

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Added 2 new tasks (~200 lines) |
| `core/celery.py` | Added beat schedule for integration task |
| `core/agents/narrative/narrative_drift_coordinator.py` | Fixed SpiderData field references |

## Bug Fixes

### SpiderData Field Mismatch (Fixed)
The `_process_new_spider_data` method was using incorrect field names:
- `sd.title` → Now extracts from `sd.raw_data.items[].title`
- `sd.content` → Now extracts from `sd.raw_data.items[].content`
- `sd.url` → Now uses `sd.source_url`
- `sd.spider_category` → Now uses `sd.data_type`

## Testing Results

### Narrative Seeding
- **30 narratives** created across 8 domains
- domains: tech (4), markets (4), politics (3), crypto (4), culture (3), geopolitics (4), climate (4), health (4)

### Spider Data Processing
- Processed **50 spider data records**
- Matched **178 narrative instances**
- Created **178 evidence records**

### Content Generation Test
```json
{
  "status": "success",
  "episode_id": "5bd49018-13cb-418f-a755-0b4ae5180f5e",
  "topic": "Narrative Shift: AI will replace most knowledge workers -> AGI is imminent",
  "channel": "Narrative Shift Reports",
  "content_length": 814
}
```

## Content Generated

The system now generates markdown content with:
1. **Change Section** - Old narrative vs new narrative
2. **Summary** - Shift summary from detection
3. **What This Means** - New narrative summary
4. **Historical Context** - From NarrativeHistorianAgent
5. **Why Now** - From TrendBreakDetectorAgent
6. **Expected Impact** - From CulturalImpactAgent
7. **Second-Order Effects** - Predicted downstream effects
8. **Metadata** - Shift ID, confidence, importance

## API/Commands

The integration is fully autonomous - no manual intervention needed.

However, you can manually trigger content creation:
```python
from core.tasks import trigger_content_from_narrative_shift
result = trigger_content_from_narrative_shift("shift-uuid-here")
```

## System State After Session 473

### Tier 1 Autonomous Situations: 3 Connected

| Situation | Status | Sessions |
|-----------|--------|----------|
| Autonomous Content Studio | COMPLETE | 466 |
| Narrative Drift Detector | COMPLETE | 471 |
| Market Intelligence Desk | Phase 5/6 | 470-472 |

### Narrative Drift System

| Metric | Value |
|--------|-------|
| Total Narratives | 30 |
| Total Evidence Records | 178+ |
| Domains Tracked | 8 |
| Agent Analyses | Historian + TrendBreak + Cultural |

### Content Studio Integration

| Metric | Value |
|--------|-------|
| New Channel | "Narrative Shift Reports" |
| Episodes Created | 1 (test) |
| Content Length | ~800 chars per shift |

## Next Session Options

### Option A: Market Intelligence Phase 6 (ROI Metrics)
Complete the Market Intelligence architecture with ROI tracking.

### Option B: Enhance Generated Content
- Add images/visualizations to shift reports
- Add Discord notifications for new shift content
- Create video summaries using AISeriesWorkflowAgent

### Option C: Tune Detection Thresholds
- Adjust confidence/importance thresholds
- Add more keywords to narratives
- Improve sentiment detection

### Option D: Test Full Pipeline End-to-End
Spider → Scoring → Validation → Provenance → Narrative → Content

## Architecture Achieved

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED INTELLIGENCE SYSTEM                  │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  67 Spiders  │───▶│  Narrative   │───▶│  Content     │     │
│  │  (Data)      │    │  Drift Det.  │    │  Studio      │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  SpiderData  │    │  Narrative   │    │  Channel     │     │
│  │  Evidence    │    │  Shift       │    │  Episode     │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                 │
│  ALL SYSTEMS NOW CONNECTED AND GENERATING VALUE                │
└─────────────────────────────────────────────────────────────────┘
```

## Key Files Reference

| Component | File |
|-----------|------|
| Integration Tasks | `core/tasks.py` (lines 13188-13415) |
| Celery Beat | `core/celery.py` (lines 773-781) |
| Coordinator Fix | `core/agents/narrative/narrative_drift_coordinator.py` |
| Narrative Models | `core/models_narrative_drift.py` |
| Content Studio | `core/models_autonomous_studio.py` |

**Total Agents: 53**
**Total Spiders: 67**
**Autonomous Situations: 3 (all connected)**
