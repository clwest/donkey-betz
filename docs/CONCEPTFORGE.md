# ConceptForge: Autonomous Think Tank Pipeline

**Session 863** | January 28, 2026

## Overview

ConceptForge transforms published content into comprehensive dossiers through a 6-stage analysis pipeline powered by 139 persona agents and 25 legendary advisors.

```
Content → Intelligence → Strategy → Product

SelfBlog (published)
    ↓ [quality_score >= 0.80 + strategic_tag]
ConceptForgePipeline
    ↓ [domain router]
DomainLab (Legal | Market | Tech | Content | Startup | Career)
    ↓
6 Stages with Persona & Legendary Advisor Input
    ↓
Dossier (versioned, multi-format)
```

## Architecture Principles

### Config-First, Not Database-First

Labs and panels are defined in code for flexibility:
- `core/conceptforge/labs.py` - Domain lab definitions
- `core/conceptforge/panels.py` - Advisor pool configurations

Database stores only **run outputs**:
- `ConceptForgeRun` - Pipeline execution record
- `ConceptForgeStageRun` - Individual stage results
- `ConceptForgeArtifact` - Produced documents

### Advisor Panel Snapshots

When a run starts, the advisor panel is **snapshotted** into `advisor_panel_snapshot` JSON field:
- Guarantees reproducibility
- Enables "same content, different panel" comparisons
- Full audit trail

### Legendary Advisors as Constraints

Legendary advisors (Warren Buffett, Elon Musk, etc.) provide:
- Debate positions (pro/con)
- Risk framing
- Business lens
- Framework constraints

Core agents do the **actual writing**:
- ResearchAgent
- SystemsArchitectAgent
- RiskAnalysisAgent
- MarketIntelligenceAgent
- ThinkingAgent

## Pipeline Stages

| Stage | Agent | Purpose |
|-------|-------|---------|
| **Research** | ResearchAgent | Spider-enriched research, trend analysis |
| **Debate** | ContentStudioDebateAgent | Pro/con debate with legendary advisors |
| **Feasibility** | SystemsArchitectAgent | Technical architecture assessment |
| **Risk** | RiskAnalysisAgent | Legal, compliance, ethics analysis |
| **Market** | MarketIntelligenceAgent | Business opportunity sizing |
| **Synthesis** | ThinkingAgent | Executive dossier with recommendation |

## Domain Labs

### LegalLab ⚖️
- **Tags**: legal, legal-tech, policy, regulation, compliance
- **Required Advisors**: Warren Buffett, Peter Thiel
- **Debate Pair**: Warren Buffett vs George Soros

### MarketLab 📈
- **Tags**: market, stocks, trading, investment, finance
- **Required Advisors**: Warren Buffett, Ray Dalio
- **Debate Pair**: Cathie Wood vs Warren Buffett (Growth vs Value)

### TechLab 🔧
- **Tags**: tech, ai, ml, product, software, saas
- **Required Advisors**: Elon Musk, Peter Thiel
- **Debate Pair**: Elon Musk vs Yuval Harari (Optimist vs Cautionary)

### ContentLab 📝
- **Tags**: content, marketing, media, social, blog
- **Required Advisors**: Gary Vaynerchuk, Seth Godin
- **Debate Pair**: Gary Vaynerchuk vs Seth Godin (Volume vs Quality)

### StartupLab 🚀
- **Tags**: startup, funding, venture, scale, growth
- **Required Advisors**: Mark Cuban, Reid Hoffman
- **Debate Pair**: Richard Branson vs Peter Thiel

### CareerLab 💼
- **Tags**: career, jobs, skills, resume, interview
- **Required Advisors**: Tim Ferriss, Simon Sinek
- **Debate Pair**: Tim Ferriss vs Gary Vaynerchuk (Lifestyle vs Hustle)

## Gate Logic

ConceptForge only triggers when:

```python
quality_score >= 0.80
AND has_strategic_tag(tags)
AND domain_lab_exists(tags)
```

Quality score factors:
- Word count (500+ words)
- Structured sections (3+)
- Tags (2+)
- Meta description
- Intro and conclusion

Manual override available via "Promote to ConceptForge" action.

## Usage

### Automatic Trigger (Signal)

When a `SelfBlog` is saved with `status='published'`:

```python
# Automatic via Django signal
# See core/signals.py handle_selfblog_save()
```

### Manual Trigger (Celery)

```python
from core.tasks import promote_to_conceptforge

promote_to_conceptforge.delay(
    source_type='blog',
    source_id=str(blog.id),
    domain='legal',  # Optional - auto-detects if not specified
    user_id=request.user.id,
)
```

### Direct Orchestration

```python
from core.conceptforge import ConceptForgeOrchestrator

orchestrator = ConceptForgeOrchestrator(user=request.user)

# Check if content qualifies
should_trigger, reason, domain = orchestrator.should_trigger(
    quality_score=0.85,
    tags=['legal', 'automation', 'tech'],
)

if should_trigger:
    run = orchestrator.start_pipeline(
        source_type='blog',
        source_id=str(blog.id),
        source_title=blog.title,
        domain=domain,
        quality_score=0.85,
    )

    # Execute (usually done async via Celery)
    orchestrator.execute_run(run)
```

