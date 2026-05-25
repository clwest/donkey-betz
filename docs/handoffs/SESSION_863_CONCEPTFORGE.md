---
originating_session: 863
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 863: ConceptForge - Autonomous Think Tank Pipeline

**Date:** January 28, 2026
**Focus:** Content → Intelligence → Strategy → Product Pipeline

## Summary

Implemented ConceptForge, an autonomous think tank pipeline that transforms published content into comprehensive dossiers through 6-stage analysis powered by 139 persona agents and 25 legendary advisors.

## What Was Built

### 1. Core Architecture (`core/conceptforge/`)

**Config-first approach** - Labs and panels defined in code, not database:

- `labs.py` - 6 domain lab configurations (Legal, Market, Tech, Content, Startup, Career)
- `panels.py` - 18 legendary advisor profiles with debate pairs
- `orchestrator.py` - Pipeline execution engine

### 2. Database Models (`core/models_conceptforge.py`)

Simplified run tracking:

- `ConceptForgeRun` - Pipeline execution record with advisor_panel_snapshot
- `ConceptForgeStageRun` - Individual stage results with inputs/outputs
- `ConceptForgeArtifact` - Produced documents (dossiers)

### 3. Django Signals (`core/signals.py`)

Gate-controlled triggers:

- `handle_selfblog_save` - Triggers pipeline on publish
- Quality gate: `quality_score >= 0.80 + strategic_tag`
- Prevents "dossier spam" by filtering low-quality content

### 4. Celery Tasks (`core/tasks.py`)

Async pipeline execution:

- `run_conceptforge_pipeline` - Main pipeline task
- `promote_to_conceptforge` - Manual promotion
- `run_conceptforge_stage` - Single stage execution (for retries)

### 5. Documentation

- `docs/CONCEPTFORGE.md` - Full architecture and usage guide
- `docs/ARCHITECTURE.md` - Updated with ConceptForge section

## Design Decisions

Based on ChatGPT feedback, implemented these key patterns:

1. **Config-first, not database-first** - Labs defined in Python, not DB tables
2. **Advisor panel snapshots** - Frozen per run for reproducibility
3. **Legendary advisors as constraints** - They provide frameworks, agents do writing
4. **Rule-based selection first** - Domain → panel pools, not "smart" matching
5. **Gate triggers** - Quality + strategic tags, not every blog

## Pipeline Stages

| Stage | Agent | Persona Advisors | Purpose |
|-------|-------|------------------|---------|
| Research | ResearchAgent | Domain-specific | Spider-enriched research |
| Debate | ContentStudioDebateAgent | Legendary pair | Pro/con positions |
| Feasibility | SystemsArchitectAgent | Tech personas | Architecture assessment |
| Risk | RiskAnalysisAgent | Legal/compliance | Risk analysis |
| Market | MarketIntelligenceAgent | Business personas | Opportunity sizing |
| Synthesis | ThinkingAgent | - | Executive dossier |

## Domain Labs

- **LegalLab** ⚖️ - Warren Buffett + Peter Thiel
- **MarketLab** 📈 - Warren Buffett + Ray Dalio (Cathie Wood vs Warren debate)
- **TechLab** 🔧 - Elon Musk + Peter Thiel
- **ContentLab** 📝 - Gary Vaynerchuk + Seth Godin
- **StartupLab** 🚀 - Mark Cuban + Reid Hoffman
- **CareerLab** 💼 - Tim Ferriss + Simon Sinek

## Files Changed

```
NEW:
- core/conceptforge/__init__.py
- core/conceptforge/labs.py
- core/conceptforge/panels.py
- core/conceptforge/orchestrator.py
- core/models_conceptforge.py
- core/signals/conceptforge_signals.py (in existing signals package)
- docs/CONCEPTFORGE.md
- docs/handoffs/SESSION_863_CONCEPTFORGE.md
- core/migrations/0205_conceptforge_pipeline.py

MODIFIED:
- core/apps.py (added signal registration)
- core/models/__init__.py (added ConceptForge model imports)
- core/tasks.py (added ConceptForge Celery tasks)
- core/signals/__init__.py (added ConceptForge signal exports)
- docs/ARCHITECTURE.md (added ConceptForge section)
- frontend/src/pages/workspace/tabs/IntelligenceTab.tsx (fixed API URL)
- frontend/src/pages/workspace/tabs/OperationsTab.tsx (fixed data extraction)
```

## Deployment Fixes

### Fix 1: Signals Package Conflict
Initial deployment failed due to signals file conflict:
- Created `core/signals.py` but `core/signals/` package already existed
- Fixed by moving signals to `core/signals/conceptforge_signals.py`

### Fix 2: Frontend API Errors (PR #462)
Fixed console errors in Operations and Intelligence tabs:
- **IntelligenceTab.tsx**: Wrong API URL `/api/v1/consciousness/thoughts/` → `/api/v1/reasoning/thoughts/`
- **OperationsTab.tsx**: Data extraction looking for wrong key `data.results` → `data.operations`
- Added error handling to prevent crashes when API calls fail

## Testing

To test manually:

```python
from core.conceptforge import ConceptForgeOrchestrator

orchestrator = ConceptForgeOrchestrator()

# Check if content qualifies
should_trigger, reason, domain = orchestrator.should_trigger(
    quality_score=0.85,
    tags=['legal', 'automation'],
)
print(f"Should trigger: {should_trigger}, Reason: {reason}, Domain: {domain}")

# Manual trigger via Celery
from core.tasks import promote_to_conceptforge
promote_to_conceptforge.delay(
    source_type='blog',
    source_id='<blog-uuid>',
    domain='legal',
)
```

## Next Steps

1. **UI Integration** - Add ConceptForge tab to Workspace (match initiative phase cards)
2. **API Endpoints** - REST endpoints for run management
3. **Discord Notifications** - Alert on dossier completion
4. **Analytics Dashboard** - Track which domains generate most value
5. **Learning Loop** - Feed dossier outcomes back to improve agents

## Quality Metrics

- 139 persona agents integrated
- 25 legendary advisors with debate pairs
- 6 domain labs configured
- 6 pipeline stages
- Gate: quality_score >= 0.80
- Full audit trail via snapshots

## Session Stats

- Models created: 3
- Services created: 1
- Celery tasks added: 3
- Documentation pages: 2
- Migration: 0205_conceptforge_pipeline