## Database Models

### ConceptForgeRun

```python
ConceptForgeRun:
    - source_type: blog | decision_summary | research_brief | audit | manual
    - source_id: UUID
    - source_title: str
    - domain: str (legal, market, tech, etc.)
    - advisor_panel_snapshot: JSON (frozen at run start)
    - status: pending | running | completed | failed | cancelled
    - current_stage: str
    - quality_score: float
    - triggered_by: signal | manual | celery_beat
    - duration_ms: int
```

### ConceptForgeStageRun

```python
ConceptForgeStageRun:
    - run: FK to ConceptForgeRun
    - stage_name: research | debate | feasibility | risk | market | synthesis
    - stage_order: 1-6
    - agent_used: str
    - advisors_used: JSON list
    - legendary_advisors_used: JSON list
    - inputs_snapshot: JSON (for debugging)
    - output_text: str
    - output_metadata: JSON
    - status: pending | running | completed | failed | skipped
    - duration_ms: int
```

### ConceptForgeArtifact

```python
ConceptForgeArtifact:
    - run: FK to ConceptForgeRun
    - stage: FK to ConceptForgeStageRun (optional)
    - name: str
    - kind: md | pdf | json | html
    - content: str
    - file_path: str (if stored in workspace)
    - version: int
    - is_primary: bool (true for final dossier)
```

## Celery Tasks

```python
# Main pipeline execution
run_conceptforge_pipeline.delay(
    source_type='blog',
    source_id=str(id),
    source_title='Title',
    domain='legal',
    quality_score=0.85,
    triggered_by='signal',
    user_id=1,
)

# Manual promotion
promote_to_conceptforge.delay(
    source_type='blog',
    source_id=str(id),
    domain=None,  # Auto-detect
    user_id=1,
)

# Single stage execution (for retries)
run_conceptforge_stage.delay(
    run_id=str(run.id),
    stage_name='research',
)
```

## Output: Dossier Card UI

The dossier displays in the same card pattern as existing initiative phases:

```
╔═══════════════════════════════════════════════════════════════════╗
║ Dossier: Automated Order Enforcement (LegalLab)                   ║
╠═══════════════════════════════════════════════════════════════════╣
║ Tabs:                                                             ║
║   [Research] [Debate] [Feasibility] [Risk] [Market] [Synthesis]   ║
╠═══════════════════════════════════════════════════════════════════╣
║ Research                                                          ║
║ ─────────────────────────────────────────────────────────────     ║
║ Key findings from spider data and trend analysis...               ║
║                                                                   ║
║ Advisor Input:                                                    ║
║ • Legal Document Reviewer: Focus on enforcement gaps...           ║
║ • Trend Analysis Expert: Growing interest in legaltech...         ║
╚═══════════════════════════════════════════════════════════════════╝
```

## Publishing Flow

After dossier completion:

1. **Blog** (public) - Already published
2. **Dossier** (internal) - For investors/partners/dev team
3. **Synthesis outputs**:
   - Pitch deck content
   - Roadmap bullet points
   - Prototype plan
   - Funding memo

## Files Reference

| File | Purpose |
|------|---------|
| `core/conceptforge/__init__.py` | Package exports |
| `core/conceptforge/labs.py` | Domain lab configurations |
| `core/conceptforge/panels.py` | Advisor panel configurations |
| `core/conceptforge/orchestrator.py` | Pipeline orchestration |
| `core/models_conceptforge.py` | Database models |
| `core/signals/conceptforge_signals.py` | Django signals (SelfBlog trigger) |
| `core/tasks.py` | Celery tasks (last section) |

## Adding a New Domain Lab

1. Add lab config to `labs.py`:

```python
'healthcare': LabConfig(
    name='HealthcareLab',
    description='Healthcare technology and policy analysis',
    icon='🏥',
    routing_tags=['health', 'healthcare', 'medical', 'biotech'],
    stages={
        'research': StageConfig(
            agent_name='ResearchAgent',
            persona_advisors=['Healthcare Analyst', 'Regulatory Compliance'],
        ),
        # ... other stages
    },
),
```

2. Add panel config to `panels.py`:

```python
'healthcare': PanelPool(
    required=['christine_lagarde', 'yuval_harari'],
    optional=['elon_musk', 'jeff_bezos'],
    debate_pairs=[
        ('elon_musk', 'yuval_harari'),
    ],
),
```

No migrations needed - labs are config-first!

## Monitoring

Check pipeline status:

```python
from core.models_conceptforge import ConceptForgeRun

# Recent runs
runs = ConceptForgeRun.objects.order_by('-created_at')[:10]

# Failed runs
failed = ConceptForgeRun.objects.filter(status='failed')

# Run progress
run = ConceptForgeRun.objects.get(id=run_id)
print(run.progress_percentage)  # 0-100
print(run.stage_summary)  # Dict of stage statuses
```

## Next Steps

1. **UI Integration**: Add ConceptForge tab to Workspace
2. **API Endpoints**: Create REST endpoints for run management
3. **Notification**: Discord alerts on dossier completion
4. **Analytics**: Track which domains generate most value
5. **Learning Loop**: Feed dossier outcomes back to improve pipeline
